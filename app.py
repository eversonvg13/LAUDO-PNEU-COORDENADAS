import streamlit as st
import os

# 1. Configuração da página (Modo Wide + Esconder Sidebar)
st.set_page_config(
    page_title="Laudo Pneus Coordenadas",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Estilo CSS Customizado (Cores da Coordenadas + Ocultar Sidebar)
st.markdown("""
    <style>
    /* Ocultar Barra Lateral (Sidebar) e Botão de Alternância */
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* Ajuste de espaçamento no topo da página */
    .block-container {
        padding-top: 1.5rem;
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
        letter-spacing: 1px;
        margin-top: 5px;
        margin-bottom: 2px;
    }

    /* Subtítulo / Fluxo */
    .sub-title {
        font-size: 0.95rem;
        color: #A0AAB2;
        margin-bottom: 1.5rem;
    }

    /* Estilização dos Botões com Vermelho da Logo */
    .stButton > button {
        background-color: #D31C24 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #B0151B !important;
        box-shadow: 0px 4px 12px rgba(211, 28, 36, 0.4);
    }

    /* Bordas de destaque nas seções */
    div[data-testid="stExpander"] {
        border: 1px solid #005C54 !important;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TOPO: LOGO E TÍTULO PRINCIPAL (SEM BARRA LATERAL)
# ---------------------------------------------------------
col_logo, col_header = st.columns([1, 6], vertical_alignment="center")

with col_logo:
    # Garanta que a imagem 'logo-nobg.png' esteja na raiz da pasta do seu projeto
    if os.path.exists("logo-nobg.png"):
        st.image("logo-nobg.png", width=120)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.write("🧭") # Fallback caso a imagem ainda não esteja na pasta

with col_header:
    st.markdown('<h1 class="main-title">LAUDO PNEUS COORDENADAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Fluxo: 1) Envie o relatório HTML &nbsp;➔&nbsp; 2) Envie as fotos &nbsp;➔&nbsp; 3) Gere o laudo em PDF</p>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# UPLOAD COMPACTO LADO A LADO (2 COLUNAS)
# ---------------------------------------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 📄 1. Relatório de Troca (HTML)")
    uploaded_html = st.file_uploader(
        "Envie o relatório exportado em HTML", 
        type=["html", "htm"], 
        key="html_uploader"
    )
    
    if uploaded_html:
        st.success("✅ Relatório carregado com sucesso!")
        with st.expander("📋 Ver / editar dados extraídos do relatório"):
            st.info("Aqui entram as tabelas/dados parseados do HTML.")

with col2:
    st.markdown("### 📸 2. Fotos dos Pneus")
    uploaded_images = st.file_uploader(
        "Envie o lote completo de fotos dos pneus", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True,
        key="img_uploader"
    )
    
    if uploaded_images:
        st.info(f"📸 {len(uploaded_images)} foto(s) carregada(s).")

# ---------------------------------------------------------
# AÇÃO PRINCIPAL / GERAÇÃO DE LAUDO
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    if st.button("🚀 GERAR LAUDO EM PDF", use_container_width=True):
        if not uploaded_html:
            st.warning("Por favor, faça o upload do relatório HTML primeiro.")
        else:
            st.success("Gerando laudo com inteligência artificial...")
            # Chame aqui a função do seu `pdf_generator.py`
