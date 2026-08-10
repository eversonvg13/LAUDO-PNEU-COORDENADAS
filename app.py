import os
import base64
import time
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image
import google.generativeai as genai
from data_utils import salvar_no_onedrive

# Importações dos módulos locais
from parser import parse_relatorio_html, CAMPOS_FIXOS
from ai_helper import (
    comprimir_imagem,
    obter_modelo_estavel,
    buscar_dados_relatorio,
    extrair_json_da_resposta,
    encontrar_fvu_por_descricao,
)
from pdf_generator import gerar_pdf_laudo_pneu, gerar_pdf_fallback

# NOVA IMPORTAÇÃO ATUALIZADA
from fvu_keywords import gerar_guia_prompt_fvu, gerar_prompt_sistema_ia

# Função para carregar a planilha FVU
@st.cache_data(show_spinner=False)
def carregar_tabela_fvu():
    """Lê a planilha local e extrai os padrões de laudo (aba FVU)."""
    try:
        df_fvu = pd.read_excel("Laudos de Pneus Romulo.xlsx", sheet_name="FVU")
        df_fvu = df_fvu.dropna(subset=['FVU'])
        
        lista_fvu = []
        for _, row in df_fvu.iterrows():
            lista_fvu.append({
                "codigo": str(row['FVU']).strip(),
                "categoria": "" if pd.isna(row.get('CATEGORIA')) else str(row['CATEGORIA']).strip(),
                "descricao": "" if pd.isna(row['DESCRIÇÃO']) else str(row['DESCRIÇÃO']).strip(),
                "causa": "" if pd.isna(row['CAUSA']) else str(row['CAUSA']).strip(),
                "acao": "" if pd.isna(row['AÇÃO']) else str(row['AÇÃO']).strip()
            })
        return lista_fvu
    except Exception as e:
        st.error(f"⚠️ Erro ao carregar a planilha: {e}")
        return []

#lista de unidade
unidades_disponiveis = [
    "ANA LUCIA",
    "JUSTINOPOLES",
    "LAFAIETE",
    "MARIA GORETTI",
    "NEVES",
    "SARZEDO",
    "UBERLANDIA",
    "VENEZA"
]

# Inicializa os dados FVU na sessão
if "fvu_data" not in st.session_state:
    st.session_state.fvu_data = carregar_tabela_fvu()

# Inicializa o gerenciamento de múltiplas chaves de API na sessão
if "lista_chaves" not in st.session_state:
    chaves = []
    # Captura a chave principal
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
        chaves.append(st.secrets["GEMINI_API_KEY"])
    
    # Captura chaves adicionais numeradas (ex: GEMINI_API_KEY_2, GEMINI_API_KEY_3)
    for k in st.secrets:
        if k.startswith("GEMINI_API_KEY_") and st.secrets[k]:
            chaves.append(st.secrets[k])
            
    # Fallback para variável de ambiente
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if env_key and env_key not in chaves:
        chaves.append(env_key)
        
    st.session_state.lista_chaves = chaves
    st.session_state.indice_chave_atual = 0

@st.cache_data(show_spinner=False)
def gerar_pdf_em_cache(pneu_dict_sem_imagens, data_str, cache_key_imagens, _imagens_objetos):
    """
    O parâmetro _imagens_objetos (prefixo '_') é ignorado pelo hasher do
    Streamlit — evita re-hashear bytes de imagem a cada rerun, o que é caro
    e pode fazer o cache nunca "bater". Quem controla se o PDF precisa ser
    regerado é o cache_key_imagens (nomes + ângulo de rotação de cada foto),
    que é leve e estável.
    """
    pneu_completo = dict(pneu_dict_sem_imagens)
    pneu_completo["imagens_objetos"] = _imagens_objetos
    return gerar_pdf_laudo_pneu(pneu_completo, data_str)

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
# ESTILIZAÇÃO CSS (TEMA ESCURO)
# ==============================================================================
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    .stApp, .main {
        background-color: #0d1117;
        color: #ffffff;
    }
    .block-container {
        padding-top: 2rem !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border-radius: 10px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    [data-testid="stFileUploadDropzone"] {
        background-color: #0d1117;
        border: 1px dashed #4b5563;
        border-radius: 8px;
    }
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

# ==============================================================================
# CABEÇALHO
# ==============================================================================
logo_b64 = get_image_base64("ssasdsds.png") or get_image_base64("logo-nobg.png")
logo_img_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 180px; object-fit: contain; margin-right: 20px;">' if logo_b64 else '<span style="font-size: 70px; margin-right: 20px;">🧭</span>'

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; width: 100%; margin-top: 10px; margin-bottom: 10px;">
        {logo_img_html}
        <h1 style="margin: 0; font-weight: 900; font-size: 36px; color: #ffffff; text-align: center;">LAUDO PNEUS COORDENADAS</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown('<hr style="border: none; height: 3px; background-color: #dc2626; margin-top: 15px; margin-bottom: 10px;">', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a1a1aa; font-size: 16px; margin-bottom: 40px;'>Fluxo: <b>1)</b> Envie o relatório e as fotos &nbsp;➔&nbsp; <b>2)</b> Gere o laudo em PDF</p>", unsafe_allow_html=True)

# ==============================================================================
# SEÇÃO 1: RELATÓRIO E FOTOS
# ==============================================================================
st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 15px;'>
        <div style='background-color: #025ca3; color: white; font-weight: bold; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 4px;'>1</div>
        <h3 style='margin: 0; padding: 0; font-size: 24px; color: #ffffff;'>Relatório e Fotos</h3>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("<h4 style='color: #ffffff; margin-top: 0;'><span style='font-size: 18px;'>📄</span> Relatório HTML</h4>", unsafe_allow_html=True)
        st.caption("Envie o relatório exportado em HTML (Relatório de Troca de Pneus - Modelo 4)")
        
        relatorio_file = st.file_uploader(
            "Selecionar arquivo", type=["html", "htm"], accept_multiple_files=False, key="uploader_html", label_visibility="collapsed"
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

with col2:
    with st.container(border=True):
        st.markdown("<h4 style='color: #ffffff; margin-top: 0;'><span style='font-size: 18px;'>🖼️</span> Fotos dos Pneus</h4>", unsafe_allow_html=True)
        st.caption("Envie o lote completo de fotos dos pneus (JPG, PNG)")
        
        uploaded_files = st.file_uploader(
            "Selecionar arquivos", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="uploader_fotos", label_visibility="collapsed"
        )
        modo_analise = st.selectbox(
            "Modo de Análise IA:",
            ["Inspeção Completa (ID Fogo + Sulco + Danos)", "Apenas Extrair Número de 'Fogo' (ID do Pneu)", "Análise Profunda de Danos e Desgaste de Banda"]
        )

if "dados_relatorio" not in st.session_state:
    st.session_state.dados_relatorio = pd.DataFrame(columns=CAMPOS_FIXOS)

if not st.session_state.dados_relatorio.empty:
    with st.expander(f"✅ {len(st.session_state.dados_relatorio)} pneus extraídos do relatório. Clique para ver/editar."):
        st.session_state.dados_relatorio = st.data_editor(
            st.session_state.dados_relatorio, num_rows="dynamic", use_container_width=True, key="editor_dados_relatorio",
        )

# ==============================================================================
# BOTÃO PRINCIPAL
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    if st.button("📤 Gerar Laudo", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("⚠️ Por favor, envie as fotos dos pneus antes de gerar o laudo.")
        elif not st.session_state.get("lista_chaves"):
            st.error("⚠️ Nenhuma Chave de API do Gemini foi configurada nos segredos (GEMINI_API_KEY).")
        else:
            if "inspection_results" not in st.session_state:
                st.session_state.inspection_results = []

            try:
                texto_status = st.empty()
                texto_status.info("Inspecionando imagens com alta precisão visual...")

                fvu_data = st.session_state.fvu_data

                # Prepara o conteúdo da requisição
                dict_fotos_enviadas = {f.name: f for f in uploaded_files}
                sorted_files = sorted(uploaded_files, key=lambda f: f.name)

                # ==============================================================
                # NOVO PROMPT COM GLOSSÁRIO MICHELIN INTEGRADO
                # ==============================================================
                guia_tecnico_fvu = gerar_guia_prompt_fvu()
                
                prompt_instrucoes = f"""
Você é um inspetor técnico sênior credenciado Michelin especialista em pneus de frotas pesadas (caminhões e ônibus).
Sua missão é realizar a verificação visual de pneus rodados, identificar avarias e classificar o laudo no código FVU exato.

ESTRUTURA DE REGRA TÉCNICA E GLOSSÁRIO MICHELIN:
{guia_tecnico_fvu}

TAREFAS PARA CADA PNEU IDENTIFICADO NAS FOTOS:
1. Identifique o número de Fogo no pneu.
2. Liste em "arquivos_fotos" a lista EXATA de nomes dos arquivos que mostram este mesmo pneu.
3. Identifique a marca e estado geral do pneu.
4. Descreva detalhadamente o dano visual encontrado (localização, profundidade, aparência das bordas, presença de arames/cintas).
5. Siga rigorosamente a ÁRVORE DE DECISÃO para definir o "codigo_fvu_sugerido".
6.Tente identificar o código FVU escrito a giz ou tinta no pneu (ex: 70K, 70R, 48D).
   Se não conseguir identificar com clareza, use "75A" como padrão.
   O usuário poderá corrigir manualmente depois.

FORMATO DE RESPOSTA (somente um JSON Array válido, sem formatação markdown):
[
  {{
    "fogo": "string",
    "marca": "string",
    "sulco": "string",
    "arquivos_fotos": ["foto1.jpg"],
    "descricao_dano_ia": "string com descrição técnica rica",
    "codigo_fvu_sugerido": "ex: 48D",
    "confianca": "Alta | Média | Baixa"
  }}
]
"""

                conteudo_requisicao = []
                for f in sorted_files:
                    bytes_comprimidos = comprimir_imagem(f.getvalue())
                    conteudo_requisicao.append(f"Arquivo: {f.name}")
                    conteudo_requisicao.append({"mime_type": "image/jpeg", "data": bytes_comprimidos})
                conteudo_requisicao.append(prompt_instrucoes)

                # ==============================================================
                # SISTEMA DE ROTAÇÃO AUTOMÁTICA DE CHAVES E RETRY
                # ==============================================================
                lista_chaves = st.session_state.lista_chaves
                total_chaves = len(lista_chaves)
                tentativa_chave = 0
                sucesso = False
                resposta_ia = None
                nome_modelo_ativo = ""

                while tentativa_chave < total_chaves and not sucesso:
                    try:
                        chave_atual = lista_chaves[st.session_state.indice_chave_atual]
                        genai.configure(api_key=chave_atual)
                        
                        nome_modelo_ativo = obter_modelo_estavel(genai)
                        model = genai.GenerativeModel(nome_modelo_ativo)
                        
                        texto_status.info(f"Processando com modelo {nome_modelo_ativo} [Chave {st.session_state.indice_chave_atual + 1}/{total_chaves}]...")
                        resposta_ia = model.generate_content(conteudo_requisicao)
                        sucesso = True
                        
                    except Exception as e:
                        erro_str = str(e)
                        if "429" in erro_str or "ResourceExhausted" in type(e).__name__ or "quota" in erro_str.lower():
                            tentativa_chave += 1
                            if tentativa_chave < total_chaves:
                                st.session_state.indice_chave_atual = (st.session_state.indice_chave_atual + 1) % total_chaves
                                texto_status.warning(f"⚠️ Cota esgotada na chave atual (Erro 429). Alternando automaticamente para a próxima chave ({tentativa_chave}/{total_chaves})...")
                                time.sleep(2)
                            else:
                                texto_status.warning(f"⚠️ Todas as chaves atingiram o limite de cota. Aguardando 15s para nova tentativa...")
                                time.sleep(15)
                                raise RuntimeError(f"Limite de cota excedido em todas as chaves disponíveis. Detalhes: {e}")
                        else:
                            raise e

                pneus_estruturados = None
                erro_parse = None
                try:
                    pneus_ia = extrair_json_da_resposta(resposta_ia.text)
                    tabela_df = st.session_state.dados_relatorio
                    pneus_estruturados = []
                    
                    for item in pneus_ia:
                        fogo_lido = str(item.get("fogo", "")).strip()
                        dados_tabela = buscar_dados_relatorio(fogo_lido, tabela_df)
                        
                        desc_ia = item.get("descricao_dano_ia", "")
                        codigo_ia = str(item.get("codigo_fvu_sugerido", "75A")).strip().upper()
                        if not codigo_ia:
                            codigo_ia = "75A"
                        fvu_direto = next((x for x in fvu_data if x["codigo"].strip().upper() == codigo_ia), None)
                        fvu_selecionado = fvu_direto if fvu_direto else encontrar_fvu_por_descricao(desc_ia, fvu_data)
                        
                        if fvu_selecionado:
                            codigo_fvu = fvu_selecionado["codigo"]
                            texto_dano = fvu_selecionado["descricao"]
                            texto_causa = fvu_selecionado["causa"]
                            texto_acao = fvu_selecionado["acao"]
                        else:
                            codigo_fvu = "OK"
                            texto_dano = desc_ia or "Sem avarias severas catalogadas."
                            texto_causa = "-"
                            texto_acao = "Acompanhamento de rotina."

                        # Extrai fotos pertencentes SOMENTE a este pneu
                        fotos_pneu_nomes = item.get("arquivos_fotos", [])
                        imagens_bytes_pneu = []
                        for nome_f in fotos_pneu_nomes:
                            if nome_f in dict_fotos_enviadas:
                                try:
                                    f_obj = dict_fotos_enviadas[nome_f]
                                    f_obj.seek(0)
                                    imagens_bytes_pneu.append(f_obj.getvalue())
                                except Exception:
                                    pass

                        # Extração da quantidade de reformas ("REFORMA") do relatório
                        # Obs: a coluna gerada pelo parser.py se chama exatamente "REFORMA"
                        # (ver CAMPOS_FIXOS em parser.py). Usar outra chave aqui faz o valor
                        # real sempre cair no fallback "0".
                        n_reformas = "0"
                        if dados_tabela is not None:
                            n_reformas = str(dados_tabela.get("REFORMA", "0")).strip()

                        pneu = {
                            "fogo": fogo_lido,
                            "pos": dados_tabela.get("POS", "") if dados_tabela else "",
                            "veiculo": dados_tabela.get("VEICULO", "") if dados_tabela else "",
                            "medida": dados_tabela.get("MEDIDA", "") if dados_tabela else "",
                            "retirada": dados_tabela.get("RETIRADA", "") if dados_tabela else "",
                            "local": dados_tabela.get("LOCAL", "") if dados_tabela else "",
                            "km_pos": dados_tabela.get("KM/POS", "") if dados_tabela else "",
                            "km_total": dados_tabela.get("KM TOTAL", "") if dados_tabela else "",
                            "n_reformas": n_reformas, 
                            "marca": item.get("marca", ""),
                            "sulco": item.get("sulco", ""),
                            "codigo_fvu": codigo_fvu,
                            "danos": texto_dano,
                            "causas_provaveis": texto_causa,
                            "observacoes": texto_acao,
                            "acao_recomendada": texto_acao,
                            "confianca": item.get("confianca", ""),
                            "fogo_localizado_na_planilha": dados_tabela is not None,
                            "imagens_bytes": imagens_bytes_pneu,
                        }
                        pneus_estruturados.append(pneu)

                except Exception as e:
                    erro_parse = str(e)

                if erro_parse:
                    st.error(f"Erro parse: {erro_parse}")
                        
                st.session_state.inspection_results = [{
                    "Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "Modelo_Usado": nome_modelo_ativo,
                    "Analise_IA_Bruta": resposta_ia.text,
                    "Pneus": pneus_estruturados,
                    "Erro_Parse": erro_parse,
                    "Imagens": sorted_files
                }]

                texto_status.success("✅ Inspeção e cruzamento de dados concluídos com sucesso!")

            except Exception as e:
                st.error(f"Erro no processamento: {str(e)}")


# ==============================================================================
# EXIBIÇÃO DOS RESULTADOS (COM MINIATURAS AUTOMÁTICAS AO LADO E CORREÇÃO DE FOGO)
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
            if res["Pneus"]:
                fvu_options = st.session_state.get("fvu_data", [])
                tabela_df = st.session_state.dados_relatorio
                lista_imagens_lote = res["Imagens"]
                total_pneus = len(res["Pneus"])
                
                # Conjunto de índices excluídos pelo usuário (persiste no session_state)
                key_excluidos = f"pneus_excluidos_{res['Timestamp']}"
                if key_excluidos not in st.session_state:
                    st.session_state[key_excluidos] = set()

                for i, pneu in enumerate(res["Pneus"], start=1):
                    # Pula pneus que o usuário excluiu
                    if i in st.session_state[key_excluidos]:
                        continue

                    key_fogo_input = f"input_fogo_corrigido_{i}_{res['Timestamp']}"
                    
                    if key_fogo_input not in st.session_state:
                        st.session_state[key_fogo_input] = pneu.get('fogo', '')

                    with st.container(border=True):
                        # Cabeçalho com input para corrigir o número de fogo caso a IA tenha falhado
                        col_tit1, col_tit2, col_excluir = st.columns([2, 1, 0.4])
                        with col_tit1:
                            fogo_atual_usuario = st.text_input(
                                f"🛞 Pneu {i} — Número de Fogo (Ajuste se necessário)",
                                value=st.session_state[key_fogo_input],
                                key=key_fogo_input
                            ).strip()
                        with col_tit2:
                            dados_tabela_atualizados = buscar_dados_relatorio(fogo_atual_usuario, tabela_df)
                            encontrou_planilha = dados_tabela_atualizados is not None
                            
                            if encontrou_planilha:
                                st.markdown("<p style='color: #22c55e; margin-top: 30px; font-weight: bold;'>✅ Localizado na Planilha</p>", unsafe_allow_html=True)
                            else:
                                st.markdown("<p style='color: #eab308; margin-top: 30px; font-weight: bold;'>⚠️ Não encontrado na planilha</p>", unsafe_allow_html=True)
                        with col_excluir:
                            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("🗑️", key=f"btn_excluir_{i}_{res['Timestamp']}", help=f"Excluir pneu {fogo_atual_usuario} do processamento"):
                                st.session_state[key_excluidos].add(i)
                                st.rerun()

                        pneu_exibicao = pneu.copy()
                        pneu_exibicao['fogo'] = fogo_atual_usuario

                        if dados_tabela_atualizados is not None:
                            pneu_exibicao["pos"] = dados_tabela_atualizados.get("POS", "")
                            pneu_exibicao["veiculo"] = dados_tabela_atualizados.get("VEICULO", "")
                            pneu_exibicao["medida"] = dados_tabela_atualizados.get("MEDIDA", "")
                            pneu_exibicao["retirada"] = dados_tabela_atualizados.get("RETIRADA", "")
                            pneu_exibicao["local"] = dados_tabela_atualizados.get("LOCAL", "")
                            pneu_exibicao["km_pos"] = dados_tabela_atualizados.get("KM/POS", "")
                            pneu_exibicao["km_total"] = dados_tabela_atualizados.get("KM TOTAL", "")
                            pneu_exibicao["n_reformas"] = str(dados_tabela_atualizados.get("REFORMA", "0")).strip()
                            pneu_exibicao["fogo_localizado_na_planilha"] = True
                        else:
                            pneu_exibicao["fogo_localizado_na_planilha"] = False

                        st.markdown("---")

                            # ==============================================================
                        # FOTOS COM ROTAÇÃO DINÂMICA E INTEGRAÇÃO NO PDF
                        # ==============================================================
                        col_fotos, col_dados = st.columns([1, 2])

                        with col_fotos:
                            st.markdown("##### 🖼️ Foto(s):")
                            
                            imagens_do_pneu = []
                            fotos_ia_brutas = pneu.get("arquivos_fotos", [])
                            
                            for f_nome in fotos_ia_brutas:
                                f_lower = str(f_nome).lower().strip()
                                for img_file in lista_imagens_lote:
                                    if f_lower in img_file.name.lower() or img_file.name.lower() in f_lower:
                                        if img_file not in imagens_do_pneu:
                                            imagens_do_pneu.append(img_file)
                            
                            if not imagens_do_pneu and lista_imagens_lote:
                                total_imgs = len(lista_imagens_lote)
                                chunk_size = max(1, total_imgs // total_pneus)
                                start_idx = (i - 1) * chunk_size
                                end_idx = start_idx + chunk_size if i < total_pneus else total_imgs
                                imagens_do_pneu = lista_imagens_lote[start_idx:end_idx]

                            if imagens_do_pneu:
                                for idx_img, img_f in enumerate(imagens_do_pneu):
                                    # Chave única para controlar o ângulo de rotação da imagem no session_state
                                    key_rot = f"rot_img_{res['Timestamp']}_{i}_{idx_img}"
                                    if key_rot not in st.session_state:
                                        st.session_state[key_rot] = 0  # Ângulo inicial (0 graus)

                                    # Botão compacto para girar 90 graus sentido horário
                                    if st.button(f"🔄 Girar 90°", key=f"btn_rot_{key_rot}"):
                                        st.session_state[key_rot] = (st.session_state[key_rot] + 90) % 360

                                    angulo_atual = st.session_state[key_rot]

                                    # Abre a imagem com PIL (Pillow) para aplicar a rotação e exibir/salvar
                                    img_pil = Image.open(img_f)
                                    if angulo_atual > 0:
                                        # Rotaciona no sentido anti-horário no PIL para equivaler ao horário visual
                                        img_pil = img_pil.rotate(-angulo_atual, expand=True)

                                    # Exibe a imagem rotacionada na largura compacta
                                    st.image(img_pil, caption=f"{img_f.name} ({angulo_atual}°)", width=220)

                                    # Salva o ângulo no objeto do pneu para a função de PDF ler depois
                                    if "rotacoes_imagens" not in pneu_exibicao:
                                        pneu_exibicao["rotacoes_imagens"] = {}
                                    pneu_exibicao["rotacoes_imagens"][img_f.name] = angulo_atual
                            else:
                                st.caption("Nenhuma foto disponível.")
                        with col_dados:
                            if fvu_options:
                                current_code = pneu.get("codigo_fvu", "")
                                matching_index = 0
                                for idx, opt in enumerate(fvu_options):
                                    if opt['codigo'].lower() == current_code.lower():
                                        matching_index = idx
                                        break
                                
                                selected_fvu_label = st.selectbox(
                                    f"🔍 Classificação FVU",
                                    options=[f"{x['codigo']} - {x['descricao']}" for x in fvu_options],
                                    index=matching_index,
                                    key=f"select_fvu_{i}_{fogo_atual_usuario}_{res['Timestamp']}"
                                )
                                
                                novo_codigo = selected_fvu_label.split(" - ")[0]
                                novo_fvu_obj = next((x for x in fvu_options if x['codigo'].lower() == novo_codigo.lower()), None)
                                if novo_fvu_obj:
                                    pneu_exibicao["codigo_fvu"] = novo_fvu_obj['codigo']
                                    pneu_exibicao["danos"] = novo_fvu_obj['descricao']
                                    pneu_exibicao["causas_provaveis"] = novo_fvu_obj['causa']
                                    pneu_exibicao["observacoes"] = novo_fvu_obj['acao']
                                    pneu_exibicao["acao_recomendada"] = novo_fvu_obj['acao']
                                    # <- sincroniza com o objeto original
                                    pneu["codigo_fvu"] = novo_fvu_obj['codigo']
                                    pneu["danos"] = novo_fvu_obj['descricao']
                                    pneu["causas_provaveis"] = novo_fvu_obj['causa']
                                    pneu["observacoes"] = novo_fvu_obj['acao']
                                    pneu["acao_recomendada"] = novo_fvu_obj['acao']

                            c1, c2 = st.columns(2)
                            with c1:
                                st.write(f"**POS:** {pneu_exibicao.get('pos', '')}")
                                st.write(f"**VEÍCULO:** {pneu_exibicao.get('veiculo', '')}")
                                st.write(f"**MEDIDA:** {pneu_exibicao.get('medida', '')}")
                                st.write(f"**RETIRADA:** {pneu_exibicao.get('retirada', '')}")
                                st.write(f"**Nº REFORMAS:** {pneu_exibicao.get('n_reformas', '')}")
                            with c2:
                              # --- LISTA SUSPENSA DE UNIDADES/LOCAL ---
                                local_atual = pneu_exibicao.get('local', '').strip().upper()
                                # Descobre o índice atual se já vier preenchido, senão padrão é 0
                                idx_local = 0
                                if local_atual in unidades_disponiveis:
                                    idx_local = unidades_disponiveis.index(local_atual)
                                
                                novo_local = st.selectbox(
                                    "📍 **LOCAL/UNIDADE:**",
                                    options=unidades_disponiveis,
                                    index=idx_local,
                                    key=f"select_local_{i}_{fogo_atual_usuario}_{res['Timestamp']}"
                                )
                                pneu_exibicao['local'] = novo_local
                                pneu['local'] = novo_local  # <- adiciona essa linha
                                # ----------------------------------------
                                st.write(f"**KM POS:** {pneu_exibicao.get('km_pos', '')}")
                                st.write(f"**KM TOTAL:** {pneu_exibicao.get('km_total', '')}")
                                st.write(f"**Confiança IA:** {pneu_exibicao.get('confianca', '')}")

                            st.write(f"**Laudo / Dano Relatado:** {pneu_exibicao.get('danos', '')}")
                            st.write(f"**Causas Prováveis:** {pneu_exibicao.get('causas_provaveis', '')}")
                            st.write(f"**Observações / Ação:** {pneu_exibicao.get('observacoes', '')}")

                            # Logo antes de chamar a função do PDF, adicione esta linha:
                            pneu_exibicao['imagens_objetos'] = imagens_do_pneu
                            pneu_sem_imagens = {k: v for k, v in pneu_exibicao.items() if k != 'imagens_objetos'}
                            cache_key_imagens = tuple(
                                (img.name, pneu_exibicao.get("rotacoes_imagens", {}).get(img.name, 0))
                                for img in imagens_do_pneu
                            )
                            pdf_pneu_bytes = gerar_pdf_em_cache(
                                pneu_sem_imagens,
                                res["Timestamp"].split()[0],
                                cache_key_imagens,
                                imagens_do_pneu,
                            )
                            veiculo_pdf = str(pneu_exibicao.get('veiculo', '')).strip().lstrip('0')
                            local_pdf = pneu_exibicao.get('local', '').strip().replace('/', '-').replace(' ', '_')
                            nome_pdf = f"laudo_{fogo_atual_usuario}"
                            if veiculo_pdf:
                                nome_pdf += f"_{veiculo_pdf}"
                            if local_pdf:
                                nome_pdf += f"_{local_pdf}"
                            st.download_button(
                                label=f"📄 Baixar PDF - Pneu {fogo_atual_usuario}",
                                data=pdf_pneu_bytes,
                                file_name=f"{nome_pdf}.pdf",
                                mime="application/pdf",
                                key=f"btn_pdf_pneu_{fogo_atual_usuario}_{i}_{res['Timestamp']}"
                            )
                # Painel de restauração — aparece só se houver pneus excluídos
                excluidos = st.session_state.get(key_excluidos, set())
                if excluidos:
                    st.markdown("---")
                    st.markdown(f"**🗑️ Pneus excluídos deste lote: {len(excluidos)}**")
                    for idx_exc in sorted(excluidos):
                        pneu_exc = res["Pneus"][idx_exc - 1]
                        fogo_exc = pneu_exc.get("fogo", f"#{idx_exc}")
                        col_info, col_rest = st.columns([3, 1])
                        with col_info:
                            st.caption(f"Pneu {idx_exc} — Fogo {fogo_exc}")
                        with col_rest:
                            if st.button("↩️ Restaurar", key=f"btn_restaurar_{idx_exc}_{res['Timestamp']}"):
                                st.session_state[key_excluidos].discard(idx_exc)
                                st.rerun()

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

# ==============================================================================
# SALVAR NA PLANILHA DE LAUDOS
# ==============================================================================
st.markdown("---")
if st.button("Salvar Laudo na Planilha", use_container_width=True):
    if "inspection_results" in st.session_state and st.session_state.inspection_results:
        ultimo_lote = st.session_state.inspection_results[-1]
        pneus_todos = ultimo_lote.get("Pneus", [])

        # Remove pneus excluídos pelo usuário antes de salvar
        key_excluidos_salvar = f"pneus_excluidos_{ultimo_lote['Timestamp']}"
        excluidos_salvar = st.session_state.get(key_excluidos_salvar, set())
        pneus_para_salvar = [
            p for idx, p in enumerate(pneus_todos, start=1)
            if idx not in excluidos_salvar
        ]

        if pneus_para_salvar:
            sucessos = 0
            erros = []

            # Percorre cada pneu individualmente da lista e salva na planilha
            for pneu in pneus_para_salvar:
                try:
                    sucesso, mensagem = salvar_no_onedrive(pneu)
                    if sucesso:
                        sucessos += 1
                    else:
                        erros.append(f"Pneu {pneu.get('fogo', 'N/D')}: {mensagem}")
                except Exception as e:
                    erros.append(f"Pneu {pneu.get('fogo', 'N/D')}: {e}")
            
            if sucessos > 0:
                st.success(f"✅ {sucessos} pneu(s) gravado(s) no Excel com sucesso!")
            if erros:
                for err in erros:
                    st.error(f"❌ {err}")
        else:
            st.warning("⚠️ Nenhum dado estruturado de pneu encontrado para salvar.")
    else:
        st.warning("⚠️ Você precisa gerar o laudo com a IA primeiro antes de salvar na planilha.")
