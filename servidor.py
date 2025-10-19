from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from flask_cors import CORS
from conversor import run
import pandas as pd

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
ALLOWED_EXTENSIONS = ['xlsx', 'xls']
UPLOAD_FOLDER = 'uploads'
CORS(app)

@app.route('/importar', methods=['POST'])
def processar_planilhas():
    try:
        print(request.files)
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
        
        run(file)
        
        return jsonify({'mensagem': 'Planilhas recebidas com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/estoque', methods=['GET'])
def obter_estoque():
    try:
        df = pd.read_parquet('estoque.parquet', engine='pyarrow')
        dados_json = df.to_dict(orient='records')
        return jsonify(dados_json), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/tabela', methods=['GET'])
def obter_tabela():
    try:
        df = pd.read_parquet('tabela.parquet', engine='pyarrow')
        dados_json = df.to_dict(orient='records')
        return jsonify(dados_json), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
