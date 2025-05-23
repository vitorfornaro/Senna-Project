from dataclasses import asdict
import json
import os
import logging
from interface.cliente_modal import Bancario, Cliente
from utils.utils import nif_validation

# Configuração de log
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def extraiDadosCliente(data: Cliente):
    try:
        is_nif_valid = nif_validation(data.nif)
        if not is_nif_valid:
            logging.warning(f"NIF inválido: {data.nif}")
            return

        if not data.bancario or len(data.bancario) == 0:
            logging.warning(f"Nenhum dado bancário encontrado para o NIF: {data.nif}")
            return

        bancario = data.bancario[0]

        cliente = Cliente(
            nome=data.nome,
            nif=data.nif,
            bancario=[
                Bancario(
                    mesMapa=bancario.mesMapa,
                    instituicao=bancario.instituicao,
                    divida=bancario.divida,
                    parcela=bancario.parcela,
                    garantias=bancario.garantias,
                    num_devedores=bancario.num_devedores,
                    prod_financeiro=bancario.prod_financeiro,
                    entrada_incumpr=bancario.entrada_incumpr,
                    data_inicio=bancario.data_inicio,
                    data_fim=bancario.data_fim,
                )
            ],
        )

        cliente_dict = asdict(cliente)
        folder_customers = "customers"
        os.makedirs(folder_customers, exist_ok=True)

        output_path = os.path.join(folder_customers, f"{data.nif}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cliente_dict, f, ensure_ascii=False, indent=2)

        logging.info(f"✅ Cliente {data.nif} salvo com sucesso em {output_path}")

    except Exception as e:
        logging.error(f"Erro ao salvar cliente {data.nif}: {e}")