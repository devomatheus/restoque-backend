import pandas as pd
from time import time

import sqlite3
from typing import List, Tuple, Any, Optional, Union

class SQLiteCRUD:
    def __init__(self, db_path: str = "database.db"):
        """
        Inicializa a conexão com o banco de dados SQLite
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self) -> None:
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Para retornar dicionários
            print(f"Conexão com {self.db_path} estabelecida com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao conectar com o banco de dados: {e}")
    
    def execute_query(self, query: str, params: Tuple = ()) -> Optional[List[dict]]:
        """
        Executa uma query genérica no banco de dados
        
        Args:
            query (str): Query SQL a ser executada
            params (Tuple): Parâmetros para a query
            
        Returns:
            Optional[List[dict]]: Resultado da consulta ou None para operações sem retorno
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            # Se for SELECT, retorna os resultados
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                # Para INSERT, UPDATE, DELETE - faz commit
                self.connection.commit()
                return None
                
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
            self.connection.rollback()
            return None
    
    def create_table(self, table_name: str, columns: dict) -> bool:
        """
        Cria uma tabela no banco de dados
        
        Args:
            table_name (str): Nome da tabela
            columns (dict): Dicionário com nome: tipo das colunas
            
        Returns:
            bool: True se sucesso, False se erro
        """
        columns_def = ", ".join([f"{col_name} {col_type}" 
                               for col_name, col_type in columns.items()])
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        result = self.execute_query(query)
        return result is None  # Retorna True se não houve erro
    
    def insert(self, table_name: str, data: dict) -> bool:
        """
        Insere um registro na tabela
        
        Args:
            table_name (str): Nome da tabela
            data (dict): Dicionário com coluna: valor
            
        Returns:
            bool: True se sucesso, False se erro
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        result = self.execute_query(query, tuple(data.values()))
        return result is None
    
    def select(self, table_name: str, where: str = None, 
               params: Tuple = (), columns: str = "*") -> Optional[List[dict]]:
        """
        Seleciona registros da tabela
        
        Args:
            table_name (str): Nome da tabela
            where (str): Condição WHERE (opcional)
            params (Tuple): Parâmetros para a condição WHERE
            columns (str): Colunas a selecionar (padrão: *)
            
        Returns:
            Optional[List[dict]]: Lista de registros ou None se erro
        """
        query = f"SELECT {columns} FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        
        return self.execute_query(query, params)
    
    def select_one(self, table_name: str, where: str = None, 
                  params: Tuple = (), columns: str = "*") -> Optional[dict]:
        """
        Seleciona um único registro da tabela
        
        Args:
            table_name (str): Nome da tabela
            where (str): Condição WHERE (opcional)
            params (Tuple): Parâmetros para a condição WHERE
            columns (str): Colunas a selecionar (padrão: *)
            
        Returns:
            Optional[dict]: Um registro ou None se não encontrado
        """
        results = self.select(table_name, where, params, columns)
        return results[0] if results else None
    
    def update(self, table_name: str, data: dict, 
              where: str, params: Tuple = ()) -> bool:
        """
        Atualiza registros na tabela
        
        Args:
            table_name (str): Nome da tabela
            data (dict): Dicionário com coluna: valor para atualizar
            where (str): Condição WHERE
            params (Tuple): Parâmetros para a condição WHERE
            
        Returns:
            bool: True se sucesso, False se erro
        """
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
        
        # Combina os valores de data com os parâmetros do WHERE
        all_params = tuple(data.values()) + params
        
        result = self.execute_query(query, all_params)
        return result is None
    
    def delete(self, table_name: str, where: str, params: Tuple = ()) -> bool:
        """
        Deleta registros da tabela
        
        Args:
            table_name (str): Nome da tabela
            where (str): Condição WHERE
            params (Tuple): Parâmetros para a condição WHERE
            
        Returns:
            bool: True se sucesso, False se erro
        """
        query = f"DELETE FROM {table_name} WHERE {where}"
        result = self.execute_query(query, params)
        return result is None
    
    def close(self) -> None:
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            print("Conexão fechada!")
    
    def __enter__(self):
        """Suporte para context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão ao sair do context manager"""
        self.close()


alias = {
    'Cód. Fornecedor': 'cod_fornecedor',
    'Fornecedor': 'fornecedor',
    'Cód. Produto': 'cod_produto', 
    'Produto': 'produto', 
    'EAN': 'ean', 
    'Categoria': 'categoria', 
    'Estoque em Andamento': 'estoque_andamento', 
    'Estoque Existente': 'estoque_existente', 
    'Estoque Disponivel': 'estoque_disponivel', 
    'Codigo': 'codigo',  
    'Descrição': 'descricao', 
    'Preço Base': 'preco_base', 
    'Desconto': 'desconto', 
    'ST': 'st', 
    'Preço Final': 'preco_final', 
    'Estoque': 'estoque'
}

input_file = "tabela.xlsx"
# pd.set_option('display.max_columns', None)

# t1 = time()
# df = pd.read_excel(
#     "tabela.xlsx", 
#     engine="openpyxl",
#     sheet_name=[0,1]
# )
# print(time() - t1)

# print(df)

# abas = pd.ExcelFile("tabela.xlsx", engine="openpyxl").sheet_names

# df = pd.read_excel(
#     input_file,
#     engine="openpyxl",
#     sheet_name=abas
# )

# print(df)



arquivo = "seuarquivo.xlsx"
xls = pd.ExcelFile(input_file)


print("Abas encontradas:", xls.sheet_names)
colunas_encontradas = []

for aba in xls.sheet_names:
    df = pd.read_excel(input_file, sheet_name=aba, nrows=0)
    #print(f"\nAba: {aba}")
    #print(df.columns.tolist())
    colunas_encontradas.extend(df.columns.tolist())
    

    # criar as colunas na tabela
    # with SQLiteCRUD("meubanco.db") as db:
        
print(colunas_encontradas)
