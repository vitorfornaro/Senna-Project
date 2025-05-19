import re
import pandas as pd

class PDFDataExtractor:
    def __init__(self):
        self.regexes = {
            'nome': re.compile(r'Nome:\s+(.+)', re.MULTILINE),
            'nif': re.compile(r'Nº de Identificação:\s+(\d+)'),
            'mes_mapa': re.compile(r'Responsabilidades de crédito referentes a\s+(.+)'),
            'instituicao': re.compile(r'Informação comunicada pela instituição:\s+(.+)'),
            'total_em_divida': re.compile(r"Total em dívida\s+do qual, em incumprimento\s+([\d\s,.]+) €"),
            'litigio': re.compile(r'Em litígio judicial\s+(Sim|Não)'),
            'abatido_ativo': re.compile(r'Abatido ao ativo\s+([\d\s,.]+) €'),
            'garantias': re.compile(r"Tipo\s+Valor\s+Número\s*\n(?:.*?\n)?([-\d\s,.]+) €"),
            'num_devedores': re.compile(r"Nº devedores no contrato\s+(\d+)"),
            'prod_financeiro': re.compile(r"Produto financeiro\s+(.+?)\s+Tipo de responsabilidade"),
            'dat_inicio': re.compile(r"Início\s+(\d{4}-\d{2}-\d{2})"),
            'dat_fim': re.compile(r"Fim\s+(\d{4}-\d{2}-\d{2})"),
            'entrada_incumpr': re.compile(r"Entrada incumpr\.\s+(\d{4}-\d{2}-\d{2})"),
            'ano_mapa': re.compile(r'\b(19|20|21)\d{2}\b')
        }

    def get_feature(self, text, regex_key):
        if regex_key == 'garantias':
            match = self.regexes[regex_key].search(text)
            if match:
                valor = match.group(1).strip()
                if valor == '-' or not valor:
                    return '0'
                return valor
            elif "Garantias" in text:
                if re.search(r"Tipo\s+Valor\s+Número\s*\n\s*-+\s+-+\s+-+", text):
                    return '0'
            return None
        else:
            match = self.regexes[regex_key].search(text)
            return match.group(1).strip() if match else None

    def extract_data(self, pdf_pages_dict):
        data = []
        for pdf_name, pages in pdf_pages_dict.items():
            for page_number, page_text in pages.items():
                row = {
                    'arquivo_pdf': pdf_name,
                    'pagina_pdf': page_number,
                    'nome': self.get_feature(page_text, 'nome'),
                    'nif': self.get_feature(page_text, 'nif'),
                    'mes_mapa': self.get_feature(page_text, 'mes_mapa'),
                    'ano_mapa': self.get_feature(page_text, 'ano_mapa'),
                    'instituicao': self.get_feature(page_text, 'instituicao'),
                    'divida': self.get_feature(page_text, 'total_em_divida'),
                    'litigio': self.get_feature(page_text, 'litigio'),
                    'parcela': self.get_feature(page_text, 'abatido_ativo'),
                    'garantias': self.get_feature(page_text, 'garantias'),
                    'num_devedores': self.get_feature(page_text, 'num_devedores'),
                    'prod_financeiro': self.get_feature(page_text, 'prod_financeiro'),
                    'entrada_incumpr': self.get_feature(page_text, 'entrada_incumpr'),
                    'dat_inicio': self.get_feature(page_text, 'dat_inicio'),
                    'dat_fim': self.get_feature(page_text, 'dat_fim')
                }
                data.append(row)
        return pd.DataFrame(data)