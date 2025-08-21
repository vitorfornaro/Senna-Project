import pandas as pd
import unicodedata
import os
import re
import json
from config import Config

class Senninha:
    BANK_MINIMA = {
        "credibom": 10000.0,
        "cofidis": 5000.0,
        "santander": 10000.0,
        "bnp": 4000.0,
        "millennium": 10500.0,
        "wizink": 3000.0,
        "hefesto": 5500.0,
        "bankinter": 13000.0,  # Bankinter SA e Bankinter Consumer Finance
        "younited": 3700.0,
        "unicre": 3500.0,
    }

    BANK_PATTERNS = {
        "credibom": [r"\bcredibom\b"],
        "cofidis": [r"\bcofidis\b"],
        "santander": [r"\bsantander\b"],
        "bnp": [r"\bbnp\b", r"paribas"],
        "millennium": [r"\bmillennium\b", r"\bbcp\b"],
        "wizink": [r"\bwizink\b"],
        "hefesto": [r"\bhefesto\b"],
        "bankinter": [r"\bbankinter\b", r"consumer\s*finance"],
        "younited": [r"\byounited\b"],
        "unicre": [r"\bunicre\b"],
    }

    @staticmethod
    def _strip_accents_lower(text: str) -> str:
        if text is None:
            return ""
        text = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in text if not unicodedata.combining(c)])
        return text.lower()

    @classmethod
    def normalize_bank_name(cls, instituicao: str) -> str:
        base = cls._strip_accents_lower(instituicao)
        base = re.sub(r"[,.;:()\-\n]+", " ", base)
        base = re.sub(r"\s+", " ", base).strip()
        for bank_key, patterns in cls.BANK_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, base):
                    return bank_key
        return ""

    @staticmethod
    def parse_float(valor_str):
        if isinstance(valor_str, str):
            valor_str = valor_str.replace('\xa0', '').replace('€', '').replace(',', '.')
            valor_str = ''.join(c for c in valor_str if not unicodedata.category(c).startswith('Z'))
            try:
                return float(valor_str)
            except ValueError:
                return None
        return valor_str

    @staticmethod
    def aplicar(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Conversão robusta
        for col in ['divida', 'parcela', 'garantias']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # === REGRA INDIVIDUAL (por linha) ===
        def regra_perfil_individual(row):
            garantia_ok = row['garantias'] == 0.0
            litigio_ok = isinstance(row['litigio'], str) and row['litigio'].replace('\xa0', '').strip().lower() in ('não', 'nao')
            produto = str(row.get('prodfinanceiro', '')).strip().lower()
            divida = row.get('divida') or 0.0

            if 'habitação' in produto or 'habitacao' in produto:
                return False

            if 'automóvel' in produto or 'automovel' in produto:
                if not garantia_ok:
                    return False
                return litigio_ok and divida >= 10000

            return garantia_ok and litigio_ok and divida > 0

        df['perfil_individual'] = df.apply(regra_perfil_individual, axis=1)

        # === PERFILA (lógica existente por instituição) ===
        df['perfila'] = False
        for instituicao, grupo in df.groupby("instituicao"):
            tem_garantia = (grupo['garantias'] > 0).any()
            tem_habitacao = grupo['prodfinanceiro'].astype(str).str.lower().str.contains("habitacao|habitação").any()
            if not tem_garantia and not tem_habitacao:
                indices = grupo[grupo['perfil_individual']].index
                df.loc[indices, 'perfila'] = True

        # === PARI/PERSI UNIFICADO (pari_persi) ===
        # 1) banco canônico por linha
        df['bank_canon'] = df['instituicao'].astype(str).apply(lambda s: Senninha.normalize_bank_name(s))

        # 2) identificador do MAPA (prioriza o arquivo; senão mes+ano; senão NIF)
        def build_map_id(row):
            arquivo = row.get('arquivopdf')
            if arquivo and str(arquivo).strip():
                return str(arquivo)
            parts = []
            if row.get('mesmapa'): parts.append(str(row['mesmapa']))
            if row.get('anomapa'): parts.append(str(row['anomapa']))
            if parts:
                return "|".join(parts)
            return str(row.get('nif', ''))

        df['map_id'] = df.apply(build_map_id, axis=1)

        # 3) soma apenas dívidas > 0 dentro do mesmo NIF + MAPA + BANCO
        df['divida_pos'] = df['divida'].where(df['divida'] > 0.0, 0.0)
        totals = (
            df.groupby(['nif', 'map_id', 'bank_canon'], dropna=False)['divida_pos']
              .sum()
              .reset_index()
              .rename(columns={'divida_pos': 'total_nif_mapa_banco'})
        )

        # 4) junta o total por (NIF, MAPA, BANCO)
        df = df.merge(totals, on=['nif', 'map_id', 'bank_canon'], how='left')
        df['total_nif_mapa_banco'] = df['total_nif_mapa_banco'].fillna(0.0)

        # 5) banco do item atinge o mínimo no contexto daquele MAPA?
        def banco_atinge_min(row):
            bank_key = row['bank_canon']
            if not bank_key:
                return False
            minimo = Senninha.BANK_MINIMA.get(bank_key)
            if minimo is None:
                return False
            return row['total_nif_mapa_banco'] >= minimo

        df['bank_ok'] = df.apply(banco_atinge_min, axis=1)

        # 6) por dívida: pari_persi = perfil_individual & divida>0 & bank_ok
        df['pari_persi'] = (df['perfil_individual'] == True) & (df['divida'] > 0) & (df['bank_ok'] == True)

        # === REMOÇÃO DEFINITIVA DOS AUXILIARES (só ficam total_nif_mapa_banco e pari_persi) ===
        df = df.drop(columns=[c for c in ['bank_canon', 'map_id', 'divida_pos', 'bank_ok'] if c in df.columns], errors='ignore')

        # Limpeza final (mantém tipos)
        df['perfil_individual'] = df['perfil_individual'].fillna(False)
        df['perfila'] = df['perfila'].fillna(False)
        df['divida'] = pd.to_numeric(df['divida'], errors='coerce').fillna(0.0)

        return df

    @staticmethod
    def exportar_json_com_resumo(df: pd.DataFrame):
        if df.empty:
            print("⚠️ Nenhum dado para exportar com resumo.")
            return

        df = df.copy()
        df = df.where(pd.notnull(df), None)

        base_path = os.path.join(Config.MAPS_DIR, "customers")
        os.makedirs(base_path, exist_ok=True)

        for nif, grupo in df.groupby("nif"):
            if not nif:
                continue

            # total elegível (mantendo sua lógica baseada em 'perfila')
            dividas_elegiveis = grupo[grupo['perfila'] == True]
            total_elegivel = float(dividas_elegiveis['divida'].sum())
            perfila = total_elegivel >= 6000

            # >>> NOVO NO RESUMO: pari_persi agregado por NIF
            # true se existir pelo menos UMA linha com pari_persi true para este NIF
            pari_persi_resumo = bool(pd.Series(grupo.get('pari_persi', False)).fillna(False).any())

            estrutura = {
                "resumo": {
                    "nif": nif,
                    "divida_total_elegivel": round(total_elegivel, 2),
                    "perfila": perfila,
                    "pari_persi": pari_persi_resumo
                },
                # as dívidas já vêm só com total_nif_mapa_banco e pari_persi de extra
                "dividas": grupo.to_dict(orient="records")
            }

            try:
                with open(os.path.join(base_path, f"{nif}.json"), "w", encoding="utf-8") as f:
                    json.dump(estrutura, f, ensure_ascii=False, indent=2)
                print(f"✅ JSON com resumo exportado para NIF {nif}")
            except Exception as e:
                print(f"❌ Erro ao salvar JSON para {nif}: {e}")