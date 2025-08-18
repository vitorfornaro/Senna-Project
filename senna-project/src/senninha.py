import pandas as pd
import unicodedata
import os
import json
from config import Config

class Senninha:
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
            print('🔍 Garantia original:', row['garantias'])  # Debug

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

        # === REGRA DE GRUPO ===
        df['perfila'] = False

        for instituicao, grupo in df.groupby("instituicao"):
            tem_garantia = (grupo['garantias'] > 0).any()
            tem_habitacao = grupo['prodfinanceiro'].astype(str).str.lower().str.contains("habitacao|habitação").any()

            if not tem_garantia and not tem_habitacao:
                indices = grupo[grupo['perfil_individual']].index
                df.loc[indices, 'perfila'] = True

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

            dividas_elegiveis = grupo[grupo['perfila']]
            total_elegivel = dividas_elegiveis['divida'].sum()
            perfila = total_elegivel >= 6000

            estrutura = {
                "resumo": {
                    "nif": nif,
                    "divida_total_elegivel": round(total_elegivel, 2),
                    "perfila": perfila
                },
                "dividas": grupo.to_dict(orient="records")
            }

            try:
                with open(os.path.join(base_path, f"{nif}.json"), "w", encoding="utf-8") as f:
                    json.dump(estrutura, f, ensure_ascii=False, indent=2)
                print(f"✅ JSON com resumo exportado para NIF {nif}")
            except Exception as e:
                print(f"❌ Erro ao salvar JSON para {nif}: {e}")