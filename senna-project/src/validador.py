import os
import json
import numpy as np
from config import Config

# Pastas de saída
NO_PERFILA_DIR = os.path.join(Config.MAPS_DIR, "no_perfila")
os.makedirs(NO_PERFILA_DIR, exist_ok=True)

# Conversor robusto
def _converter_json(obj):
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    return str(obj)

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

            outras = grupo[
                (grupo["instituicao"] == row["instituicao"]) & (
                    (grupo["litigio"].astype(str).str.strip().str.lower() == "sim") |
                    (grupo["garantias"].fillna(0).astype(float) > 0)
                )
            ]
            if not outras.empty:
                motivos.append("Instituição tem outra dívida com garantia/litigio")

            dividas_com_motivos.append({
                "instituicao": row["instituicao"],
                "valor": float(row["divida"]),
                "motivos_reprovacao": list(set(motivos)) or ["Regras de perfilamento não atendidas"]
            })

        estrutura = {
            "resumo": {
                "nif": nif,
                "divida_total_elegivel": float(grupo["divida"].sum()),
                "perfila": False
            },
            "motivos": dividas_com_motivos
        }

        caminho = os.path.join(NO_PERFILA_DIR, f"{nif}.json")
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(estrutura, f, ensure_ascii=False, indent=2, default=_converter_json)
            print(f"💾 JSON de não perfilamento salvo em: {caminho}")
        except Exception as e:
            print(f"❌ Erro ao salvar JSON de {nif}: {e}")