import pandas as pd
import unicodedata

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
        # Conversão dos valores
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

        # Checar se grupo perfila (>= 6000)
        soma_total_elegivel = df[df['perfil_individual']]['divida'].sum()
        grupo_perfila = soma_total_elegivel >= 6000
        df['perfila'] = df['perfil_individual'] & grupo_perfila

        print(f"\n💰 Soma das dívidas elegíveis: € {soma_total_elegivel:,.2f}")
        print(f"🧾 Resultado final: {'✅ PERFILA' if grupo_perfila else '❌ NÃO PERFILA'}")

        return df