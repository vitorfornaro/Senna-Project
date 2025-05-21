import os
import json

def salvar_nao_perfilar(df, pasta_destino="maps/no_perfila/"):
    os.makedirs(pasta_destino, exist_ok=True)

    # Filtrar apenas os que não perfilam
    df_nao_perfilar = df[df["perfila"] == False]

    # Agrupar por NIF
    for nif, grupo in df_nao_perfilar.groupby("nif"):
        dividas = grupo.to_dict(orient="records")
        motivo = []

        for linha in dividas:
            razoes = []
            if not (linha["litigio"] or "").strip().lower() == "não":
                razoes.append("litigio != 'Não'")
            if linha["garantias"] and linha["garantias"] > 0:
                razoes.append("garantia > 0")
            if not razoes:
                razoes.append("reprovado por regra da instituição")

            linha["motivo_nao_perfilar"] = ", ".join(razoes)

        # Estrutura final
        output = {
            "nif": nif,
            "motivo_resumo": f"{len(dividas)} dividas não perfiladas",
            "dividas": dividas
        }

        # Caminho do JSON
        file_path = os.path.join(pasta_destino, f"{nif}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"📁 Reprovado salvo em: {file_path}")