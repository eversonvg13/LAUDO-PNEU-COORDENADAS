import os
import datetime
import streamlit as st
import pandas as pd

# Importação dos módulos customizados do projeto
try:
    from parser import parse_html_report
except Exception as e:
    parse_html_report = None
    st.error(f"⚠️ Erro ao importar parser.py: {e}")

try:
    from ai_helper import process_images_with_ai
except Exception as e:
    process_images_with_ai = None

try:
    from pdf_generator import gerar_pdf_laudo
except Exception as e:
    gerar_pdf_laudo = None
    st.error(f"⚠️ Erro ao importar pdf_generator.py: {e}")


# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & ÍCONE DA ABA
# ---------------------------------------------------------
ICON_PATH = "ssasdsds.png" if os.path.exists("ssasdsds.png") else ("logo-nobg.png" if os.path.exists("logo-nobg.png") else "🎯")

st.set_page_config(
    page_title="Laudo Pneus Coordenadas",
    page_icon=ICON_PATH,
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------
# 2. ESTILIZAÇÃO CSS CUSTOMIZADA (CORES DA MARCA)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Ocultar Barra Lateral (Sidebar) e Botão de Alternância */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* Ajuste do container principal */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    /* Título Principal Unificado */
    .main-title {
        font-family: 'Helvetica Neue', Roboto, Arial, sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0;
        padding: 0;
    }

    /* Subtítulo do Fluxo */
    .sub-title {
        font-size: 0.95rem;
        color: #A0AAB2;
        margin-top: 4px;
        margin-bottom: 1.5rem;
    }

    /* Estilização dos Botões no Vermelho da Logo (#D31C24) */
    .stButton > button {
        background-color: #D31C24 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 0.65rem 1.5rem !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #B0151B !important;
        box-shadow: 0px 4px 14px rgba(211, 28, 36, 0.45);
    }

    /* Destaque nos Expanders com o Verde/Teal da Logo (#005C54) */
    div[data-testid="stExpander"] {
        border: 1px solid #005C54 !important;
        border-radius: 8px;
    }

    /* Ajuste visual das caixas de upload */
    div[data-testid="stFileUploader"] {
        padding: 0.5rem;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. CABEÇALHO: LOGO DA BÚSSOLA + TÍTULO
# ---------------------------------------------------------
col_logo, col_header = st.columns([1.5, 8.5], vertical_alignment="center")

with col_logo:
    if os.path.exists("ssasdsds.png"):
        st.image("ssasdsds.png", width=140)
    elif os.path.exists("logo-nobg.png"):
        st.image("logo-nobg.png", width=140)
    else:
        st.write("🧭")

with col_header:
    st.markdown('<h1 class="main-title">LAUDO PNEUS COORDENADAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Fluxo: 1) Envie o relatório HTML &nbsp;➔&nbsp; 2) Envie as fotos &nbsp;➔&nbsp; 3) Gere o laudo em PDF</p>', unsafe_allow_html=True)

st.markdown("---")


# ---------------------------------------------------------
# MEMÓRIA DE SESSÃO DO STREAMLIT (SESSION STATE)
# ---------------------------------------------------------
if "df_dados" not in st.session_state:
    st.session_state["df_dados"] = None


# ---------------------------------------------------------
# 4. UPLOADS LADO A LADO (COMPACTOS)
# ---------------------------------------------------------
col_html, col_imgs = st.columns(2, gap="large")

with col_html:
    st.markdown("### 📄 1. Relatório de Troca (HTML)")
    uploaded_html = st.file_uploader(
        "Envie o relatório exportado em HTML", 
        type=["html", "htm"], 
        key="html_uploader"
    )

    if uploaded_html is not None:
        if parse_html_report is not None:
            # Processa o HTML apenas se ainda não está guardado na sessão
            if st.session_state["df_dados"] is None:
                try:
                    uploaded_html.seek(0)
                    resultado = parse_html_report(uploaded_html)
                    
                    if resultado is not None and len(resultado) > 0:
                        st.session_state["df_dados"] = resultado
                    else:
                        st.error("⚠️ O arquivo HTML foi recebido, mas a função `parse_html_report` não encontrou dados de pneus nele.")
                except Exception as e:
                    st.error(f"Erro ao processar o arquivo HTML: {e}")

            # Se já temos dados na memória
            if st.session_state["df_dados"] is not None:
                df_temp = st.session_state["df_dados"]
                qtd = len(df_temp) if hasattr(df_temp, "__len__") else 0
                st.success(f"✅ {qtd} pneus extraídos com sucesso.")
                
                with st.expander("📋 Ver / editar dados extraídos do relatório"):
                    if isinstance(df_temp, pd.DataFrame):
                        # Permite edição visual e atualiza a sessão
                        st.session_state["df_dados"] = st.data_editor(df_temp, num_rows="dynamic", use_container_width=True)
                    else:
                        st.write(df_temp)
        else:
            st.error("⚠️ A função `parse_html_report` não está disponível. Verifique o `parser.py`.")
    else:
        # Se o usuário remover o arquivo, limpa a sessão
        st.session_state["df_dados"] = None

with col_imgs:
    st.markdown("### 📸 2. Fotos dos Pneus")
    uploaded_images = st.file_uploader(
        "Envie o lote completo de fotos dos pneus", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True,
        key="img_uploader"
    )

    if uploaded_images:
        st.info(f"📸 {len(uploaded_images)} foto(s) carregada(s) com sucesso.")


# ---------------------------------------------------------
# 5. AÇÃO PRINCIPAL: GERAÇÃO DO LAUDO PDF
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    if st.button("🚀 GERAR LAUDO EM PDF", use_container_width=True):
        df_dados_atual = st.session_state.get("df_dados")

        if uploaded_html is None or df_dados_atual is None:
            st.warning("⚠️ Por favor, envie um relatório HTML válido antes de continuar.")
        elif not uploaded_images:
            st.warning("⚠️ Por favor, envie as fotos dos pneus antes de gerar o laudo.")
        else:
            with st.spinner("Processando dados e gerando laudo PDF..."):
                try:
                    if gerar_pdf_laudo is not None:
                        timestamp_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                        # Converte DataFrame para lista de dicionários se necessário
                        if isinstance(df_dados_atual, pd.DataFrame):
                            pneus_input = df_dados_atual.to_dict(orient="records")
                        else:
                            pneus_input = df_dados_atual

                        if not pneus_input:
                            st.error("⚠️ Nenhum dado de pneu válido encontrado para gerar o PDF.")
                        else:
                            pdf_bytes = gerar_pdf_laudo(pneus_input, timestamp_atual)

                            st.success("🎉 Laudo em PDF gerado com sucesso!")
                            st.download_button(
                                label="📥 Baixar Laudo PDF",
                                data=pdf_bytes,
                                file_name=f"Laudo_Pneus_Coordenadas_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    else:
                        st.error("A função `gerar_pdf_laudo` não está carregada corretamente. Verifique o `pdf_generator.py`.")

                except Exception as e:
                    st.error(f"Ocorreu um erro ao gerar o laudo: {e}")
