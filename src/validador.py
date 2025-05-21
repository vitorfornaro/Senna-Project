# src/validador.py

import pandas as pd

def validar_perfilamento(df: pd.DataFrame, verbose: bool = True):
    """
    Valida o perfilamento com explicações detalhadas por NIF e instituição.
    """

    print("\n🧠 Iniciando validação dos resultados de perfilamento...\n")

    nifs = df['nif'].dropna().unique()

    for nif in nifs:
        print(f"\n📌 NIF: {nif}")

        df_nif = df[df['nif'] == nif].copy()
        df_perfiladas = df_nif[df_nif['perfil_individual'] == True]
        total_elegivel = df_perfiladas['divida'].sum()
        grupo_perfila = total_elegivel >= 6000

        print(f"💰 Total de dívidas elegíveis: € {total_elegivel:,.2f}")
        print(f"✅ PERFILA? {'Sim' if grupo_perfila else 'Não'}")

        if verbose:
            print("\n🔎 Analisando dívidas...")

            for _, row in df_nif.iterrows():
                motivos = []

                if not isinstance(row['litigio'], str) or row['litigio'].strip().lower() != 'não':
                    motivos.append("⚠️ Litígio presente")

                if row['garantias'] is not None and row['garantias'] > 0:
                    motivos.append("⚠️ Possui garantia")

                if not motivos:
                    motivos.append("✅ Dívida elegível")

                print(f"\n📄 Instituição: {row['instituicao']}")
                print(f"   → Valor: € {row['divida']}")
                print(f"   → Perfilou? {'Sim' if row['perfil_individual'] else 'Não'}")
                for motivo in motivos:
                    print(f"      - {motivo}")