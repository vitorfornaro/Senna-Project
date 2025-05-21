import pandas as pd
import json
import os
from config import Config  # Importa a configuração

class PDFOutputHandler:
    def __init__(self):
        self.csv_folder = os.path.join(Config.MAPS_DIR, "outputs", "csv")
        self.json_folder = os.path.join(Config.MAPS_DIR, "outputs", "json")
        self.client_json_folder = os.path.join(Config.MAPS_DIR, "customers")

        self.csv_path = os.path.join(self.csv_folder, "resultado_extracao.csv")
        self.json_path = os.path.join(self.json_folder, "resultado_extracao.json")

        os.makedirs(self.csv_folder, exist_ok=True)
        os.makedirs(self.json_folder, exist_ok=True)
        os.makedirs(self.client_json_folder, exist_ok=True)

    def save_to_csv(self, dataframe):
        if not dataframe.empty:
            mode = 'a' if os.path.exists(self.csv_path) else 'w'
            header = not os.path.exists(self.csv_path)
            dataframe.to_csv(self.csv_path, mode=mode, header=header, index=False)
            print(f"📄 Dados adicionados ao CSV: {self.csv_path}")
        else:
            print("⚠️ Nenhum dado a salvar no CSV.")

    def save_to_json(self, dataframe):
        if not dataframe.empty:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        existing_data = []
            else:
                existing_data = []

            new_data = dataframe.to_dict(orient="records")
            updated_data = existing_data + new_data

            with open(self.json_path, 'w', encoding='utf-8') as json_file:
                json.dump(updated_data, json_file, ensure_ascii=False, indent=4)
            print(f"🧾 Dados adicionados ao JSON geral: {self.json_path}")
        else:
            print("⚠️ Nenhum dado a salvar no JSON geral.")

    def save_json_by_client(self, dataframe):
        """Salva um arquivo JSON separado por NIF com bloco de resumo e lista de dívidas."""
        if dataframe.empty:
            print("⚠️ Nenhum dado válido para salvar por cliente.")
            return

        df_validos = dataframe[dataframe['nif'].notna()]
        clientes_salvos = 0

        for nif, group in df_validos.groupby("nif"):
            dividas = group.to_dict(orient="records")

            # Calcular resumo do perfilamento
            total_elegivel = sum(item["divida"] for item in dividas if item.get("perfil_individual"))
            perfila = total_elegivel >= 6000

            json_data = {
                "resumo": {
                    "nif": nif,
                    "divida_total_elegivel": round(total_elegivel, 2),
                    "perfila": perfila
                },
                "dividas": dividas
            }

            json_path = os.path.join(self.client_json_folder, f"{nif}.json")
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                clientes_salvos += 1
            except Exception as e:
                print(f"❌ Erro ao salvar JSON para NIF {nif}: {e}")

        print(f"\n✅ {clientes_salvos} arquivos JSON salvos no novo formato em: {self.client_json_folder}")