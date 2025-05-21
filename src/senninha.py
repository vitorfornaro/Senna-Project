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
        return valor_str  # caso já seja float ou None

    @staticmethod
    def aplicar(df: pd.DataFrame) -> pd.DataFrame:
        # 🔄 Conversão de colunas monetárias
        for col in ['divida', 'parcela', 'garantias']:
            df[col] = df[col].apply(Senninha.parse_float)

        # 🧠 Regras de perfilamento — apenas por garantia e litigio
        def regra_perfil_individual(row):
            garantia_ok = pd.isna(row['garantias']) or row['garantias'] == 0
            litigio_ok = isinstance(row['litigio'], str) and row['litigio'].replace('\xa0', '').strip().lower() == 'não'
            return garantia_ok and litigio_ok

        df['perfil_individual'] = df.apply(regra_perfil_individual, axis=1)

        # 💰 Soma das dívidas elegíveis
        soma = df[df['perfil_individual']]['divida'].sum()
        grupo_perfila = soma >= 6000
        df['perfila'] = df['perfil_individual'] & grupo_perfila

        print(f"\n💰 Soma das dívidas elegíveis: € {soma:,.2f}")
        print(f"🧾 Resultado final: {'✅ PERFILA' if grupo_perfila else '❌ NÃO PERFILA'}")

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

            dividas_elegiveis = grupo[(grupo['perfil_individual'] == True)]
            total_elegivel = dividas_elegiveis['divida'].sum()
            perfila = total_elegivel >= 6000

            estrutura = {
                "resumo": {
                    "nif": nif,
                    "divida_total_elegivel": round(total_elegivel, 2),
                    "perfila": bool(perfila)
                },
                "dividas": grupo.to_dict(orient="records")
            }

            path_json = os.path.join(base_path, f"{nif}.json")
            try:
                with open(path_json, "w", encoding="utf-8") as f:
                    json.dump(estrutura, f, ensure_ascii=False, indent=2)
                print(f"✅ Exportado JSON com resumo para NIF: {nif}")
            except Exception as e:
                print(f"❌ Erro ao salvar JSON de {nif}: {e}")