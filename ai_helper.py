import io
import re
import json
import difflib
from PIL import Image


def comprimir_imagem(file_bytes, max_dim=1024, qualidade=80):
    img = Image.open(io.BytesIO(file_bytes))
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=qualidade, optimize=True)
    return buffer.getvalue()


def obter_modelo_estavel(genai):
    modelos_homologados = [
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
    ]
    prefixos_descontinuados = ("gemini-1.", "gemini-2.0", "gemini-2.5")

    try:
        modelos_disponiveis = [
            m.name.replace('models/', '')
            for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
        modelos_validos = [m for m in modelos_disponiveis if not m.startswith(prefixos_descontinuados)]

        for h in modelos_homologados:
            if h in modelos_validos:
                return h
        for m in modelos_validos:
            if 'flash' in m:
                return m
        if modelos_validos:
            return modelos_validos[0]
    except Exception:
        pass

    return "gemini-flash-latest"


def buscar_dados_relatorio(fogo_lido, df):
    if df is None or df.empty or not fogo_lido:
        return None

    fogo_lido = str(fogo_lido).strip()
    fogo_lido_norm = fogo_lido.lstrip("0") or "0"

    fogos_tabela = df["FOGO"].astype(str).str.strip()

    match = df[fogos_tabela == fogo_lido]
    if match.empty:
        match = df[fogos_tabela.str.lstrip("0").replace("", "0") == fogo_lido_norm]

    if match.empty:
        return None
    return match.iloc[0].to_dict()


def extrair_json_da_resposta(texto):
    texto_limpo = texto.strip()
    texto_limpo = re.sub(r"^```json", "", texto_limpo.strip())
    texto_limpo = re.sub(r"^```", "", texto_limpo.strip())
    texto_limpo = re.sub(r"```$", "", texto_limpo.strip())

    inicio = texto_limpo.find("[")
    fim = texto_limpo.rfind("]")
    if inicio == -1 or fim == -1:
        raise ValueError("Nenhum array JSON encontrado na resposta da IA.")

    return json.loads(texto_limpo[inicio:fim + 1])


def encontrar_fvu_por_descricao(descricao_ia, fvu_data, limiar=0.35):
    """
    Usada como fallback quando o código FVU sugerido pela IA não bate
    exatamente com nenhum código da tabela. Busca, entre os registros
    de fvu_data, aquele cuja DESCRIÇÃO mais se aproxima textualmente
    da descrição do dano fornecida pela IA (descricao_dano_ia).
    Retorna o dict do item mais parecido, ou None se nada ultrapassar
    o limiar mínimo de similaridade.
    """
    if not descricao_ia or not fvu_data:
        return None

    texto_ia = str(descricao_ia).strip().lower()
    if not texto_ia:
        return None

    melhor_item = None
    melhor_score = 0.0

    for item in fvu_data:
        desc_item = str(item.get("descricao", "")).strip().lower()
        if not desc_item:
            continue
        score = difflib.SequenceMatcher(None, texto_ia, desc_item).ratio()
        if score > melhor_score:
            melhor_score = score
            melhor_item = item

    if melhor_item is not None and melhor_score >= limiar:
        return melhor_item
    return None
