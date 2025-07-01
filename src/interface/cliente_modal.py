from dataclasses import dataclass
from typing import List

@dataclass
class Bancario:
  mesMapa: str
  instituicao: str
  divida: float
  parcela: str
  garantias: float
  num_devedores: int
  prod_financeiro: str
  entrada_incumpr: str
  data_inicio: str
  data_fim: str

@dataclass
class Cliente:
  nome: str
  nif: str
  bancario: List[Bancario]
