import re
import os
from datetime import datetime
import pandas as pd

LOG_FOLDER = "./logs"
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOG_FOLDER, "erros_processamento.txt")

class PDFDataExtractor:
    def __init__(self):
        self.regexes = {
            'nome': re.compile(r'Nome:\s+(.+)', re.MULTILINE),
            'nif': re.compile(r'Nº de Identificação:\s+(\d+)'),
            'mes_mapa': re.compile(r'Responsabilidades de crédito referentes a\s+(.+)', re.MULTILINE),
            'ano_mapa': re.compile(r'\b(19|20|21)\d{2}\b'),
            # Captura blocos por instituição (com o prefixo incluído)
            'bloco_instituicao': re.compile(r'(Informação comunicada pela instituição:.*?)(?=Informação comunicada pela instituição:|$)', re.DOTALL)
        }

        self.item_regexes = {
            'instituicao': re.compile(r'Informação comunicada pela instituição:\s+(.+)'),
            'divida': re.compile(r'Total em dívida\s+do qual, em incumprimento\s+([\d\s,.]+) €'),
            'litigio': re.compile(r'Em litígio judicial\s+(Sim|Não)'),
            'parcela': re.compile(r'Abatido ao ativo\s+([\d\s,.]+) €'),
            'garantias': re.compile(r"Tipo\s+Valor\s+Número\s*\n(?:.*?\n)?([-\d\s,.]+) €"),
            'num_devedores': re.compile(r"Nº devedores no contrato\s+(\d+)"),
            'prod_financeiro': re.compile(r"Produto financeiro\s+(.+?)\s+Tipo de responsabilidade"),
            'dat_inicio': re.compile(r"Início\s+(\d{4}-\d{2}-\d{2})"),
            'dat_fim': re.compile(r"Fim\s+(\d{4}-\d{2}-\d{2})"),
            'entrada_incumpr': re.compile(r"Entrada incumpr\.\s+(\d{4}-\d{2}-\d{2})"),
        }

    def get_header_info(self, text, key):
        match = self.regexes[key].search(text)
        return match.group(1).strip() if match else None

    def extract_data(self, pdf_pages_dict):
        data = []

        for pdf_name, pages in pdf_pages_dict.items():
            for page_number, page_text in sorted(pages.items()):
                try:
                    nome = self.get_header_info(page_text, 'nome')
                    nif = self.get_header_info(page_text, 'nif')
                    mes_mapa = self.get_header_info(page_text, 'mes_mapa')
                    ano_mapa = self.get_header_info(page_text, 'ano_mapa')

                    blocos_instituicao = self.regexes['bloco_instituicao'].findall(page_text)
                    print(f"📄 Página {page_number} de '{pdf_name}' contém {len(blocos_instituicao)} blocos de instituição detectados.")

                    for i, bloco in enumerate(blocos_instituicao, 1):
                        bloco = bloco.replace('\xa0', ' ')  # limpeza de espaços invisíveis
                        linhas = bloco.strip().splitlines()
                        nome_inst = "NÃO IDENTIFICADA"

                        if linhas and linhas[0].startswith("Informação comunicada pela instituição:"):
                            match_inst = re.match(r"Informação comunicada pela instituição:\s+(.+)", linhas[0])
                            if match_inst:
                                nome_inst = match_inst.group(1).strip()
                                bloco = "\n".join(linhas[1:])  # remove a linha da instituição do bloco

                        sub_blocos = re.findall(r"(Montantes.*?Produto financeiro.+?)(?=Montantes|$)", bloco, re.DOTALL)
                        if not sub_blocos:
                            sub_blocos = [bloco]

                        for sub_bloco in sub_blocos:
                            sub_bloco = sub_bloco.replace('\xa0', ' ')
                            row = {
                                'arquivo_pdf': os.path.basename(pdf_name).replace("decrypted_", ""),
                                'pagina_pdf': f"texto_pagina{page_number}",
                                'nome': nome,
                                'nif': nif,
                                'mes_mapa': mes_mapa,
                                'ano_mapa': ano_mapa,
                                'instituicao': nome_inst
                            }

                            for key, regex in self.item_regexes.items():
                                if key == 'instituicao':
                                    continue  # já tratamos acima
                                match = regex.search(sub_bloco)
                                valor = match.group(1).strip() if match else None
                                if valor:
                                    valor = valor.replace("\xa0", "").replace(" ", "")
                                if key == 'garantias' and (valor in ('-', '', None)):
                                    valor = '0'
                                row[key] = valor

                            data.append(row)

                except Exception as e:
                    log_msg = f"[{datetime.now().isoformat()}] Erro ao processar página {page_number} do '{pdf_name}': {str(e)}\n"
                    print(log_msg.strip())
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(log_msg)

        print(f"\n📊 Total de linhas extraídas: {len(data)}")
        return pd.DataFrame(data)