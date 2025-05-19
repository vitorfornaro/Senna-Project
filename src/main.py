import pandas as pd
from pdf_decryptor import PDFDecryptor
from pdf_text_extractor import PDFTextExtractor
from pdf_data_extractor import PDFDataExtractor
from pdf_output_handler import PDFOutputHandler

def process_pdfs():
    decryptor = PDFDecryptor()
    decrypted_pdfs = decryptor.decrypt_pdfs_with_progress()

    if not decrypted_pdfs:
        print("Nenhum PDF para descriptografar.")
        return

    extractor = PDFTextExtractor()
    pdfs_text = extractor.extract_text_from_pdfs()

    if not pdfs_text:
        print("Nenhum texto extraído.")
        return

    data_extractor = PDFDataExtractor()
    df = data_extractor.extract_data(pdfs_text)

    if df.empty:
        print("Nenhum dado extraído do texto.")
        return

    # Substituir NaN/NaT por None para JSON
    df = df.where(pd.notnull(df), None)

    output_handler = PDFOutputHandler()
    output_handler.save_to_csv(df)
    output_handler.save_to_json(df)
    output_handler.save_json_by_client(df)  # ✅ Aqui você salva JSON por cliente

    print("✅ Todos os arquivos foram processados com sucesso!")

if __name__ == "__main__":
    process_pdfs()