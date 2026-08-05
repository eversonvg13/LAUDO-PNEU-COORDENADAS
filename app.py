import os
import base64
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image

# Importações dos nossos módulos locais
from parser import parse_relatorio_html, CAMPOS_FIXOS
from ai_helper import (
    comprimir_imagem,
    obter_modelo_estavel,
    buscar_dados_relatorio,
    extrair_json_da_resposta,
)
from pdf_generator import gerar_pdf_laudo_pneu, gerar_pdf_fallback

# Função auxiliar para converter imagem em base64 (centralização perfeita via HTML)
def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        except Exception:
            return None
    return None

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
favicon = "🧭"
if os.path.exists("ssasdsds.png"):
    try:
        favicon = Image.open("ssasdsds.png")
    except Exception:
        favicon = "🧭"

st.set_page_config(
    page_title="LAUDO PNEUS COORDENADAS",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# ESTILIZAÇÃO CSS (TEMA ESCURO + LAYOUT DOS CARDS)
# ==============================================================================
st.markdown("""
    <style>
    /* Ocultar Barra Lateral e Controle de Expandir/Recolher */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Fundo Escuro da Aplicação */
    .stApp, .main {
        background-color: #0d1117;
        color: #ffffff;
    }

    /* Remove padding superior padrão do Streamlit para o cabeçalho ficar alinhado */
    .block-container {
        padding-top: 2rem !important;
    }

    /* Customização dos contêineres (Cards) para o tema escuro */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border-radius: 10px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* Estilo da área de arrastar e soltar (Uploader) */
    [data-testid="stFileUploadDropzone"] {
        background-color: #0d1117;
        border: 1px dashed #4b5563;
        border-radius: 8px;
    }

    /* Estilização do Botão Principal (Rosa/Vermelho claro do print) */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
        font-size: 16px;
        background-color: #f07b82;
        color: white;
        border: none;
        padding: 10px;
    }
    div.stButton > button:first-child:hover {
        background-color: #dc2626;
        color: white;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Obtenção da chave de API em segundo plano (via Variável de Ambiente ou Secrets)
api_key = os.environ.get("GEMINI_API_KEY", "") or st.secrets.get("GEMINI_API_KEY", "")

# ==============================================================================
# CABEÇALHO CENTRALIZADO COM LOGO MAIOR
# ==============================================================================
logo_b64 = get_image_base64("ssasdsds.png") or get_image_base64("logo-nobg.png")

if logo_b64:
    logo_img_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 180px; object-fit: contain; margin-right: 20px;">'
else:
    logo_img_html = '<span style="font-size: 70px; margin-right: 20px;">🧭</span>'

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; width: 100%; margin-top: 10px; margin-bottom: 10px;">
        {logo_img_html}
        <h1 style="margin: 0; font-weight: 900; font-size: 36px; color: #ffffff; text-align: center;">LAUDO PNEUS COORDENADAS</h1>
    </div>
""", unsafe_allow_html=True)

# Linha vermelha forte dividindo o cabeçalho
st.markdown('<hr style="border: none; height: 3px; background-color: #dc2626; margin-top: 15px; margin-bottom: 10px;">', unsafe_allow_html=True)

# Texto de Fluxo Centralizado
st.markdown("<p style='text-align: center; color: #a1a1aa; font-size: 16px; margin-bottom: 40px;'>Fluxo: <b>1)</b> Envie o relatório e as fotos &nbsp;➔&nbsp; <b>2)</b> Gere o laudo em PDF</p>", unsafe_allow_html=True)

# ==============================================================================
# SEÇÃO 1: RELATÓRIO E FOTOS (TÍTULO E CARDS)
# ==============================================================================
st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 15px;'>
        <div style='background-color: #025ca3; color: white; font-weight: bold; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 4px;'>1</div>
        <h3 style='margin: 0; padding: 0; font-size: 24px; color: #ffffff;'>Relatório e Fotos</h3>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# --- CARD 1: RELATÓRIO HTML ---
with col1:
    with st.container(border=True):
        st.markdown("<h4 style='color: #ffffff; margin-top: 0;'><span style='font-size: 18px;'>📄</span> Relatório HTML</h4>", unsafe_allow_html=True)
        st.caption("Envie o relatório exportado em HTML (Relatório de Troca de Pneus - Modelo 4)")
        
        relatorio_file = st.file_uploader(
            "Selecionar arquivo",
            type=["html", "htm"],
            accept_multiple_files=False,
            key="uploader_html",
            label_visibility="collapsed"
        )

        if relatorio_file is not None:
            if st.session_state.get("relatorio_nome_processado") != relatorio_file.name:
                with st.spinner("Extraindo dados..."):
                    try:
                        df_relatorio = parse_relatorio_html(relatorio_file.getvalue())
                        st.session_state.dados_relatorio = df_relatorio
                        st.session_state.relatorio_nome_processado = relatorio_file.name
                    except Exception as e:
                        st.error(f"Erro: {e}")

# --- CARD 2: FOTOS DOS PNEUS ---
with col2:
    with st.container(border=True):
        st.markdown("<h4 style='color: #ffffff; margin-top: 0;'><span style='font-size: 18px;'>🖼️</span> Fotos dos Pneus</h4>", unsafe_allow_html=True)
        st.caption("Envie o lote completo de fotos dos pneus (JPG, PNG)")
        
        uploaded_files = st.file_uploader(
            "Selecionar arquivos",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="uploader_fotos",
            label_visibility="collapsed"
        )
        
        modo_analise = st.selectbox(
            "Modo de Análise IA:",
            [
                "Inspeção Completa (ID Fogo + Sulco + Danos)",
                "Apenas Extrair Número de 'Fogo' (ID do Pneu)",
                "Análise Profunda de Danos e Desgaste de Banda"
            ]
        )

# ==============================================================================
# VISUALIZAÇÃO DOS DADOS DO RELATÓRIO (EXPANDER OPCIONAL)
# ==============================================================================
if "dados_relatorio" not in st.session_state:
    st.session_state.dados_relatorio = pd.DataFrame(columns=CAMPOS_FIXOS)

if not st.session_state.dados_relatorio.empty:
    with st.expander(f"✅ {len(st.session_state.dados_relatorio)} pneus extraídos do relatório. Clique para ver/editar."):
        st.session_state.dados_relatorio = st.data_editor(
            st.session_state.dados_relatorio,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_dados_relatorio",
        )

# ==============================================================================
# SEÇÃO DO BOTÃO PRINCIPAL (CARD INFERIOR)
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    if st.button("📤 Gerar Laudo", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("⚠️ Por favor, envie as fotos dos pneus antes de gerar o laudo.")
        elif not api_key:
            st.error("⚠️ Chave de API do Gemini não configurada no servidor (GEMINI_API_KEY).")
        else:
            if "inspection_results" not in st.session_state:
                st.session_state.inspection_results = []

            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)

                texto_status = st.empty()
                texto_status.info("Selecionando modelo estável...")

                nome_modelo_ativo = obter_modelo_estavel(genai)
                texto_status.info(f"Conectado ao modelo: {nome_modelo_ativo}. Comprimindo lote de fotos...")

                model = genai.GenerativeModel(nome_modelo_ativo)
                sorted_files = sorted(uploaded_files, key=lambda f: f.name)

                prompt_instrucoes = f"""
                Você é um inspetor especialista em inventário de pneus de frota (SMART-LOG).
                Abaixo estão {len(sorted_files)} fotos ordenadas cronologicamente.

                Sua tarefa:
                1. Analise todas as imagens e agrupe-as por pneu individual. Cada novo pneu começa com a
                   foto da lateral contendo o número de 'Fogo' (identificação pintada em giz/tinta, ex: 32813),
                   seguida das fotos de banda de rodagem/sulco/danos daquele pneu até a próxima foto de 'Fogo'.
                2. Para cada pneu, leia o número de Fogo exatamente como aparece na foto.
                3. Modo de análise solicitado: {modo_analise}.

                Responda SOMENTE com um array JSON válido (nada de texto antes ou depois, nada de markdown),
                no seguinte formato exato, um objeto por pneu:

                [
                  {{
                    "fogo": "string (número lido na foto)",
                    "marca": "string (observado na foto)",
                    "sulco": "string (observado na foto)",
                    "danos": "string (observado na foto)",
                    "acao_recomendada": "string",
                    "confianca": "Alta | Média | Baixa"
                  }}
                ]

                NÃO invente dados de placa, posição, quilometragem ou datas.
                """

                conteudo_requisicao = []
                for f in sorted_files:
                    bytes_comprimidos = comprimir_imagem(f.getvalue())
                    conteudo_requisicao.append(f"Arquivo: {f.name}")
                    conteudo_requisicao.append({"mime_type": "image/jpeg", "data": bytes_comprimidos})
                conteudo_requisicao.append(prompt_instrucoes)

                texto_status.info(f"Enviando dados para a IA ({nome_modelo_ativo})... aguarde, isso pode levar alguns minutos.")
                resposta_ia = model.generate_content(conteudo_requisicao)

                pneus_estruturados = None
                erro_parse = None
                try:
                    pneus_ia = extrair_json_da_resposta(resposta_ia.text)
                    tabela_df = st.session_state.dados_relatorio
                    pneus_estruturados = []
                    for item in pneus_ia:
                        fogo_lido = str(item.get("fogo", "")).strip()
                        dados_tabela = buscar_dados_relatorio(fogo_lido, tabela_df)

                        pneu = {
                            "fogo": fogo_lido,
                            "pos": dados_tabela.get("POS", "") if dados_tabela else "",
                            "veiculo": dados_tabela.get("VEICULO", "") if dados_tabela else "",
                            "medida": dados_tabela.get("MEDIDA", "") if dados_tabela else "",
                            "retirada": dados_tabela.get("RETIRADA", "") if dados_tabela else "",
                            "local": dados_tabela.get("LOCAL", "") if dados_tabela else "",
                            "km_pos": dados_tabela.get("KM/POS", "") if dados_tabela else "",
                            "km_total": dados_tabela.get("KM TOTAL", "") if dados_tabela else "",
                            "marca": item.get("marca", ""),
                            "sulco": item.get("sulco", ""),
                            "danos": item.get("danos", ""),
                            "acao_recomendada": item.get("acao_recomendada", ""),
                            "confianca": item.get("confianca", ""),
                            "fogo_localizado_na_planilha": dados_tabela is not None,
                        }
                        pneus_estruturados.append(pneu)
                except Exception as e:
                    erro_parse = str(e)

                st.session_state.inspection_results = [{
                    "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "Modelo_Usado": nome_modelo_ativo,
                    "Analise_IA_Bruta": resposta_ia.text,
                    "Pneus": pneus_estruturados,
                    "Erro_Parse": erro_parse,
                    "Imagens": sorted_files
                }]

                texto_status.success(f"✅ Inspeção concluída com sucesso via {nome_modelo_ativo}!")

            except Exception as e:
                st.error(f"Erro no processamento: {str(e)}")

# Importe a função individual no topo do arquivo
from pdf_generator import gerar_pdf_laudo_pneu, gerar_pdf_fallback

# ==============================================================================
# EXIBIÇÃO DOS RESULTADOS (LAUDO CONSOLIDADO)
# ==============================================================================
if st.session_state.get("inspection_results"):
    st.markdown("---")
    
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 15px;'>
            <div style='background-color: #025ca3; color: white; font-weight: bold; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 4px;'>2</div>
            <h3 style='margin: 0; padding: 0; font-size: 24px; color: #ffffff;'>Laudos dos Pneus</h3>
        </div>
    """, unsafe_allow_html=True)

    for res in st.session_state.inspection_results:
        with st.expander(f"🛞 Lote Processado ({len(res['Imagens'])} fotos)", expanded=True):
            st.markdown("##### Miniaturas Enviadas:")
            cols = st.columns(min(len(res["Imagens"]), 6))
            for idx, img_file in enumerate(res["Imagens"]):
                with cols[idx % 6]:
                    st.image(img_file, caption=img_file.name, use_container_width=True)

            st.markdown("---")

            if res["Pneus"]:
                for i, pneu in enumerate(res["Pneus"], start=1):
                    fogo_num = pneu.get('fogo', f'N/A_{i}')
                    titulo = f"PNEU {i} — FOGO {fogo_num}"
                    if pneu.get("fogo_localizado_na_planilha") is False:
                        titulo += " ⚠️ (não encontrado na planilha)"

                    with st.container(border=True):
                        st.markdown(f"### 🛞 {titulo}")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"**POS:** {pneu.get('pos', '')}")
                            st.write(f"**VEÍCULO:** {pneu.get('veiculo', '')}")
                            st.write(f"**MEDIDA:** {pneu.get('medida', '')}")
                            st.write(f"**RETIRADA:** {pneu.get('retirada', '')}")
                        with c2:
                            st.write(f"**LOCAL/UNIDADE:** {pneu.get('local', '')}")
                            st.write(f"**KM POS:** {pneu.get('km_pos', '')}")
                            st.write(f"**KM TOTAL:** {pneu.get('km_total', '')}")
                            st.write(f"**Confiança IA:** {pneu.get('confianca', '')}")

                        st.write(f"**Laudo / Dano Relatado:** {pneu.get('danos', '')}")
                        st.write(f"**Ação Recomendada:** {pneu.get('acao_recomendada', '')}")

                        # Botão de download INDIVIDUAL para cada pneu
                        pdf_pneu_bytes = gerar_pdf_laudo_pneu(pneu, res["Timestamp"].split()[0])
                        st.download_button(
                            label=f"📄 Baixar PDF - Pneu {fogo_num}",
                            data=pdf_pneu_bytes,
                            file_name=f"laudo_pneu_{fogo_num}.pdf",
                            mime="application/pdf",
                            key=f"btn_pdf_pneu_{fogo_num}_{i}"
                        )
            else:
                st.warning("⚠️ Não foi possível estruturar o JSON da IA. Baixe o relatório em texto abaixo.")
                st.text_area("Resposta bruta da IA", res["Analise_IA_Bruta"], height=200)
                pdf_fallback = gerar_pdf_fallback(res["Analise_IA_Bruta"], res["Timestamp"])
                st.download_button(
                    label="📥 Baixar Laudo Texto Simples",
                    data=pdf_fallback,
                    file_name=f"laudo_bruto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                )
