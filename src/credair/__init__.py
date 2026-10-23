"""CredAIR: funções de limpeza, engenharia de atributos e modelagem de risco de crédito.

As regras foram validadas no notebook `notebooks/analise_credito.ipynb` (fases 3 a 8)
e consolidadas aqui para serem reaproveitadas e testadas.
"""

from importlib import import_module

# Importação sob demanda: o simulador no Vercel usa limpeza e atributos sem carregar o scikit-learn
_ORIGEM = {
    "limpar": "credair.limpeza",
    "criar_atributos": "credair.atributos",
    "modelo_logistico": "credair.modelo",
    "metricas": "credair.modelo",
    "escolher_limiar": "credair.modelo",
    "avaliar": "credair.simulador",
}

__all__ = list(_ORIGEM)


def __getattr__(nome):
    if nome in _ORIGEM:
        return getattr(import_module(_ORIGEM[nome]), nome)
    raise AttributeError(f"module 'credair' has no attribute {nome!r}")
