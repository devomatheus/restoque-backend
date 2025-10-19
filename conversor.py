
import pandas as pd
import logging
import sys
from time import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def validar_dataframe(df, colunas_obrigatorias, nome):
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"O objeto '{nome}' não é um DataFrame.")
    for coluna in colunas_obrigatorias:
        if coluna not in df.columns:
            raise ValueError(f"Coluna obrigatória '{coluna}' ausente em '{nome}'.")

def run(arquivo):
    try:
        logging.info("Lendo as colunas necessárias das planilhas...")

        df_tabela = pd.read_excel(arquivo, sheet_name='Tabela', engine='openpyxl')
        df_estoque = pd.read_excel(arquivo, sheet_name='Estoque', engine='openpyxl')

        logging.info("Validando DataFrames...")
        validar_dataframe(df_tabela, ['EAN'], 'Tabela')
        validar_dataframe(df_estoque, ['EAN', 'Estoque Disponivel'], 'Estoque')

        logging.info("Criando mapeamento de EAN para estoque...")
        mapeamento_estoque = df_estoque.set_index('EAN')['Estoque Disponivel'].to_dict()

        logging.info("Atualizando coluna 'Estoque' na tabela principal...")
        df_tabela['Estoque'] = df_tabela['EAN'].map(mapeamento_estoque).fillna(0)
        if not pd.api.types.is_numeric_dtype(df_tabela['Estoque']):
            logging.warning("Coluna 'Estoque' não é numérica. Convertendo para inteiro.")
        df_tabela['Estoque'] = df_tabela['Estoque'].astype(int)
        
        logging.info("Salvando resultado em parquets...")
        df_estoque.to_parquet('estoque.parquet', engine='pyarrow', compression='snappy')
        df_tabela.to_parquet('tabela.parquet', engine='pyarrow', compression='snappy')

        logging.info("Processamento concluído! Arquivos criado.")
    except FileNotFoundError as e:
        logging.error(f"Arquivo não encontrado: {e.filename}")
    except ValueError as e:
        logging.error(f"Erro de valor: {e}")
    except TypeError as e:
        logging.error(f"Erro de tipo: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}", exc_info=True)
