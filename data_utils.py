import requests
import streamlit as st

WEBHOOK_URL = "https://hook.us2.make.com/cbfm6m6pmbcpzuwfssj24e3427vi4fh3"

def salvar_no_onedrive(dados_ia):
    try:
        payload = {
            "fogo":         dados_ia.get("fogo", ""),
            "cod_medida":   dados_ia.get("cod_medida", ""),
            "medida":       dados_ia.get("medida", ""),
            "veiculo":      dados_ia.get("veiculo", ""),
            "posicao":      dados_ia.get("posicao", ""),
            "cod_unidade":  dados_ia.get("cod_unidade", ""),
            "data_retirada":dados_ia.get("data_retirada", ""),
            "analise":      dados_ia.get("analise", ""),
            "nr_ref":       dados_ia.get("nr_ref", ""),
            "km_posicao":   dados_ia.get("km_posicao", ""),
            "km_total":     dados_ia.get("km_total", ""),
            "valor":        dados_ia.get("valor", ""),
            "retorno":      dados_ia.get("retorno", ""),
            "desconto":     dados_ia.get("desconto", ""),
            "fvu":          dados_ia.get("fvu", ""),
            "cod_relator":  dados_ia.get("cod_relator", ""),
        }

        response = requests.post(WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            return True, "Laudo salvo com sucesso na planilha!"
        else:
            return False, f"Erro ao enviar para o Make: {response.status_code}"

    except Exception as e:
        return False, f"Erro na requisição: {str(e)}"
