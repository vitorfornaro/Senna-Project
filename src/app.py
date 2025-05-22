from flask import Flask, request, jsonify
import tempfile
import os
import uuid

from pdf_decryptor import PDFDecryptor
from pdf_text_extractor import PDFTextExtractor
from pdf_data_extractor import PDFDataExtractor
from senninha import Senninha

app = Flask(__name__)

@app.route('/perfilamento', methods=['POST'])
def perfilamento():
    if 'mdr' not in request.files:
        return jsonify({"error": "Arquivo PDF não enviado no campo 'mdr'"}), 400

    arquivo = request.files['mdr']
    filename = f"{uuid.uuid4().hex}.pdf"
    temp_input = os.path.join(tempfile.gettempdir(), filename)

    # Salvar o PDF temporariamente
    arquivo.save(temp_input)

    try:
        # Descriptografar
        decryptor = PDFDecryptor()
        decrypted_path = decryptor.decrypt_single_pdf(temp_input)
        if not decrypted_path:
            return _mapa_invalido_response()

        # Extrair texto
        extractor = PDFTextExtractor()
        textos = extractor.extract_text_from_files([decrypted_path])
        if not textos:
            return _mapa_invalido_response()

        # Extrair dados estruturados
        data_extractor = PDFDataExtractor()
        df = data_extractor.extract_data(textos)
        if df.empty:
            return _mapa_invalido_response()

        # Aplicar perfilamento
        df = Senninha.aplicar(df)
        df = df.where(df.notnull(), None)

        nome = df.iloc[0]['nome'] if 'nome' in df.columns else ''
        nif = df.iloc[0]['nif'] if 'nif' in df.columns else ''
        perfila = any(df['perfila'])

        # Formatar a resposta final com snake_case
        info = df.to_dict(orient="records")
        info_snake = [renomear_chaves_para_snake_case(reg) for reg in info]

        resposta = {
            "nome": nome,
            "nif": nif,
            "perfila": perfila,
            "valid_map": True,
            "info_institutions": info_snake
        }
        return jsonify(resposta)

    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        return _mapa_invalido_response()

    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if 'decrypted_path' in locals() and os.path.exists(decrypted_path):
            os.remove(decrypted_path)

def _mapa_invalido_response():
    return jsonify({
        "nome": None,
        "nif": None,
        "perfila": False,
        "valid_map": False,
        "info_institutions": []
    })

def renomear_chaves_para_snake_case(d):
    return {
        k.lower()
         .replace(" ", "")
         .replace("ã", "a")
         .replace("á", "a")
         .replace("é", "e")
         .replace("í", "i")
         .replace("ç", "c")
         .replace("ô", "o")
         .replace("ó", "o"): v
        for k, v in d.items()
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)