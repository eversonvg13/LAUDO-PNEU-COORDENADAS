# data_utils.py
import openpyxl
import os

def salvar_no_excel(caminho_arquivo, dados_ia):
    """
    Função modular para salvar dados no Excel mantendo as fórmulas.
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            return False, "Arquivo não encontrado."

        # Carrega o arquivo
        wb = openpyxl.load_workbook(caminho_arquivo, data_only=False)
        ws = wb['Dados'] # Nome da aba
        
        # Encontra a próxima linha vazia
        proxima_linha = ws.max_row + 1
        
        # Preenchimento (ajuste os campos conforme o seu JSON)
        ws.cell(row=proxima_linha, column=1).value = dados_ia.get('id_pneu')
        ws.cell(row=proxima_linha, column=2).value = dados_ia.get('codigo_fvu')
        ws.cell(row=proxima_linha, column=3).value = dados_ia.get('observacoes')
        
        # Salva o arquivo
        wb.save(caminho_arquivo)
        return True, "Sucesso!"
        
    except Exception as e:
        return False, str(e)