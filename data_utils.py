import msal
import requests
import streamlit as st

def obter_token():
    """Autentica no Azure AD e retorna o Token de Acesso"""
    app = msal.ConfidentialClientApplication(
        st.secrets["AZURE_CLIENT_ID"],
        authority=f"https://login.microsoftonline.com/{st.secrets['AZURE_TENANT_ID']}",
        client_credential=st.secrets["AZURE_CLIENT_SECRET"]
    )
    token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token_response.get("access_token")

def salvar_no_onedrive(dados_ia):
    """
    Envia os dados mapeados na ordem exata das 27 colunas para a tabela do OneDrive,
    deixando as colunas com fórmulas em branco para que o Excel preencha automaticamente.
    """
    token = obter_token()
    if not token:
        return False, "Falha na autenticação com a Microsoft."
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # ID do arquivo extraído do OneDrive
    file_id = "710AD0E3-83C9-473B-9A9B-255724AAA15C"
    
    # URL da API Graph para a tabela 'TabelaPneus'
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/workbook/tables/TabelaPneus/rows"
    
    # Mapeamento rigoroso na ordem exata das 27 colunas
    linha_para_excel = [
        '',                                # 1. LAUDO Nº (Fórmula)
        dados_ia.get('fogo', ''),          # 2. FOGO
        dados_ia.get('cod_medida', ''),    # 3. COD. MEDIDA
        dados_ia.get('medida', ''),        # 4. MEDIDA
        dados_ia.get('veiculo', ''),       # 5. VEÍCULO
        dados_ia.get('posicao', ''),       # 6. POSIÇÃO
        dados_ia.get('cod_unidade', ''),   # 7. COD.UNIDADE
        '',                                # 8. UNIDADE (Fórmula PROCV)
        dados_ia.get('data_retirada', ''), # 9. DATA DE RETIRADA
        dados_ia.get('analise', ''),       # 10. ANÁLISE
        dados_ia.get('nr_ref', ''),        # 11. Nº REF.
        dados_ia.get('km_posicao', ''),    # 12. KM POSIÇÃO
        dados_ia.get('km_total', ''),      # 13. KM TOTAL
        dados_ia.get('valor', ''),         # 14. VALOR
        '',                                # 15. STATUS (Fórmula)
        dados_ia.get('retorno', ''),       # 16. RETORNO
        dados_ia.get('desconto', ''),      # 17. DESCONTO
        dados_ia.get('fvu', ''),           # 18. FVU
        '',                                # 19. DANOS CAUSADOS (Fórmula)
        '',                                # 20. CAUSAS PROVAVEIS (Fórmula)
        '',                                # 21. COMPLEMENTO (Fórmula)
        dados_ia.get('cod_relator', ''),   # 22. COD.RELATOR
        '',                                # 23. RELATOR (Fórmula)
        '',                                # 24. MÊS (Fórmula)
        '',                                # 25. DIAS PENDENTE (Fórmula)
        '',                                # 26. CATEGORIA (Fórmula)
        ''                                 # 27. ANO (Fórmula)
    ]
    
    payload = {
        "values": [linha_para_excel]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        return True, "Laudo salvo com sucesso no OneDrive!"
    else:
        return False, f"Erro ao salvar na API ({response.status_code}): {response.text}"
