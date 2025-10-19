import pandas as pd
import os

def separar_abas_para_arquivos(arquivo_original, pasta_destino=None):
    """
    Separa cada aba de uma planilha Excel em arquivos individuais.
    
    Args:
        arquivo_original (str): Caminho para o arquivo Excel original
        pasta_destino (str): Pasta onde os arquivos serão salvos (opcional)
    """
    
    # Se não for especificada uma pasta de destino, usa a mesma pasta do arquivo original
    if pasta_destino is None:
        pasta_destino = os.path.dirname(arquivo_original)
    
    # Garante que a pasta de destino existe
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lê o arquivo Excel
    try:
        # Lê todas as abas
        planilha = pd.ExcelFile(arquivo_original)
        abas = planilha.sheet_names
        
        print(f"Encontradas {len(abas)} abas no arquivo: {arquivo_original}")
        
        # Processa cada aba
        for aba in abas:
            # Lê os dados da aba
            df = pd.read_excel(arquivo_original, sheet_name=aba)
            
            # Cria o nome do arquivo de saída
            nome_base = os.path.splitext(os.path.basename(arquivo_original))[0]
            nome_arquivo_saida = f"{nome_base}_{aba}.xlsx"
            caminho_completo = os.path.join(pasta_destino, nome_arquivo_saida)
            
            # Salva a aba como arquivo separado
            df.to_excel(caminho_completo, index=False, sheet_name=aba)
            
            print(f"✓ Aba '{aba}' salva como: {nome_arquivo_saida}")
            
        print(f"\nProcesso concluído! Arquivos salvos em: {pasta_destino}")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_original}' não encontrado.")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

# Versão alternativa que retorna os DataFrames (se você quiser trabalhar com eles)
def separar_abas_em_dataframes(arquivo_original):
    """
    Separa cada aba em DataFrames individuais e retorna um dicionário.
    
    Args:
        arquivo_original (str): Caminho para o arquivo Excel original
    
    Returns:
        dict: Dicionário com nome_da_aba: DataFrame
    """
    try:
        # Lê todas as abas em um dicionário de DataFrames
        dataframes = pd.read_excel(arquivo_original, sheet_name=None)
        
        print(f"Abas carregadas: {list(dataframes.keys())}")
        return dataframes
        
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return {}

# Exemplo de uso
if __name__ == "__main__":
    # Configurações
    arquivo_excel = "tabela.xlsx"  # Substitua pelo caminho do seu arquivo
    pasta_saida = "planilhas_separadas"       # Pasta onde salvar os arquivos
    
    # Opção 1: Separar em arquivos individuais
    separar_abas_para_arquivos(arquivo_excel, pasta_saida)
    
    # Opção 2: Carregar em DataFrames (se quiser processar os dados)
    # dataframes = separar_abas_em_dataframes(arquivo_excel)
    # for nome_aba, df in dataframes.items():
    #     print(f"Aba: {nome_aba}, Dimensões: {df.shape}")
