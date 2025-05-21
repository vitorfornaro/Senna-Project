import os
import json
from config import Config

# ✅ Pastas de saída
CUSTOMER_DIR = os.path.join(Config.MAPS_DIR, "customers")
NO_PERFILA_DIR = os.path.join(Config.MAPS_DIR, "no_perfila")

os.makedirs(CUSTOMER_DIR, exist_ok=True)
os.makedirs(NO_PERFILA_DIR, exist_ok=True)

def salvar_nao_perfilar(df):
    df_nao_perfila = df[df["perfila"] == False]

    if df_nao_perfila.empty:
        print("✅ Nenhum cliente reprovado. Nada a salvar.")
        return

    for nif, grupo in df_nao_perfila.groupby("nif"):
        dividas_com_motivos = []

        for _, row in grupo.iterrows():
            motivos = []

            if str(row["litigio"]).strip().lower() == "sim":
                motivos.append("Litígio judicial")

            if float(row.get("garantias") or 0) > 0:
                motivos.append("Dívida com garantia")

            outras = grupo[(grupo["instituicao"] == row["instituicao"]) & (
                (grupo["litigio"].astype(str).str.strip().str.lower() == "sim") |
                (grupo["garantias"].fillna(0).astype(float) > 0)
            )]
            if not outras.empty:
                motivos.append("Instituição tem outra dívida com garantia/litigio")

            dividas_com_motivos.append({
                "instituicao": row["instituicao"],
                "valor": row["divida"],
                "motivos_reprovacao": list(set(motivos)) or ["Regras de perfilamento não atendidas"]
            })

        resumo = {
            "nif": nif,
            "divida_total_elegivel": grupo["divida"].sum(),
            "perfila": False
        }

        estrutura = {
            "resumo": resumo,
            "motivos": dividas_com_motivos
        }

        # ✅ Salvar na pasta exclusiva "no_perfila"
        caminho = os.path.join(NO_PERFILA_DIR, f"{nif}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estrutura, f, ensure_ascii=False, indent=2)

        print(f"💾 JSON de não perfilamento salvo em: {caminho}")