import pandas as pd
import unicodedata
import os
import json
from config import Config

class Senninha:
    @staticmethod
    def parse_float(valor_str):
        if isinstance(valor_str, str):
            valor_str = ''.join(c for c in valor_str if not unicodedata.category(c).startswith('Z'))
            valor_str = valor_str.replace('€', '').replace(',', '.')
            try:
                return float(valor_str)
            except ValueError:
                return None
        return None

    @staticmethod
    def aplicar(df: pd.DataFrame) -> pd.DataFrame:
        # Conversão dos valores monetários
        for col in ['divida', 'parcela', 'garantias']:
            df[col] = df[col].apply(Senninha.parse_float)

        # Regras de perfilamento
        def regra_sem_garantia(row):
            return pd.isna(row['garantias']) or row['garantias'] == 0.0

        def regra_sem_litigio(row):
            return isinstance(row['litigio'], str) and row['litigio'].strip().lower() == 'não'

        instituicoes_com_garantia = df[df['garantias'] > 0]['instituicao'].unique().tolist()

        def instituicao_sem_qualquer_garantia(row):
            return row['instituicao'] not in instituicoes_com_garantia

        # Aplicar regras
        df['perfil_individual'] = df.apply(
            lambda r: regra_sem_garantia(r) and regra_sem_litigio(r) and instituicao_sem_qualquer_garantia(r),
            axis=1
        )

        soma_total_elegivel = df[df['perfil_individual']]['divida'].sum()
        grupo_perfila = soma_total_elegivel >= 6000
        df['perfila'] = df['perfil_individual'] & grupo_perfila

        print(f"\n💰 Soma das dívidas elegíveis: € {soma_total_elegivel:,.2f}")
        print(f"🧾 Resultado final: {'✅ PERFILA' if grupo_perfila else '❌ NÃO PERFILA'}")

        return df

    @staticmethod
    def exportar_json_com_resumo(df: pd.DataFrame):
        output_dir = os.path.join(Config.MAPS_DIR, "customers")
        os.makedirs(output_dir, exist_ok=True)

        df_validos = df[df['nif'].notna()]

        for nif, grupo in df_validos.groupby("nif"):
            grupo = grupo.copy()
            grupo['divida'] = grupo['divida'].apply(Senninha.parse_float)
            grupo['perfil_individual'] = grupo['perfil_individual'].astype(bool)

            dividas_elegiveis = grupo[grupo['perfil_individual']]
            total_elegivel = dividas_elegiveis['divida'].sum()
            perfila = total_elegivel >= 6000

            json_data = {
                "resumo": {
                    "nif": nif,
                    "divida_total_elegivel": round(total_elegivel, 2),
                    "perfila": perfila
                },
                "dividas": grupo.to_dict(orient="records")
            }

            json_path = os.path.join(output_dir, f"{nif}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ JSONs com resumo e dívidas salvos em: {output_dir}")