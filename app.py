import os
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
from pdf_generator import gerar_pdf_laudo, gerar_pdf_fallback

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (ÍCONE DA BÚSSOLA SOZINHA NA ABA)
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
# ESTILIZAÇÃO CSS (OCULTA BARRA LATERAL + TEMA ESCURO + BOTÃO VERMELHO)
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

    /* Estilização do Botão Principal Vermelho */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        background-color: #dc2626;
        color: white;
        border: none;
        padding: 12px 24px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    div.stButton > button:first-child:hover {
        background-color: #b91c1c;
        color: white;
        border: none;
    }

    /* Ajuste de cores para títulos e divisores */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    hr {
        border-color: #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABEÇALHO (LOGO BÚSSOLA SOZINHA + TÍTULO DA COORDENADAS)
# ==============================================================================
col_logo, col_titulo = st.columns([0.8, 6])

with col_logo:
    if os.path.exists("ssasdsds.png"):
        st.image("ssasdsds.png", width=90)
    elif os.path.exists("logo-nobg.png"):
        st.image("logo-nobg.png", width=90)
    else:
        st.markdown("# 🧭")

with col_titulo:
    st.markdown("<h1 style='margin-bottom: 0px; margin-top: -5px;'>LAUDO PNEUS COORDENADAS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; font-size: 15px;'>Fluxo: 1) Envie o relatório HTML &nbsp;➔&nbsp; 2) Envie as fotos &nbsp;➔&nbsp; 3) Gere o laudo em PDF</p>", unsafe_allow_html=True)

# Configuração da API Key no topo (como a sidebar foi removida)
with st.expander("🔑 Configurações / Chave de API Gemini", expanded=False):
    api_key_input = st.text_input("Chave da API Gemini", type="password", value=os.environ.get("GEMINI_API_KEY", ""))

api_key = api_key_input or st.secrets.get("GEMINI_API_KEY", "")

st.markdown("---")

# ==============================================================================
# SEÇÃO PRINCIPAL (PASSO 1 E PASSO 2 LADO A LADO EM COLUNAS)
# ==============================================================================
col1, col2 = st.columns(2)

# --- COLUNA 1: RELATÓRIO HTML ---
with col1:
    st.markdown("### 📄 1. Relatório de Troca (HTML)")
    relatorio_file = st.file_uploader(
        "Envie o relatório exportado em HTML",
        type=["html", "htm"],
        accept_multiple_files=False,
        key="uploader_html"
    )

    if relatorio_file is not None:
        if st.session_state.get("relatorio_nome_processado") != relatorio_file.name:
            with st.spinner("Extraindo dados do relatório..."):
                try:
                    df_relatorio = parse_relatorio_html(relatorio_file.getvalue())
                    st.session_state.dados_relatorio = df_relatorio
                    st.session_state.relatorio_nome_processado = relatorio_file.name
                except Exception as e:
                    st.error(f"Não foi possível processar o relatório: {e}")

    if "dados_relatorio" not in st.session_state:
        st.session_state.dados_relatorio = pd.DataFrame(columns=CAMPOS_FIXOS)

    if not st.session_state.dados_relatorio.empty:
        st.success(f"✅ {len(st.session_state.dados_relatorio)} pneus extraídos do relatório.")
        with st.expander("📋 Ver / editar dados extraídos do relatório", expanded=False):
            st.caption("Pode corrigir manualmente qualquer campo antes de gerar o laudo.")
            st.session_state.dados_relatorio = st.data_editor(
                st.session_state.dados_relatorio,
                num_rows="dynamic",
                use_container_width=True,
                key="editor_dados_relatorio",
            )
    else:
        with st.expander("📋 Tabela de Dados Manual / Vazia", expanded=False):
            st.caption("Nenhum relatório carregado ainda — envie o HTML acima ou preencha manualmente:")
            st.session_state.dados_relatorio = st.data_editor(
                st.session_state.dados_relatorio,
                num_rows="dynamic",
                use_container_width=True,
                key="editor_dados_relatorio_manual",
            )

# --- COLUNA 2: FOTOS DOS PNEUS ---
with col2:
    st.markdown("### 📷 2. Fotos dos Pneus")
    uploaded_files = st.file_uploader(
        "Envie o lote completo de fotos dos pneus",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="uploader_fotos"
    )

    modo_analise = st.selectbox(
        "Selecione o Modo de Análise",
        [
            "Inspeção Completa (ID Fogo + Sulco + Danos)",
            "Apenas Extrair Número de 'Fogo' (ID do Pneu)",
            "Análise Profunda de Danos e Desgaste de Banda"
        ]
    )

# ==============================================================================
# BOTÃO PRINCIPAL DE EXECUÇÃO
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 GERAR LAUDO EM PDF", type="primary"):
    if not uploaded_files:
        st.warning("⚠️ Por favor, envie as fotos dos pneus antes de gerar o laudo.")
    elif not api_key:
        st.error("⚠️ Por favor, insira sua chave da API Gemini nas configurações acima.")
    else:
        if "inspection_results" not in st.session_state:
            st.session_state.inspection_results = []

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)

            texto_status = st.empty()
            texto_status.text("Selecionando modelo estável...")

            nome_modelo_ativo = obter_modelo_estavel(genai)
            texto_status.text(f"Conectado ao modelo: {nome_modelo_ativo}. Comprimindo lote de fotos...")

            model = genai.GenerativeModel(nome_modelo_ativo)
            sorted_files = sorted(uploaded_files, key=lambda f: f.name)

            prompt_instrucoes = f"""
            Você é um inspetor especialista em inventário de pneus de frota (SMART-LOG).
            Abaixo estão {len(sorted_files)} fotos ordenadas cronologicamente.

            Sua tarefa:
            1. Analise todas as imagens e agrupe-as por pneu individual. Cada novo pneu começa com a
               foto da lateral contendo o número de 'Fogo' (identificação pintada em giz/tinta, ex: 32813),
               seguida das fotos de banda de rodagem/sulco/danos daquele pneu até a próxima foto de 'Fogo'.
            2. Para cada pneu, leia o número de Fogo exatamente como aparece na foto (todos os dígitos,
               incluindo zeros à esquerda se estiverem visíveis).
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

            NÃO invente dados de placa, posição, quilometragem ou datas — essas informações não vêm
            das fotos e serão preenchidas separadamente a partir do relatório da frota.
            """

            conteudo_requisicao = []
            for f in sorted_files:
                bytes_comprimidos = comprimir_imagem(f.getvalue())
                conteudo_requisicao.append(f"Arquivo: {f.name}")
                conteudo_requisicao.append({"mime_type": "image/jpeg", "data": bytes_comprimidos})
            conteudo_requisicao.append(prompt_instrucoes)

            texto_status.text(f"Enviando dados para a IA ({nome_modelo_ativo})...")
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

# ==============================================================================
# EXIBIÇÃO DOS RESULTADOS (LAUDO CONSOLIDADO)
# ==============================================================================
if st.session_state.get("inspection_results"):
    st.markdown("---")
    st.subheader("📊 Laudo Consolidado")

    for res in st.session_state.inspection_results:
        with st.expander(f"🛞 Laudo do Lote ({len(res['Imagens'])} fotos) - Modelo: {res.get('Modelo_Usado', 'gemini-flash-latest')}", expanded=True):
            st.markdown("##### Miniaturas Enviadas:")
            cols = st.columns(min(len(res["Imagens"]), 6))
            for idx, img_file in enumerate(res["Imagens"]):
                with cols[idx % 6]:
                    st.image(img_file, caption=img_file.name, use_container_width=True)

            st.markdown("---")

            if res["Pneus"]:
                st.markdown("#### 🤖 Laudo por Pneu")
                for i, pneu in enumerate(res["Pneus"], start=1):
                    titulo = f"PNEU {i} — FOGO {pneu.get('fogo', 'N/A')}"
                    if pneu.get("fogo_localizado_na_planilha") is False:
                        titulo += " ⚠️ (não encontrado na planilha)"
                    with st.container(border=True):
                        st.markdown(f"**{titulo}**")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"**POS:** {pneu.get('pos', '')}")
                            st.write(f"**VEICULO:** {pneu.get('veiculo', '')}")
                            st.write(f"**MEDIDA:** {pneu.get('medida', '')}")
                            st.write(f"**RETIRADA:** {pneu.get('retirada', '')}")
                        with c2:
                            st.write(f"**LOCAL:** {pneu.get('local', '')}")
                            st.write(f"**KM/POS:** {pneu.get('km_pos', '')}")
                            st.write(f"**KM TOTAL:** {pneu.get('km_total', '')}")
                            st.write(f"**Confiança:** {pneu.get('confianca', '')}")
                        st.write(f"**Marca/Fabricante:** {pneu.get('marca', '')}")
                        st.write(f"**Condição do Sulco:** {pneu.get('sulco', '')}")
                        st.write(f"**Danos/Anomalias:** {pneu.get('danos', '')}")
                        st.write(f"**Ação Recomendada:** {pneu.get('acao_recomendada', '')}")

                pdf_bytes = gerar_pdf_laudo(res["Pneus"], res["Timestamp"])
                st.download_button(
                    label="📥 Baixar Laudo Técnico em PDF",
                    data=pdf_bytes,
                    file_name=f"laudo_pneus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary",
                )
            else:
                st.warning(
                    "⚠️ A IA respondeu, mas não foi possível estruturar o resultado automaticamente "
                    f"({res.get('Erro_Parse', 'motivo desconhecido')}). Veja a resposta bruta abaixo e, "
                    "se necessário, baixe o laudo em formato simples."
                )
                st.text_area("Resposta bruta da IA", res["Analise_IA_Bruta"], height=300)
                pdf_fallback = gerar_pdf_fallback(res["Analise_IA_Bruta"], res["Timestamp"])
                st.download_button(
                    label="📥 Baixar Laudo (texto simples) em PDF",
                    data=pdf_fallback,
                    file_name=f"laudo_pneus_bruto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary",
                )
