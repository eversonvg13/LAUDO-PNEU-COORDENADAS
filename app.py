import os
import base64
import time
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image
import google.generativeai as genai

# Importações dos módulos locais
from parser import parse_relatorio_html, CAMPOS_FIXOS
from ai_helper import (
    comprimir_imagem,
    obter_modelo_estavel,
    buscar_dados_relatorio,
    extrair_json_da_resposta,
)
from pdf_generator import gerar_pdf_laudo_pneu, gerar_pdf_fallback

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

# ==============================================================================
# TABELA DE PALAVRAS-CHAVE E MATCHING FVU
# ==============================================================================
FVU_KEYWORDS = {
    # 45B — motorista sobe em obstáculo alto (meio-fio, cabeçeira de ponte, pedra)
    # com a BANDA DE RODAGEM. Corte atravessa de flanco a flanco na banda. Corte profundo transversal.
    "45B": {
        "pos": ["corte banda", "corte transversal", "corte de flanco a flanco", "ruptura banda",
                "banda rompida", "corte profundo banda", "impacto obstáculo", "meio-fio banda",
                "cabeçeira", "corte na banda de rodagem", "rasgo banda", "objeto banda"],
        "neg": ["flanco", "talão", "ressulc", "desgaste", "liso", "careca", "calvo",
                "sem sulco", "cinta", "irregular", "rachadura flanco"],
    },
    # 45F — corte HORIZONTAL pequeno no flanco, geralmente único e retilíneo, com algumas ranhuras.
    "45F": {
        "pos": ["corte horizontal flanco", "corte retilíneo flanco", "corte pequeno flanco",
                "corte lateral", "ranhura flanco", "ferida flanco", "furo flanco",
                "corte flanco", "incisão flanco", "objeto cortante flanco"],
        "neg": ["talão", "ressulc", "banda de rodagem", "desgaste", "cinta",
                "grande", "arrancou", "pedaço", "circunferencial", "rachadura"],
    },
    # 45G — parecido com 45F mas o corte é MAIOR, pode arrancar pedaços do flanco.
    "45G": {
        "pos": ["corte grande flanco", "rasgo flanco", "arrancou pedaço flanco",
                "dano extenso flanco", "corte profundo flanco", "flanco danificado gravemente",
                "pedaço arrancado flanco", "lesão grande flanco", "impacto flanco severo"],
        "neg": ["talão", "ressulc", "banda de rodagem", "desgaste", "cinta",
                "horizontal pequeno", "ranhura", "lonas expostas", "destruído", "rachadura"],
    },
    # 45N — ressulcagem EXECUTADA mas fora dos parâmetros do CONTRAN (profundidade/largura errada).
    # Só em pneu SEM reforma (desenho original do fabricante).
    "45N": {
        "pos": ["ressulcagem incorreta", "ressulcagem fora do padrão", "ressulcagem mal executada",
                "ressulcagem irregular", "ressulco incorreto", "frieza fora do padrão",
                "sulco fora da norma", "ressulcagem inadequada"],
        "neg": ["não ressulcado", "sem ressulcagem", "reforma"],
    },
    # 45R — NÃO realizou a ressulcagem quando deveria. Só em pneu SEM reforma.
    "45R": {
        "pos": ["não ressulcado", "sem ressulcagem", "ressulcagem não realizada",
                "pneu não ressulcado", "falta de ressulcagem", "ressulcagem ausente",
                "deveria ter sido ressulcado"],
        "neg": ["incorreta", "mal executada", "fora do padrão", "reforma"],
    },
    # 45D — desgaste IRREGULAR: um lado da banda mais desgastado que o outro (diferença nos sulcos).
    # NÃO há cinta aparente. Se atingiu a cinta → obrigatoriamente 48D.
    "45D": {
        "pos": ["desgaste irregular", "desgaste de um lado", "sulco mais baixo de um lado",
                "desgaste assimétrico", "ombro desgastado", "desgaste lateral",
                "diferença de sulco", "alinhamento", "desgaste desigual", "um lado mais desgastado"],
        "neg": ["cinta aparente", "cinta exposta", "cinta visível", "liso", "careca",
                "sem sulco", "calvo", "desgaste total", "extremo"],
    },
    # 46F — agressões REPETIDAS no mesmo ponto do flanco (circunferenciais).
    # Ex: peça do veículo solta rodando no pneu, ou pedra presa entre duplos.
    "46F": {
        "pos": ["agressão repetida flanco", "dano circunferencial flanco", "marcas repetidas flanco",
                "pedra entre duplos", "peça solta contato pneu", "perfuração circunferencial",
                "fissura circunferencial flanco", "ranhuras circunferenciais", "dano ao longo do flanco",
                "abrasão repetida flanco", "sulco circunferencial flanco"],
        "neg": ["talão", "banda de rodagem", "ressulc", "desgaste", "corte único", "corte pontual"],
    },
    # 48D — cintas/fios de aço APARENTES. Não necessariamente desgaste irregular nos sulcos.
    # Se desgaste irregular atingiu a cinta → também é 48D.
    "48D": {
        "pos": ["cinta aparente", "cinta exposta", "cinta visível", "fio de aço exposto",
                "aço aparente", "careca", "calvo", "liso", "sem sulco", "banda lisa",
                "desgaste até a cinta", "lona exposta banda", "desgaste extremo",
                "desgaste total banda", "sulco inexistente", "limite de desgaste",
                "indicador de desgaste", "desgaste excessivo"],
        "neg": ["flanco", "talão", "ressulc", "rachadura", "corte"],
    },
    # 52B — rodou com BAIXA PRESSÃO mas sem destruição externa visível.
    # Dano aparece INTERNAMENTE: ranhuras ou rachaduras no liner (butílico) interno.
    "52B": {
        "pos": ["baixa pressão", "liner danificado", "butílico danificado", "dano interno",
                "ranhura interna", "rachadura interna", "flexão por baixa pressão",
                "marca interna", "linha interna rachada", "butil rachado", "dano no liner"],
        "neg": ["sem ar", "vazio", "rodou vazio", "pó interno", "esfarelamento",
                "destruído externamente", "flanco sem estrutura"],
    },
    # 52H — rodou completamente SEM AR. Dano externo e/ou interno grave.
    # Internamente: pó (borracha esfarelada pela fricção). Externamente: flanco destruído sem estrutura.
    "52H": {
        "pos": ["rodou sem ar", "pó interno", "borracha esfarelada", "esfarelamento interno",
                "flanco sem estrutura", "sem ar", "vazio", "rodou vazio",
                "destruído externamente", "flanco colapsado", "fricção interna",
                "pneu murcho rodou", "pressão zero rodou"],
        "neg": ["baixa pressão", "dano somente interno", "liner", "butílico", "sobrecarga"],
    },
    # 70J — lona de REFORÇO DO TALÃO se desprende do encordoamento por aquecimento excessivo/abrupto.
    # Visualmente: talão muito destruído, dano se estende para parte do flanco. Aquecimento é a causa.
    "70J": {
        "pos": ["lona talão desprendida", "reforço talão desprendido", "encordoamento talão",
                "talão destruído", "aquecimento talão", "separação lona talão",
                "talão aberto", "lona reforço solta", "talão danificado gravemente",
                "dano talão e flanco", "talão afetado flanco"],
        "neg": ["rachadura", "trinca", "crack", "montagem", "desmontagem", "alavanca",
                "cordoeis rompidos", "zona baixa"],
    },
    # 70K — rachadura CIRCUNFERENCIAL no flanco bem acima do talão.
    # Parece com 45F mas é uma rachadura oscilante (como parede rachada), não corte retilíneo.
    "70K": {
        "pos": ["rachadura circunferencial flanco", "trinca circunferencial flanco",
                "rachadura horizontal flanco", "rachadura oscilante flanco",
                "rachadura acima talão", "fissura circunferencial lateral",
                "rachadura parede flanco", "crack circunferencial flanco"],
        "neg": ["corte retilíneo", "corte pontual", "talão", "zona baixa", "montagem",
                "pequeno corte", "ranhura", "banda"],
    },
    # 70L — rompimento dos CORDOÉIS (encordoamento) do talão. Parecido com 70J mas aqui os cordoéis rompem.
    "70L": {
        "pos": ["cordoéis rompidos", "encordoamento rompido", "cordoéis talão rompidos",
                "ruptura cordoéis", "cordão talão rompido", "arames talão rompidos",
                "encordoamento talão partido"],
        "neg": ["rachadura", "trinca", "zona baixa", "montagem", "desmontagem",
                "lona reforço", "circunferencial"],
    },
    # 70Q — zona do talão ABAIXA/deforma sem rachadura. Deixa o pneu suscetível ao 70R.
    # NÃO há rachadura na zona baixa — apenas afundamento/deformação.
    "70Q": {
        "pos": ["zona talão abaixada", "talão afundado", "zona baixa deformada",
                "talão deformado sem rachadura", "afundamento talão", "talão baixo",
                "deformação zona talão", "talão sem rachadura deformado"],
        "neg": ["rachadura", "trinca", "crack", "fissura", "pé de galinha",
                "ruptura", "cordoéis", "montagem"],
    },
    # 70R — rachadura na ZONA BAIXA DO TALÃO. O famoso "pé de galinha no talão".
    # Diferencia do 70Q justamente por TER rachadura. Pode ser grande ou pequena.
    "70R": {
        "pos": ["rachadura zona baixa", "pé de galinha", "trinca zona baixa",
                "rachadura talão", "fissura zona baixa", "crack zona baixa talão",
                "rachadura base talão", "trinca base talão", "pé de galinha talão",
                "rachadura na zona do talão"],
        "neg": ["flanco", "circunferencial", "montagem", "desmontagem",
                "cordoéis", "lona reforço", "destruído"],
    },
    # 71J — borracheiro danifica o talão na montagem/desmontagem.
    # Fica próximo da parte interna do pneu, no alto do talão (assentamento/vedação da roda).
    # Talão em bom estado — zona baixa sem deformação funda.
    "71J": {
        "pos": ["dano montagem", "dano desmontagem", "talão danificado montagem",
                "marca ferramenta talão", "alavanca talão", "corte montagem",
                "dano assentamento roda", "região vedação talão danificada",
                "alto talão danificado", "ferramental talão"],
        "neg": ["rachadura", "trinca", "zona baixa funda", "aquecimento",
                "flanco", "circunferencial", "cordoéis"],
    },
    # 71K — parecido com 71J mas o talão já estava aquecido/fragilizado antes da montagem/desmontagem.
    # Diferencial: zona baixa do talão está FUNDA (deformada). Se zona baixa funda → 71K; se não → 71J.
    "71K": {
        "pos": ["talão aquecido", "talão fragilizado", "quebra talão aquecido",
                "zona baixa funda", "zona baixa deformada profunda", "talão fundo",
                "pneu aquecido desmontagem", "quebra montagem talão fragilizado"],
        "neg": ["rachadura", "trinca", "pé de galinha", "flanco", "circunferencial"],
    },
    # 75A — contato prolongado com óleo/derivado de petróleo.
    # Flanco ESTUFADO para fora (visível de cima). Manchas de óleo na lateral.
    "75A": {
        "pos": ["flanco estufado", "estufamento lateral", "óleo flanco", "manchado óleo",
                "absorção óleo", "derivado petróleo", "contato óleo", "lateral estufada",
                "flanco inchado", "mancha derivado", "óleo na lateral", "borracha estufada"],
        "neg": ["corte", "rachadura", "desgaste", "talão", "banda"],
    },
}

def encontrar_fvu_por_descricao(descricao_ia, fvu_data):
    if not descricao_ia or not fvu_data:
        return fvu_data[0] if fvu_data else None

    desc_lower = descricao_ia.lower()
    melhor_match = None
    max_score = -999

    for item in fvu_data:
        codigo = item["codigo"].strip().upper()
        kw = FVU_KEYWORDS.get(codigo, {})
        score = 0
        for termo in kw.get("pos", []):
            if termo in desc_lower:
                score += 3
        for termo in kw.get("neg", []):
            if termo in desc_lower:
                score -= 4
        texto_fvu = (item["descricao"] + " " + item["categoria"]).lower()
        for palavra in [p for p in texto_fvu.split() if len(p) > 3]:
            if palavra in desc_lower:
                score += 1
        if score > max_score:
            max_score = score
            melhor_match = item

    return melhor_match if melhor_match and max_score > 0 else fvu_data[0]

@st.cache_data(show_spinner=False)
def gerar_pdf_em_cache(pneu_dict, data_str):
    return gerar_pdf_laudo_pneu(pneu_dict, data_str)

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

                fvu_data = carregar_tabela_fvu()
                
                # Prepara o conteúdo da requisição
                dict_fotos_enviadas = {f.name: f for f in uploaded_files}
                sorted_files = sorted(uploaded_files, key=lambda f: f.name)

                linhas_fvu = "\n".join([
                    f'  {{"codigo": "{x["codigo"]}", "descricao": "{x["descricao"]}", "categoria": "{x["categoria"]}"}}'
                    for x in fvu_data
                ])
                prompt_instrucoes = f"""
Você é um inspetor técnico especialista em pneus de frotas pesadas.
Analise as fotos enviadas e inspecione cada pneu.

Sua tarefa para cada pneu:
1. Leia o número de Fogo escrito a giz.
2. Indique a lista EXATA de nomes dos arquivos de imagem que pertencem a este pneu em "arquivos_fotos".
3. Identifique a marca e estado geral do pneu.
4. Descreva detalhadamente o dano visual encontrado.
5. CLASSIFIQUE o dano escolhendo o código FVU mais adequado da tabela abaixo.
   Se o pneu estiver em bom estado, use "OK".

TABELA FVU:
[
{linhas_fvu}
]

REGRAS CRÍTICAS DE CLASSIFICAÇÃO (leia com atenção):

BANDA DE RODAGEM:
- 48D = banda LISA, CARECA, sem sulcos, desgaste total/extremo. Se a banda estiver calva → sempre 48D, nunca 45B.
- 45B = dano PONTUAL na banda (corte, rasgo por objeto/prego). NÃO use para desgaste generalizado.
- 45D = desgaste IRREGULAR (mais desgastado de um lado), causado por problemas de alinhamento.

FLANCO (lateral do pneu):
- 45F = furo/ferida acidental por objeto pontiagudo no flanco.
- 45G = choque/beliscão no flanco por buraco ou meio-fio, sem destruição total.
- 70R = RACHADURA ou TRINCA profunda no flanco ou zona baixa. Visual: fissura/corte profundo no lateral.
- 70J = flanco ou carcaça DESTRUÍDA com lonas metálicas/arames expostos e desenrolados. Visual: pneu explodido/aberto com estrutura interna visível. NÃO confundir com 45G (que é apenas um choque/amassado).

TALÃO (borda interna que encaixa na roda):
- 70J = desenrolamento da lona carcaça — estrutura interna completamente exposta e destruída.
- 70K = separação do reforço do talão da roda/aro.
- 70L = ruptura da lona carcaça especificamente no talão.
- 70Q = deformação/alteração do talão sem ruptura.
- 70R = rachadura/trinca na zona baixa ou flanco.

MONTAGEM/DESMONTAGEM:
- 71J = marca de alavanca ou ferramenta durante montagem/desmontagem. NÃO use quando o dano é por flexão ou uso.

RESUMO DOS MAIS CONFUNDIDOS:
- Flanco destruído com lonas expostas → 70J (não 45G, não 70L)
- Rachadura/trinca no flanco → 70R (não 71J, não 70J)
- Banda lisa/careca → 48D (não 45B)

Responda SOMENTE com um array JSON válido, sem texto adicional:
[
  {{
    "fogo": "string",
    "marca": "string",
    "sulco": "string",
    "arquivos_fotos": ["arquivo1.jpg"],
    "descricao_dano_ia": "string",
    "codigo_fvu_sugerido": "ex: 45D ou OK",
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
                        codigo_ia = str(item.get("codigo_fvu_sugerido", "")).strip().upper()
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

                        # Extração da quantidade de reformas ("Re") do relatório
                        n_reformas = "0"
                        if dados_tabela is not None:
                            n_reformas = str(dados_tabela.get("Re", dados_tabela.get("REFORMAS", dados_tabela.get("RE", "0")))).strip()

                        pneu = {
                            "fogo": fogo_lido,
                            "pos": dados_tabela.get("POS", "") if dados_tabela else "",
                            "veiculo": dados_tabela.get("VEICULO", "") if dados_tabela else "",
                            "medida": dados_tabela.get("MEDIDA", "") if dados_tabela else "",
                            "retirada": dados_tabela.get("RETIRADA", "") if dados_tabela else "",
                            "local": dados_tabela.get("LOCAL", "") if dados_tabela else "",
                            "km_pos": dados_tabela.get("KM/POS", "") if dados_tabela else "",
                            "km_total": dados_tabela.get("KM TOTAL", "") if dados_tabela else "",
                            "n_reformas": dados_tabela.get("REFORMA", "") if dados_tabela else "",
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
# EXIBIÇÃO DOS RESULTADOS (COM MENU DE CORREÇÃO)
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
                    st.image(img_file, caption=img_file.name, width=150)

            st.markdown("---")

            if res["Pneus"]:
                fvu_options = st.session_state.get("fvu_data", [])
                
                for i, pneu in enumerate(res["Pneus"], start=1):
                    fogo_num = pneu.get('fogo', f'N/A_{i}')
                    titulo = f"PNEU {i} — FOGO {fogo_num}"
                    if pneu.get("fogo_localizado_na_planilha") is False:
                        titulo += " ⚠️ (não encontrado na planilha)"

                    with st.container(border=True):
                        st.markdown(f"### 🛞 {titulo}")
                        
                        pneu_exibicao = pneu.copy()
                        
                        if fvu_options:
                            current_code = pneu.get("codigo_fvu", "")
                            matching_index = 0
                            for idx, opt in enumerate(fvu_options):
                                if opt['codigo'].lower() == current_code.lower():
                                    matching_index = idx
                                    break
                            
                            selected_fvu_label = st.selectbox(
                                f"🔍 Classificação FVU (Ajustar se necessário - Pneu {fogo_num})",
                                options=[f"{x['codigo']} - {x['descricao']}" for x in fvu_options],
                                index=matching_index,
                                key=f"select_fvu_{i}_{fogo_num}_{res['Timestamp']}"
                            )
                            
                            novo_codigo = selected_fvu_label.split(" - ")[0]
                            novo_fvu_obj = next((x for x in fvu_options if x['codigo'].lower() == novo_codigo.lower()), None)
                            
                            if novo_fvu_obj:
                                pneu_exibicao["codigo_fvu"] = novo_fvu_obj['codigo']
                                pneu_exibicao["danos"] = novo_fvu_obj['descricao']
                                pneu_exibicao["causas_provaveis"] = novo_fvu_obj['causa']
                                pneu_exibicao["observacoes"] = novo_fvu_obj['acao']
                                pneu_exibicao["acao_recomendada"] = novo_fvu_obj['acao']

                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"**POS:** {pneu_exibicao.get('pos', '')}")
                            st.write(f"**VEÍCULO:** {pneu_exibicao.get('veiculo', '')}")
                            st.write(f"**MEDIDA:** {pneu_exibicao.get('medida', '')}")
                            st.write(f"**RETIRADA:** {pneu_exibicao.get('retirada', '')}")
                            st.write(f"**Nº REFORMAS:** {pneu_exibicao.get('n_reformas', '')}")
                        with c2:
                            st.write(f"**LOCAL/UNIDADE:** {pneu_exibicao.get('local', '')}")
                            st.write(f"**KM POS:** {pneu_exibicao.get('km_pos', '')}")
                            st.write(f"**KM TOTAL:** {pneu_exibicao.get('km_total', '')}")
                            st.write(f"**Confiança IA:** {pneu_exibicao.get('confianca', '')}")

                        st.write(f"**Laudo / Dano Relatado:** {pneu_exibicao.get('danos', '')}")
                        st.write(f"**Causas Prováveis:** {pneu_exibicao.get('causas_provaveis', '')}")
                        st.write(f"**Observações / Ação:** {pneu_exibicao.get('observacoes', '')}")

                        pdf_pneu_bytes = gerar_pdf_em_cache(pneu_exibicao, res["Timestamp"].split()[0])
                        st.download_button(
                            label=f"📄 Baixar PDF - Pneu {fogo_num}",
                            data=pdf_pneu_bytes,
                            file_name=f"laudo_pneu_{fogo_num}.pdf",
                            mime="application/pdf",
                            key=f"btn_pdf_pneu_{fogo_num}_{i}_{res['Timestamp']}"
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
