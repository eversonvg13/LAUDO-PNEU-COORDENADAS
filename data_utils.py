import openpyxl
import streamlit as st

def salvar_no_onedrive(dados_ia):
    """
    Salva os dados mapeados diretamente na planilha Excel local do projeto,
    na aba 'TabelaPneus' (ou na aba ativa caso não exista).
    """
    try:
        caminho_arquivo = "Laudos de Pneus Romulo.xlsx"
        
        # Carrega a planilha existente no projeto
        wb = openpyxl.load_workbook(caminho_arquivo)
        
        # Seleciona a aba onde os laudos são salvos
        if "TabelaPneus" in wb.sheetnames:
            ws = wb["TabelaPneus"]
        else:
            ws = wb.active  # Pega a aba ativa caso o nome seja diferente
            
        # Mapeamento rigoroso na ordem exata das 27 colunas
        linha_para_excel = [
            '',                                 # 1. LAUDO Nº (Fórmula)
            dados_ia.get('fogo', ''),           # 2. FOGO
            dados_ia.get('cod_medida', ''),     # 3. COD. MEDIDA
            dados_ia.get('medida', ''),         # 4. MEDIDA
            dados_ia.get('veiculo', ''),        # 5. VEÍCULO
            dados_ia.get('posicao', ''),        # 6. POSIÇÃO
            dados_ia.get('cod_unidade', ''),    # 7. COD.UNIDADE
            '',                                 # 8. UNIDADE (Fórmula PROCV)
            dados_ia.get('data_retirada', ''),  # 9. DATA DE RETIRADA
            dados_ia.get('analise', ''),        # 10. ANÁLISE
            dados_ia.get('nr_ref', ''),         # 11. Nº REF.
            dados_ia.get('km_posicao', ''),     # 12. KM POSIÇÃO
            dados_ia.get('km_total', ''),       # 13. KM TOTAL
            dados_ia.get('valor', ''),          # 14. VALOR
            '',                                 # 15. STATUS (Fórmula)
            dados_ia.get('retorno', ''),        # 16. RETORNO
            dados_ia.get('desconto', ''),       # 17. DESCONTO
            dados_ia.get('fvu', ''),            # 18. FVU
            '',                                 # 19. DANOS CAUSADOS (Fórmula)
            '',                                 # 20. CAUSAS PROVAVEIS (Fórmula)
            '',                                 # 21. COMPLEMENTO (Fórmula)
            dados_ia.get('cod_relator', ''),    # 22. COD.RELATOR
            '',                                 # 23. RELATOR (Fórmula)
            '',                                 # 24. MÊS (Fórmula)
            '',                                 # 25. DIAS PENDENTE (Fórmula)
            '',                                 # 26. CATEGORIA (Fórmula)
            ''                                  # 27. ANO (Fórmula)
        ]
        
        # Adiciona a nova linha logo abaixo dos dados existentes
        ws.append(linha_para_excel)
        
        # Salva as alterações no arquivo local
        wb.save(caminho_arquivo)
        
        return True, "Laudo salvo com sucesso na planilha local!"
        
    except Exception as e:
        return False, f"Erro ao salvar localmente no arquivo Excel: {str(e)}"
