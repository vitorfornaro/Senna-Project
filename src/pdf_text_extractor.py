import os
import shutil
import re
from PyPDF2 import PdfReader
from config import Config
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile

class PDFTextExtractor:
    def __init__(self, input_folder=Config.DECRYPTED_FOLDER, processed_folder=Config.PROCESSED_DECRYPTED_FOLDER):
        self.input_folder = input_folder
        self.processed_folder = processed_folder

    def extract_text_from_pdfs(self, pdf_paths=None):
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
                reader = PdfReader(input_pdf_path)
                pagina_dict = {}
                paginas_validas = 0

                for idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pagina_dict[f"texto_pagina{idx+1}"] = text.strip()
                        paginas_validas += 1
                    else:
                        # ⚠️ OCR fallback
                        ocr_text = self.extract_text_with_ocr(input_pdf_path, idx)
                        if ocr_text:
                            pagina_dict[f"texto_pagina{idx+1}"] = ocr_text
                            paginas_validas += 1

                print(f"📄 '{file_name}' tem {paginas_validas} páginas extraídas.")
                pdfs_text[file_name] = pagina_dict

            except Exception as e:
                print(f"⚠️ Erro ao extrair '{file_name}': {e}")
            finally:
                shutil.move(input_pdf_path, processed_pdf_path)

        return pdfs_text

    def extract_text_with_ocr(self, pdf_path, page_index):
        try:
            with tempfile.TemporaryDirectory() as path:
                images = convert_from_path(
                    pdf_path,
                    dpi=300,
                    first_page=page_index + 1,
                    last_page=page_index + 1,
                    output_folder=path
                )
                if images:
                    ocr_text = pytesseract.image_to_string(images[0], lang='por')
                    return ocr_text.strip()
        except Exception as e:
            print(f"❌ Erro ao aplicar OCR na página {page_index+1} de '{pdf_path}': {e}")
        return ""