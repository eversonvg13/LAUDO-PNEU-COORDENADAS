import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
import json
import io

# Configuração da página
st.set_page_config(
    page_title="SMART-LOG — Gestão de Pneus",
    page_icon="🛞",
    layout="wide"
)

# --- GERENCIAMENTO DE CHAVES API E ROTAÇÃO (Anti-429) ---
def get_api_keys():
    keys = []
    if "GEMINI_API_KEYS" in st.secrets:
        keys = st.secrets["GEMINI_API_KEYS"]
    elif "gemini_keys" in st.secrets:
        keys = st.secrets["gemini_keys"]
    else:
        for k, v in st.secrets.items():
            if "API_KEY" in k.upper():
                keys.append(v)
    if not keys and "GEMINI_API_KEY" in st.secrets:
        keys = [st.secrets["GEMINI_API_KEY"]]
    return keys

api_keys = get_api_keys()
if not api_keys:
    st.error("⚠️ Nenhuma chave de API do Gemini configurada nos Secrets do Streamlit.")
    st.stop()

if "current_key_index" not in st.session_state:
    st.session_state.current_key_index = 0

def configure_gemini():
    key = api_keys[st.session_state.current_key_index % len(api_keys)]
    genai.configure(api_key=key)

def rotate_key():
    st.session_state.current_key_index += 1
    configure_gemini()
    st.toast("🔄 Alternando chave de API devido a limite de cota (429)...", icon="⚠️")

configure_gemini()

# --- TÍTULO E CABEÇALHO ---
st.title("🛞 SMART-LOG — Sistema Inteligente de Laudo de Pneus")
st.markdown("---")

# --- UPLOAD DE ARQUIVOS ---
col_up1, col_up2 = st.columns(2)
with col_up1:
    relatorio_file = st.file_uploader("📁 Enviar Relatório (Excel / HTML)", type=["xlsx", "xls", "html", "htm"])
with col_up2:
    fotos_files = st.file_uploader("📸 Enviar Fotos dos Pneus", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Armazenamento em Session State
if "pneus_data" not in st.session_state:
    st.session_state.pneus_data = []

df = None
if relatorio_file is not None:
    try:
        if relatorio_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(relatorio_file)
        else:
            df = pd.read_html(relatorio_file)[0]
        
        st.success(f"✅ {len(df)} pneus extraídos do relatório com sucesso!")
        
        with st.expander("Visualizar dados brutos importados"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Erro ao processar o relatório: {e}")

# --- PROCESSAMENTO COM IA (GEMINI) ---
if fotos_files and st.button("🚀 Processar Inspeção com IA (Gemini)"):
    imagens_dict = {f.name: Image.open(f) for f in fotos_files}
    
    prompt_instrucoes = """
    Você é um inspetor técnico sênior especialista em frotas pesadas. 
    Sua tarefa CRUCIAL é identificar o número de FOGO do pneu.
    
    Instruções estritas para a leitura do Fogo:
    1. Procure atentamente por números escritos à mão com giz branco, amarelo ou tinta na lateral (borracha) do pneu. 
    2. O número de fogo costuma ser uma sequência numérica clara (ex: 9012, 276666, 30939, etc.). Não confunda com códigos de série de fabricação em alto-relevo (DOT).
    3. Agrupe as fotos que pertencem exatamente ao mesmo pneu na propriedade "arquivos_fotos".
    4. Identifique a marca, o estado do sulco e descreva o dano visual encontrado.

    Responda SOMENTE com um array JSON válido (um objeto por pneu detectado):
    [
      {
        "fogo": "apenas o número exato lido a giz",
        "marca": "string",
        "sulco": "string",
        "arquivos_fotos": ["nome_arquivo1.jpg", "nome_arquivo2.jpg"],
        "descricao_dano_ia": "string",
        "confianca": "Alta | Média | Baixa"
      }
    ]
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    success = False
    tentativas = 0
    response_text = ""
    
    while not success and tentativas < len(api_keys) + 1:
        try:
            content_parts = [prompt_instrucoes]
            for nome_img, img_obj in imagens_dict.items():
                content_parts.append(f"Arquivo: {nome_img}")
                content_parts.append(img_obj)
                
            response = model.generate_content(content_parts)
            response_text = response.text
            success = True
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                rotate_key()
                tentativas += 1
            else:
                st.error(f"Erro na chamada da IA: {e}")
                break

    if success:
        try:
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            resultado_ia = json.loads(clean_json)
            st.session_state.pneus_ia = resultado_ia
            st.success("✨ Inspeção por IA concluída com sucesso!")
        except Exception as ex:
            st.error(f"Erro ao decodificar a resposta JSON da IA: {ex}")
            st.text(response_text)

# --- EXIBIÇÃO E AJUSTE DOS LAUDOS ---
if "pneus_ia" in st.session_state and st.session_state.pneus_ia:
    st.markdown("### 📋 Laudos Gerados e Classificação FVU")
    
    for idx, pneu in enumerate(st.session_state.pneus_ia):
        fogo_atual = str(pneu.get("fogo", f"Desconhecido_{idx}")).strip()
        
        # Extração robusta da quantidade de reformas
        n_reformas = "0"
        if df is not None:
            match_row = None
            for col in df.columns:
                matches = df[df[col].astype(str).str.contains(fogo_atual, na=False)]
                if not matches.empty:
                    match_row = matches.iloc[0]
                    break
            
            if match_row is not None:
                chaves_reforma = ["Re", "RE", "re", "Reformas", "REFORMAS", "reformas", "R", "Nº Re", "Nº Reformas", "N_RE"]
                for chave in chaves_reforma:
                    if chave in match_row:
                        val = match_row[chave]
                        if val is not None and str(val).strip() and str(val).strip().lower() != "nan":
                            n_reformas = str(val).strip()
                            break
                if n_reformas == "0":
                    for k in match_row.index:
                        k_str = str(k).upper()
                        if "RE" in k_str or "REF" in k_str:
                            val = match_row[k]
                            if val is not None and str(val).strip() and str(val).strip().lower() != "nan":
                                n_reformas = str(val).strip()
                                break

        with st.expander(f"📦 PNEU {idx+1} — FOGO {fogo_atual} (Reformas: {n_reformas})"):
            st.markdown(f"**Classificação FVU (Ajustar se necessário - Pneu {fogo_atual})**")
            fvu_class = st.selectbox(
                "Classificação FVU", 
                [
                    "70J - Desenolamento do retorno da lona carcaça no talão.",
                    "10A - Desgaste irregular por desalinhamento.",
                    "20B - Penetração de objeto cortante na banda de rodagem.",
                    "30C - Bolha lateral por impacto em guias."
                ],
                key=f"fvu_{idx}"
            )
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Nº REFORMAS:** {n_reformas}")
                st.markdown(f"**Confiança IA:** {pneu.get('confianca', 'Alta')}")
                st.markdown(f"**Marca:** {pneu.get('marca', 'N/D')}")
            with col_info2:
                st.markdown(f"**Sulco:** {pneu.get('sulco', 'N/D')}")
                st.markdown(f"**Dano Detectado:** {pneu.get('descricao_dano_ia', 'N/D')}")
                
            st.markdown("---")
            if st.button(f"📄 Baixar PDF — Fogo {fogo_atual}", key=f"btn_pdf_{idx}"):
                st.info(f"Geração de PDF acionada para o pneu {fogo_atual}.")
