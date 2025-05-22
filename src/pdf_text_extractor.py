import os
import shutil
import re
from PyPDF2 import PdfReader
from config import Config

class PDFTextExtractor:
    def __init__(self, input_folder=Config.DECRYPTED_FOLDER, processed_folder=Config.PROCESSED_DECRYPTED_FOLDER):
        self.input_folder = input_folder
        self.processed_folder = processed_folder

    def extract_text_from_pdfs(self, pdf_paths=None):  # ← aceita lista de PDFs
        if pdf_paths is None:
            pdf_paths = [os.path.join(self.input_folder, f) for f in os.listdir(self.input_folder) if f.lower().endswith(".pdf")]

        if not pdf_paths:
            print("Nenhum PDF encontrado para extração.")
            return {}

        pdfs_text = {}
        for input_pdf_path in pdf_paths:
            file_name = os.path.basename(input_pdf_path)
            processed_pdf_path = os.path.join(self.processed_folder, file_name)
            try:
                full_text = ""
                reader = PdfReader(input_pdf_path)
                for idx, page in enumerate(reader.pages):
                    full_text += f"------------------ PAGINA {idx} ----------------\n"
                    page_text = page.extract_text() or ""
                    full_text += page_text

                paginas = re.split(r"------------------ PAGINA \d+ ----------------", full_text)
                paginas = [p.strip() for p in paginas if p.strip()]

                print(f"📄 '{file_name}' tem {len(paginas)} páginas extraídas.")
                pdfs_text[file_name] = {f"texto_pagina{idx+1}": pag for idx, pag in enumerate(paginas)}

            except Exception as e:
                print(f"⚠️ Erro ao extrair '{file_name}': {e}")
            finally:
                shutil.move(input_pdf_path, processed_pdf_path)

        return pdfs_text