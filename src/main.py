import pandas as pd
from pdf_decryptor import PDFDecryptor
from pdf_text_extractor import PDFTextExtractor
from pdf_data_extractor import PDFDataExtractor
from pdf_output_handler import PDFOutputHandler
from senninha import Senninha
from validador import salvar_nao_perfilar  # Salvar clientes não perfilados com motivo

def process_pdfs():
    print("🚀 Iniciando processamento dos PDFs...")

    # 🔓 Descriptografar
    decryptor = PDFDecryptor()
    decrypted_pdfs = decryptor.decrypt_pdfs_with_progress()
    if not decrypted_pdfs:
        print("⚠️ Nenhum PDF para descriptografar.")
        return

    # 📝 Extração de texto (inclui fallback OCR)
    extractor = PDFTextExtractor()
    pdfs_text = extractor.extract_text_from_pdfs()
    if not pdfs_text:
        print("⚠️ Nenhum texto extraído dos PDFs.")
        return

    # 🔍 Extração de dados estruturados
    data_extractor = PDFDataExtractor()
    df = data_extractor.extract_data(pdfs_text)
    if df.empty:
        print("⚠️ Nenhum dado extraído do texto.")
        return

    print(f"📊 Total de registros extraídos: {len(df)}")

    # 👤 Debug opcional por NIF (remover em produção se não quiser output)
    # print(df[df["nif"] == "275211339"])

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

if __name__ == "__main__":
    process_pdfs()