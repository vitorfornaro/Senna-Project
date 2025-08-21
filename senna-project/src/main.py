import pandas as pd
import json

# ✅ Imports ajustados para a nova estrutura
from services.pdf_decryptor import PDFDecryptor
from services.pdf_text_extractor import PDFTextExtractor
from services.pdf_data_extractor import PDFDataExtractor
from services.senninha import Senninha
from handlers.pdf_output_handler import PDFOutputHandler
from handlers.validador import salvar_nao_perfilar  # salva clientes não perfilados

def process_pdfs():
    print("🚀 Iniciando processamento dos PDFs...")

    # 🔓 Descriptografar
    decryptor = PDFDecryptor()
    decrypted_pdfs = decryptor.decrypt_pdfs_with_progress()
    if not decrypted_pdfs:
        print(json.dumps({"status": "empty", "mensagem": "Nenhum PDF para descriptografar."}, ensure_ascii=False))
        return

    # 📝 Extração de texto (inclui fallback OCR)
    extractor = PDFTextExtractor()
    pdfs_text = extractor.extract_text_from_pdfs()
    if not pdfs_text:
        print(json.dumps({"status": "empty", "mensagem": "Nenhum texto extraído dos PDFs."}, ensure_ascii=False))
        return

    # 🔍 Extração de dados estruturados
    data_extractor = PDFDataExtractor()
    df = data_extractor.extract_data(pdfs_text)
    if df.empty:
        print(json.dumps({"status": "empty", "mensagem": "Nenhum dado extraído do texto."}, ensure_ascii=False))
        return

    print(f"📊 Total de registros extraídos: {len(df)}")

    # 🧠 Regras de perfilamento
    df = Senninha.aplicar(df)

    # 💾 Exportação JSON por cliente (perfilados)
    Senninha.exportar_json_com_resumo(df)

    # ❌ Exportar não perfilados com motivo
    salvar_nao_perfilar(df)

    # 🧹 Preparar dados para exportação
    df = df.where(pd.notnull(df), None)

    # 📤 Exportações finais
    output_handler = PDFOutputHandler()
    output_handler.save_to_csv(df)
    output_handler.save_to_json(df)
    output_handler.save_json_by_client(df)

    print("✅ Todos os arquivos foram processados e salvos com sucesso!")

    # ✅ Retornar um JSON parseável para o n8n
    try:
        if not df.empty:
            output_data = df.head(1).to_dict(orient="records")[0]
            print(json.dumps(output_data, ensure_ascii=False))
        else:
            print(json.dumps({"status": "vazio", "mensagem": "Nenhum dado perfilado."}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": "Erro ao gerar saída JSON", "details": str(e)}, ensure_ascii=False))

if __name__ == "__main__":
    process_pdfs()