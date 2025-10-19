from flask import Flask, jsonify, request
import pandas as pd
import pyarrow.parquet as pq
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
ALLOWED_EXTENSIONS = ['xlsx', 'xls']
UPLOAD_FOLDER = 'uploads'

@app.route('/planilhas-processar', methods=['POST'])
def processar_planilhas():
    try:
        if 'arquivo' not in request.files:
            return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['arquivo']
        
        if file.filename == '':
            return jsonify({'erro': 'Nome de arquivo vazio'}), 400
        
        if not file.filename.endswith('.xlsx'):
            return jsonify({'erro': 'Tipo de arquivo não permitido'}), 400
        
        filename = secure_filename(file.filename)
        
        if not filename:
            return jsonify({'erro': 'Nome de arquivo inválido'}), 400
        
        df = pd.read_excel(file)
        print(df.head())
        
        return jsonify({'mensagem': 'Planilhas recebidas com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/dados-parquet', methods=['GET'])
def ler_parquet_para_json():
    try:
        # Caminho para o arquivo parquet
        arquivo_parquet = 'estoque.parquet'
        
        # Verifica se o arquivo existe
        if not os.path.exists(arquivo_parquet):
            return jsonify({'erro': f'Arquivo {arquivo_parquet} não encontrado'}), 404
        
        # Lê o arquivo parquet usando pandas
        df = pd.read_parquet(arquivo_parquet)
        
        # Converte para JSON
        # 'orient='records'' cria uma lista de objetos
        dados_json = df.to_json(orient='records', date_format='iso')
        
        # Retorna os dados como JSON
        # jsonify garante que o Content-Type seja application/json
        return jsonify(dados_json)
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao processar arquivo: {str(e)}'}), 500

# Versão alternativa usando pyarrow diretamente
@app.route('/dados-parquet-arrow', methods=['GET'])
def ler_parquet_pyarrow():
    try:
        arquivo_parquet = 'estoque.parquet'
        
        if not os.path.exists(arquivo_parquet):
            return jsonify({'erro': f'Arquivo {arquivo_parquet} não encontrado'}), 404
        
        # Lê o arquivo com pyarrow
        tabela = pq.read_table(arquivo_parquet)
        
        # Converte para pandas e depois para JSON
        df = tabela.to_pandas()
        dados_json = df.to_json(orient='records', date_format='iso')
        
        return jsonify(dados_json)
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao processar arquivo: {str(e)}'}), 500

# Endpoint com parâmetro para nome do arquivo
@app.route('/dados-parquet/<nome_arquivo>', methods=['GET'])
def ler_parquet_especifico(nome_arquivo):
    try:
        arquivo_parquet = f'{nome_arquivo}.parquet'
        
        if not os.path.exists(arquivo_parquet):
            return jsonify({'erro': f'Arquivo {arquivo_parquet} não encontrado'}), 404
        
        df = pd.read_parquet(arquivo_parquet)
        dados_json = df.to_json(orient='records', date_format='iso')
        
        return jsonify(dados_json)
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao processar arquivo: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
