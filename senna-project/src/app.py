from flask import Flask, request, jsonify
import tempfile
import os
import uuid
from unidecode import unidecode

from pdf_decryptor import PDFDecryptor
from pdf_text_extractor import PDFTextExtractor
from pdf_data_extractor import PDFDataExtractor
from senninha import Senninha

app = Flask(__name__)

@app.route('/perfilamento', methods=['POST'])
def perfilamento():
    print("📥 Requisição recebida para /perfilamento")

    if 'mdr' not in request.files:
        print("❌ Campo 'mdr' não foi enviado.")
        return jsonify({"error": "Arquivo PDF não enviado no campo 'mdr'"}), 400

    arquivo = request.files['mdr']
    filename = f"{uuid.uuid4().hex}.pdf"
    temp_input = os.path.join(tempfile.gettempdir(), filename)
    print(f"📎 PDF salvo temporariamente como: {temp_input}")
    arquivo.save(temp_input)

    try:
        print("🔐 Descriptografando PDF...")
        decryptor = PDFDecryptor()
        decrypted_path = decryptor.decrypt_single_pdf(temp_input)
        if not decrypted_path:
            print("❌ Falha na descriptografia.")
            return _mapa_invalido_response()

        print(f"📄 Extraindo texto de: {decrypted_path}")
        extractor = PDFTextExtractor(input_folder=os.path.dirname(decrypted_path),
                                     processed_folder=os.path.dirname(decrypted_path))
        textos = extractor.extract_text_from_pdfs([decrypted_path])
        if not textos:
            print("❌ Nenhum texto foi extraído.")
            return _mapa_invalido_response()

        print("📊 Extraindo dados estruturados...")
        data_extractor = PDFDataExtractor()
        df = data_extractor.extract_data(textos)
        if df.empty:
            print("❌ Nenhum dado estruturado encontrado.")
            return _mapa_invalido_response()

        print("🧠 Aplicando perfilamento...")
        df = Senninha.aplicar(df)
        df = df.where(df.notnull(), None)

        nome = df.iloc[0].get('nome', '')
        nif = df.iloc[0].get('nif', '')
        perfila = any(df['perfila'])

        print(f"✅ Resultado: {nome} - {nif} - {'PERFILA' if perfila else 'NÃO PERFILA'}")

        info = df.to_dict(orient="records")
        info_snake = [renomear_chaves_para_snake_case(reg) for reg in info]

        return jsonify({
            "nome": unidecode(nome.lower().replace(" ", "")) if nome else None,
            "nif": nif,
            "perfila": perfila,
            "valid_map": True,
            "info_institutions": info_snake
        })

    except Exception as e:
        print(f"🔥 Erro crítico no processamento: {e}")
        return _mapa_invalido_response()

    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if 'decrypted_path' in locals() and decrypted_path and os.path.exists(decrypted_path):
            os.remove(decrypted_path)

def _mapa_invalido_response():
    print("⚠️ Resposta gerada: Mapa inválido")
    return jsonify({
        "nome": None,
        "nif": None,
        "perfila": False,
        "valid_map": False,
        "info_institutions": []
    })

def renomear_chaves_para_snake_case(d):
    resultado = {}
    for k, v in d.items():
        chave = unidecode(k.lower().replace(" ", "").replace("-", ""))
        valor = unidecode(v.lower().replace(" ", "").replace("-", "")) if isinstance(v, str) else v
        resultado[chave] = valor
    return resultado

if __name__ == '__main__':
    # ✅ ESSENCIAL: escutar em todas as interfaces para que o n8n (outro container) consiga acessar
    app.run(host='0.0.0.0', port=5001)