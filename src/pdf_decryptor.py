import os
import shutil
import tempfile
import pikepdf
import fitz  # PyMuPDF
from config import Config  # Certifique-se de que o caminho esteja correto

class PDFDecryptor:
    def __init__(self, source_folder=Config.ENCRYPTED_FOLDER, 
                 processed_folder=Config.PROCESSED_ENCRYPTED_FOLDER, 
                 target_folder=Config.DECRYPTED_FOLDER):
        self.source_folder = source_folder
        self.processed_folder = processed_folder
        self.target_folder = target_folder

    def decrypt_pdfs_with_progress(self):
        pdf_files = [f for f in os.listdir(self.source_folder) if f.lower().endswith('.pdf')]
        total_files = len(pdf_files)

        if total_files == 0:
            print("Nenhum arquivo PDF encontrado na pasta maps.")
            return []

        decrypted_files = []

        for index, pdf_file in enumerate(pdf_files, start=1):
            encrypted_pdf_path = os.path.join(self.source_folder, pdf_file)

            # Remove todos os "decrypted_" do nome original
            file_name_clean = pdf_file
            while file_name_clean.startswith("decrypted_"):
                file_name_clean = file_name_clean[len("decrypted_"):]

            decrypted_pdf_path = os.path.join(self.target_folder, f"decrypted_{file_name_clean}")

            try:
                print(f"Processando {index} de {total_files} PDFs...")
                with pikepdf.open(encrypted_pdf_path) as pdf:
                    pdf.save(decrypted_pdf_path)
                print(f"✅ PDF desbloqueado com sucesso! Salvo em: {decrypted_pdf_path}")

                # Move o PDF original para a pasta processed
                shutil.move(encrypted_pdf_path, os.path.join(self.processed_folder, pdf_file))
                print(f"📁 PDF original criptografado movido para: {self.processed_folder}")

                decrypted_files.append(decrypted_pdf_path)
            except pikepdf.PasswordError:
                print(f"🔒 O PDF '{pdf_file}' está protegido por senha e não pode ser desbloqueado.")
            except FileNotFoundError as e:
                print(f"❌ Erro: Arquivo não encontrado. {e}")
            except Exception as e:
                print(f"⚠️ Ocorreu um erro ao descriptografar: {e}")

        return decrypted_files

    def decrypt_single_pdf(self, input_path):
        """
        Método específico para uso via API REST — descriptografa um único PDF.
        Ele cria um arquivo temporário com o mesmo conteúdo.
        """
        try:
            with open(input_path, "rb") as f:
                pdf_data = f.read()

            # Criar um arquivo temporário com o mesmo conteúdo
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_file.write(pdf_data)
            temp_file.close()

            return temp_file.name

        except Exception as e:
            print(f"❌ Erro ao descriptografar PDF único: {e}")
            return None