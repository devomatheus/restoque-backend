import pandas as pd
import numpy as np
from datetime import datetime, date
import re

def analisar_tipo_coluna(serie):
    """
    Analisa uma série do pandas e retorna o tipo mais apropriado
    """
    # Remove valores nulos para análise
    serie_sem_nulos = serie.dropna()
    
    if len(serie_sem_nulos) == 0:
        return "VAZIO", 0
    
    # Contador para estatísticas
    total_valores = len(serie_sem_nulos)
    
    # Tentar identificar datas
    contador_data = 0
    contador_hora = 0
    contador_inteiro = 0
    contador_decimal = 0
    contador_string = 0
    contador_booleano = 0
    
    for valor in serie_sem_nulos:
        # Verificar se já é datetime do pandas
        if pd.api.types.is_datetime64_any_dtype(serie_sem_nulos):
            if pd.notna(valor):
                if valor.time() == datetime.min.time():
                    contador_data += 1
                else:
                    contador_hora += 1
            continue
        
        # Converter para string para análise
        str_valor = str(valor).strip()
        
        # Verificar booleano
        if str_valor.lower() in ['true', 'false', 'verdadeiro', 'falso', 'sim', 'não', 'yes', 'no', '1', '0']:
            contador_booleano += 1
        
        # Verificar inteiro
        elif re.match(r'^-?\d+$', str_valor):
            contador_inteiro += 1
        
        # Verificar decimal
        elif re.match(r'^-?\d+[,.]\d+$', str_valor.replace(',', '.')):
            contador_decimal += 1
        
        # Verificar datas e horas
        else:
            # Padrões comuns de data
            padroes_data = [
                r'^\d{1,2}/\d{1,2}/\d{4}$',  # DD/MM/AAAA
                r'^\d{4}-\d{1,2}-\d{1,2}$',  # AAAA-MM-DD
                r'^\d{1,2}-\d{1,2}-\d{4}$',  # DD-MM-AAAA
                r'^\d{1,2}\.\d{1,2}\.\d{4}$', # DD.MM.AAAA
            ]
            
            # Padrões comuns de hora
            padroes_hora = [
                r'^\d{1,2}:\d{2}(:\d{2})?$',  # HH:MM ou HH:MM:SS
                r'^\d{1,2}:\d{2}(:\d{2})?[AP]M$',  # HH:MM AM/PM
            ]
            
            # Padrões combinados data+hora
            padroes_data_hora = [
                r'^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}',
                r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2}',
            ]
            
            eh_data = any(re.match(padrao, str_valor) for padrao in padroes_data)
            eh_hora = any(re.match(padrao, str_valor) for padrao in padroes_hora)
            eh_data_hora = any(re.match(padrao, str_valor) for padrao in padroes_data_hora)
            
            if eh_data_hora:
                contador_hora += 1
            elif eh_data:
                contador_data += 1
            elif eh_hora:
                contador_hora += 1
            else:
                contador_string += 1
    
    # Determinar o tipo predominante
    tipos = {
        'INTEIRO': contador_inteiro / total_valores,
        'DECIMAL': contador_decimal / total_valores,
        'DATA': contador_data / total_valores,
        'HORA': contador_hora / total_valores,
        'BOOLEANO': contador_booleano / total_valores,
        'STRING': contador_string / total_valores
    }
    
    tipo_principal = max(tipos, key=tipos.get)
    percentual = tipos[tipo_principal] * 100
    
    return tipo_principal, percentual

def analisar_excel(arquivo_excel, planilha=0):
    """
    Analisa um arquivo Excel e retorna os tipos de dados de cada coluna
    """
    try:
        # Ler o arquivo Excel
        df = pd.read_excel(arquivo_excel, sheet_name=planilha)
        
        print(f"Arquivo: {arquivo_excel}")
        print(f"Planilha: {planilha if isinstance(planilha, int) else planilha}")
        print(f"Total de linhas: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        print("\n" + "="*80)
        
        resultados = []
        
        for coluna in df.columns:
            serie = df[coluna]
            tipo_detectado, confianca = analisar_tipo_coluna(serie)
            
            # Estatísticas da coluna
            nulos = serie.isna().sum()
            percentual_nulos = (nulos / len(serie)) * 100
            valores_unicos = serie.nunique()
            
            resultados.append({
                'Coluna': coluna,
                'Tipo_Detectado': tipo_detectado,
                'Confiança (%)': round(confianca, 2),
                'Valores_Únicos': valores_unicos,
                'Valores_Nulos': nulos,
                '%_Nulos': round(percentual_nulos, 2),
                'Tipo_Pandas': str(serie.dtype)
            })
            
            # Exibir resultados formatados
            print(f"Coluna: {coluna}")
            print(f"  → Tipo detectado: {tipo_detectado}")
            print(f"  → Confiança: {confianca:.2f}%")
            print(f"  → Valores únicos: {valores_unicos}")
            print(f"  → Valores nulos: {nulos} ({percentual_nulos:.2f}%)")
            print(f"  → Tipo no pandas: {serie.dtype}")
            print(f"  → Amostra de valores: {list(serie.dropna().head(3).values)}")
            print("-" * 50)
        
        return pd.DataFrame(resultados)
        
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

def gerar_relatorio_detalhado(df_resultados):
    """
    Gera um relatório detalhado da análise
    """
    if df_resultados is None:
        return
    
    print("\n" + "="*80)
    print("RELATÓRIO RESUMIDO")
    print("="*80)
    
    # Estatísticas gerais
    total_colunas = len(df_resultados)
    tipos_contagem = df_resultados['Tipo_Detectado'].value_counts()
    
    print(f"\nDistribuição de tipos:")
    for tipo, count in tipos_contagem.items():
        percentual = (count / total_colunas) * 100
        print(f"  {tipo}: {count} colunas ({percentual:.1f}%)")
    
    # Colunas com muitos nulos
    colunas_problematicas = df_resultados[df_resultados['%_Nulos'] > 50]
    if len(colunas_problematicas) > 0:
        print(f"\nColunas com mais de 50% de valores nulos:")
        for _, coluna in colunas_problematicas.iterrows():
            print(f"  {coluna['Coluna']}: {coluna['%_Nulos']}% nulos")

# Exemplo de uso
if __name__ == "__main__":
    # Substitua pelo caminho do seu arquivo Excel
    arquivo_excel = "tabela.xlsx"  # Altere para o caminho do seu arquivo
    
    # Analisar o arquivo
    resultados = analisar_excel(arquivo_excel)
    
    # Gerar relatório
    if resultados is not None:
        gerar_relatorio_detalhado(resultados)
        
        # Salvar resultados em CSV
        resultados.to_csv('analise_tipos_dados.csv', index=False, encoding='utf-8-sig')
        print(f"\nResultados salvos em 'analise_tipos_dados.csv'")
