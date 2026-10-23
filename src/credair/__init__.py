"""CredAIR: funções de limpeza, engenharia de atributos e modelagem de risco de crédito.

As regras foram validadas no notebook `notebooks/analise_credito.ipynb` (fases 3 a 8)
e consolidadas aqui para serem reaproveitadas e testadas.
"""

from credair.atributos import criar_atributos
from credair.limpeza import limpar
from credair.modelo import escolher_limiar, metricas, modelo_logistico

__all__ = ["limpar", "criar_atributos", "modelo_logistico", "metricas", "escolher_limiar"]
