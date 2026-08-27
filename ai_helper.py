import io
import re
import json
import time
import difflib
import concurrent.futures
from PIL import Image

# Tempo máximo (segundos) que uma chamada individual ao Gemini pode levar
# antes de ser considerada travada e cancelada com erro. Sem isso, uma
# conexão presa (comum em alguns ambientes de hospedagem) trava para sempre.
TIMEOUT_SEGUNDOS = 120


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


def montar_lotes(sorted_files, imagens_por_lote):
    """
    Divide a lista de arquivos (já ordenada) em lotes de tamanho fixo,
    preservando a ordem. Cada lote vira UMA chamada separada à IA.

    imagens_por_lote deve ser um múltiplo do nº de fotos que o usuário tira
    por pneu (normalmente 2), para não correr o risco de separar as fotos de
    um mesmo pneu em dois lotes diferentes.
    """
    imagens_por_lote = max(1, imagens_por_lote)
    return [
        sorted_files[i:i + imagens_por_lote]
        for i in range(0, len(sorted_files), imagens_por_lote)
    ]


def _chamar_gemini_processo(api_key, nome_modelo, arquivos_batch, prompt_instrucoes):
    """
    Executa UMA chamada ao Gemini para um lote de imagens.

    Roda dentro de um processo separado (via ProcessPoolExecutor). Isso é
    importante porque genai.configure(api_key=...) altera um estado GLOBAL
    do SDK — se dois lotes rodassem em paralelo dentro de THREADS do mesmo
    processo, um poderia sobrescrever a chave do outro no meio da chamada.
    Usando processos separados, cada um tem seu próprio estado do SDK e pode
    usar uma chave de API diferente com segurança, de verdade em paralelo.

    arquivos_batch: lista de tuplas (nome_arquivo, bytes_jpeg_ja_comprimidos)
    Retorna o texto bruto da resposta da IA.
    """
    import google.generativeai as genai_proc

    # transport="rest" em vez do gRPC padrão: em vários ambientes de
    # hospedagem (ex: Streamlit Community Cloud), conexões gRPC ficam
    # travadas silenciosamente (sem erro, sem timeout) quando a rede/proxy
    # do host não lida bem com HTTP/2 de longa duração. REST falha rápido
    # com uma mensagem de erro clara em vez de travar para sempre.
    genai_proc.configure(api_key=api_key, transport="rest")
    model = genai_proc.GenerativeModel(nome_modelo)

    conteudo = []
    for nome, dados in arquivos_batch:
        conteudo.append(f"Arquivo: {nome}")
        conteudo.append({"mime_type": "image/jpeg", "data": dados})
    conteudo.append(prompt_instrucoes)

    # timeout explícito: sem isso, uma conexão travada faz a chamada nunca
    # retornar. Com o timeout, ela levanta uma exceção clara depois de
    # TIMEOUT_SEGUNDOS, que o chamador pode tratar/reportar.
    resposta = model.generate_content(
        conteudo, request_options={"timeout": TIMEOUT_SEGUNDOS}
    )
    return resposta.text


def processar_lotes_em_paralelo(lotes, lista_chaves, nome_modelo, prompt_instrucoes,
                                 max_ciclos=3, callback_status=None):
    """
    Dispara um lote de chamadas ao Gemini em paralelo (um processo por lote,
    até o nº de chaves de API disponíveis) e devolve os textos brutos de
    resposta na MESMA ordem dos lotes de entrada.

    Em caso de erro de cota (429) num lote específico, só aquele lote é
    reenviado com a próxima chave disponível — os demais lotes já concluídos
    não são refeitos.

    Lança RuntimeError se, ao final de max_ciclos, algum lote ainda não
    tiver conseguido resposta em nenhuma chave.
    """
    total_chaves = len(lista_chaves)
    total_lotes = len(lotes)
    resultados = [None] * total_lotes
    pendentes = list(range(total_lotes))
    indice_chave = {i: i % total_chaves for i in pendentes}

    max_workers = max(1, min(total_lotes, total_chaves))

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        for ciclo in range(max_ciclos):
            if not pendentes:
                break

            futuros = {}
            for i in pendentes:
                chave = lista_chaves[indice_chave[i]]
                fut = executor.submit(
                    _chamar_gemini_processo, chave, nome_modelo, lotes[i], prompt_instrucoes
                )
                futuros[fut] = i

            novos_pendentes = []
            try:
                concluidos = concurrent.futures.wait(
                    futuros.keys(), timeout=TIMEOUT_SEGUNDOS + 30
                ).done
            except Exception:
                concluidos = []

            for fut in futuros:
                i = futuros[fut]
                if fut not in concluidos:
                    # Processo não terminou nem com a folga extra de 30s
                    # acima do timeout interno da chamada — trata como falha
                    # deste lote (não deixa o app girando para sempre).
                    fut.cancel()
                    indice_chave[i] = (indice_chave[i] + 1) % total_chaves
                    novos_pendentes.append(i)
                    if callback_status:
                        callback_status(f"⚠️ Lote {i + 1} travou/expirou. Tentando de novo...")
                    continue
                try:
                    resultados[i] = fut.result()
                    if callback_status:
                        callback_status(f"Lote {i + 1}/{total_lotes} concluído ({len(lotes[i])} fotos).")
                except Exception as e:
                    erro_str = str(e)
                    is_quota = "429" in erro_str or "ResourceExhausted" in type(e).__name__ or "quota" in erro_str.lower()
                    if is_quota:
                        indice_chave[i] = (indice_chave[i] + 1) % total_chaves
                        novos_pendentes.append(i)
                        if callback_status:
                            callback_status(f"⚠️ Cota esgotada no lote {i + 1}. Tentando próxima chave...")
                    else:
                        raise RuntimeError(f"Erro no lote {i + 1}: {e}")

            pendentes = novos_pendentes
            if pendentes and ciclo < max_ciclos - 1:
                if callback_status:
                    callback_status(
                        f"⚠️ Aguardando 65s para recarregar cotas ({len(pendentes)} lote(s) pendente(s))..."
                    )
                time.sleep(65)

    if pendentes:
        raise RuntimeError(
            f"Limite de cota excedido para {len(pendentes)} lote(s) de imagens após {max_ciclos} ciclos."
        )

    return resultados
