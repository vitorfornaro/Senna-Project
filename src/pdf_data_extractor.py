import re
import os
import unicodedata
from datetime import datetime
import pandas as pd

LOG_FOLDER = "./logs"
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOG_FOLDER, "erros_processamento.txt")

# Função para limpar e padronizar texto
def limpar_nome(texto):
    if pd.isna(texto):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.lower().replace("sucursal em portugal", "")
    texto = texto.replace(",", "").replace(".", "").strip()
    return texto

# Carrega o CSV de mapeamento
caminho_csv = os.path.join(os.path.dirname(__file__), "bancos_padrao.csv")
df_map = pd.read_csv(caminho_csv)

# Função para normalizar nome da instituição
def normalizar_nome_banco(nome_extraido):
    nome_limpo = limpar_nome(nome_extraido)
    for _, row in df_map.iterrows():
        chave = limpar_nome(row['chave'])
        if chave in nome_limpo:
            return row['name']
    return nome_extraido

class PDFDataExtractor:
    def __init__(self):
        self.regexes = {
            'nome': re.compile(r'Nome:\s+(.+)', re.MULTILINE),
            'nif': re.compile(r'Nº de Identificação:\s+(\d+)'),
            'mesmapa': re.compile(r'Responsabilidades de crédito referentes a\s+(.+)', re.MULTILINE),
            'anomapa': re.compile(r'\b(19|20|21)\d{2}\b'),
            'bloco_instituicao': re.compile(
                r'(Informação comunicada pela instituição:.*?)(?=Informação comunicada pela instituição:|$)',
                re.DOTALL
            )
        }

        self.item_regexes = {
            'instituicao': re.compile(r'Informação comunicada pela instituição:\s+(.+)'),
            'divida': re.compile(r'Total em dívida\s+do qual, em incumprimento\s+([\d\s,.]+)\s*€'),
            'divida_fallback': re.compile(r'Total em dívida.*?([\d\s,.]+)\s*€', re.DOTALL),
            'litigio': re.compile(r'Em litígio judicial\s+(Sim|Não)', re.IGNORECASE),
            'parcela': re.compile(r'Abatido ao ativo.*?([\d\s,.]+)\s*€'),
            'garantias': re.compile(r"Valor\s+[\d\s.,]+\s+([\d\s.,]+)\s*€", re.DOTALL),
            'numdevedores': re.compile(r"Nº devedores no contrato\s+(\d+)"),
            'prodfinanceiro': re.compile(r"Produto financeiro\s+(.+?)\s+Tipo de responsabilidade", re.DOTALL),
            'datinicio': re.compile(r"Início\s+(\d{4}-\d{2}-\d{2})"),
            'datfim': re.compile(r"Fim\s+(\d{4}-\d{2}-\d{2})"),
            'entradaincumpr': re.compile(r"Entrada incumpr\.\s+(\d{4}-\d{2}-\d{2})"),
        }

    def get_header_info(self, text, key):
        match = self.regexes[key].search(text)
        return match.group(1).strip() if match else None

    def _sanitize_numeric(self, valor):
        if not valor or valor in ('-', ''):
            return 0.0
        try:
            return float(valor.replace('.', '').replace(',', '.'))
        except Exception:
            return 0.0

    def extract_data(self, pdf_pages_dict):
        data = []

        for pdf_name, pages in pdf_pages_dict.items():
            for page_number, page_text in sorted(pages.items()):
                try:
                    nome = self.get_header_info(page_text, 'nome')
                    nif = self.get_header_info(page_text, 'nif')
                    mesmapa = self.get_header_info(page_text, 'mesmapa')
                    anomapa = self.get_header_info(page_text, 'anomapa')

                    blocos_instituicao = self.regexes['bloco_instituicao'].findall(page_text)
                    print(f"📄 Página texto_pagina{page_number} de '{pdf_name}' contém {len(blocos_instituicao)} blocos de instituição detectados.")

                    for bloco in blocos_instituicao:
                        bloco = bloco.replace('\xa0', ' ')
                        linhas = bloco.strip().splitlines()
                        nome_inst = "nao_identificada"

                        if linhas and linhas[0].startswith("Informação comunicada pela instituição:"):
                            match_inst = re.match(r"Informação comunicada pela instituição:\s+(.+)", linhas[0])
                            if match_inst:
                                nome_inst = match_inst.group(1).strip()
                                bloco = "\n".join(linhas[1:])

                        sub_blocos = re.findall(r"(Montantes.*?Produto financeiro.+?)(?=Montantes|$)", bloco, re.DOTALL)
                        if not sub_blocos:
                            sub_blocos = [bloco]

                        for sub_bloco in sub_blocos:
                            sub_bloco = sub_bloco.replace('\xa0', ' ')
                            row = {
                                'arquivopdf': os.path.basename(pdf_name).replace("decrypted_", ""),
                                'paginapdf': f"texto_pagina{page_number}",
                                'nome': nome.lower() if nome else None,
                                'nif': nif,
                                'mesmapa': mesmapa.lower() if mesmapa else None,
                                'anomapa': anomapa,
                                'instituicao': normalizar_nome_banco(nome_inst).lower()
                            }

                            for key, regex in self.item_regexes.items():
                                if key == 'instituicao' or key == 'divida_fallback':
                                    continue

                                match = regex.search(sub_bloco)
                                valor = match.group(1).strip() if match else None

                                if key == 'divida' and not valor:
                                    fallback_match = self.item_regexes['divida_fallback'].search(sub_bloco)
                                    valor = fallback_match.group(1).strip() if fallback_match else None

                                if valor:
                                    valor = valor.replace("\xa0", "").replace(" ", "")

                                if key in ['divida', 'parcela', 'garantias']:
                                    row[key] = self._sanitize_numeric(valor)
                                elif key == 'numdevedores':
                                    try:
                                        row[key] = int(valor) if valor else None
                                    except Exception:
                                        row[key] = None
                                else:
                                    row[key] = valor

                            data.append(row)

                except Exception as e:
                    log_msg = f"[{datetime.now().isoformat()}] Erro na página {page_number} do '{pdf_name}': {str(e)}\n"
                    print(log_msg.strip())
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(log_msg)

        df_final = pd.DataFrame(data)

        colunas_esperadas = {
            'divida': 0.0,
            'parcela': 0.0,
            'garantias': 0.0,
            'numdevedores': None
        }

        for coluna, valor_padrao in colunas_esperadas.items():
            if coluna not in df_final.columns:
                df_final[coluna] = valor_padrao

        print(f"\n📊 Total de linhas extraídas: {len(df_final)}")
        return df_final
