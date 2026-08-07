import requests
from datetime import datetime

WEBHOOK_URL = "https://hook.us2.make.com/cbfm6m6pmbcpzuwfssj24e3427vi4fh3"

COD_UNIDADE = {
    "ANA LUCIA":     "98",
    "JUSTINOPOLES":  "870",
    "LAFAIETE":      "250",
    "MARIA GORETTI": "16",
    "NEVES":         "520",
    "SARZEDO":       "61",
    "UBERLANDIA":    "6",
    "VENEZA":        "990",
}

COD_RELATOR = "16196"

def limpar_km(valor):
    try:
        return str(valor).replace(".", ",").strip()
    except:
        return ""

def separar_medida(medida_completa):
    try:
        partes = str(medida_completa).split("-", 1)
        if len(partes) == 2:
            return partes[0].strip(), partes[1].strip()
        return "", medida_completa
    except:
        return "", medida_completa

def salvar_no_onedrive(dados_ia):
    try:
        medida_completa = dados_ia.get("medida", "")
        cod_medida, medida = separar_medida(medida_completa)

        local = dados_ia.get("local", "").strip().upper()
        cod_unidade = COD_UNIDADE.get(local, "")

        payload = {
            "fogo":         dados_ia.get("fogo", ""),
            "cod_medida":   cod_medida,
            "medida":       medida,
            "veiculo":      dados_ia.get("veiculo", ""),
            "posicao":      dados_ia.get("pos", ""),
            "cod_unidade":  cod_unidade,
            "data_retirada":dados_ia.get("retirada", ""),
            "analise":      datetime.now().strftime("%d/%m/%Y"),
            "nr_ref":       dados_ia.get("n_reformas", ""),
            "km_posicao":   limpar_km(dados_ia.get("km_pos", "")),
            "km_total":     limpar_km(dados_ia.get("km_total", "")),
            "valor":        dados_ia.get("valor", ""),
            "retorno":      dados_ia.get("retorno", ""),
            "desconto":     dados_ia.get("desconto", ""),
            "fvu":          dados_ia.get("codigo_fvu", ""),
            "cod_relator":  COD_RELATOR,
        }

        response = requests.post(WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            return True, "Laudo salvo com sucesso na planilha!"
        else:
            return False, f"Erro ao enviar para o Make: {response.status_code}"

    except Exception as e:
        return False, f"Erro na requisição: {str(e)}"
