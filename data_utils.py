import msal
import requests
import streamlit as st

def obter_token():
    # O Streamlit busca automaticamente os dados que salvamos nos Secrets
    app = msal.ConfidentialClientApplication(
        st.secrets["AZURE_CLIENT_ID"],
        authority=f"https://login.microsoftonline.com/{st.secrets['AZURE_TENANT_ID']}",
        client_credential=st.secrets["AZURE_CLIENT_SECRET"]
    )
    # Solicita o token de permissão de aplicativo
    token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token_response.get("access_token")

def salvar_no_onedrive(id_pneu, codigo_fvu, observacoes):
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # IMPORTANTE: Você precisa do ID do arquivo (driveItem ID)
    # Dica: Rode um teste simples para listar seus arquivos se não souber o ID exato
    file_id = "SEU_FILE_ID_AQUI" 
    
    # Endpoint para adicionar linha a uma tabela chamada 'TabelaPneus'
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/workbook/tables/TabelaPneus/rows"
    
    payload = {"values": [[id_pneu, codigo_fvu, observacoes]]}
    
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 201
