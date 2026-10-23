"""Simulação de propostas novas com o modelo final (Fase 11, decisão D14).

O treino usa o scikit-learn, mas a avaliação de uma proposta usa só os parâmetros aprendidos
(medianas, médias, desvios, coeficientes e limiar). Assim a função do Vercel não precisa do
scikit-learn, que deixaria o pacote da função acima do limite de tamanho.
"""

import numpy as np
import pandas as pd

from credair.atributos import criar_atributos
from credair.config import ALVO, BRONZE, RANDOM_STATE, VARIAVEIS_FINAIS
from credair.limpeza import limpar

# Campos que o simulador pede: as variáveis do modelo final, menos a derivada (comprometimento_renda)
CAMPOS = ["idade", "renda_mensal", "tempo_emprego_anos", "score_credito", "valor_solicitado",
          "prazo_meses", "dividas_ativas"]


def treinar_modelo_final():
    # Refaz o treino do notebook: mesma divisão 80/20, mesmo modelo e mesmo limiar (seções 6 a 8)
    from sklearn.model_selection import train_test_split

    from credair.modelo import escolher_limiar, modelo_logistico

    ouro = criar_atributos(limpar(pd.read_csv(BRONZE))[0])
    X_treino, _, y_treino, _ = train_test_split(ouro[VARIAVEIS_FINAIS], ouro[ALVO], test_size=0.2,
                                                stratify=ouro[ALVO], random_state=RANDOM_STATE)
    modelo = modelo_logistico(VARIAVEIS_FINAIS, []).fit(X_treino, y_treino)
    limiar = escolher_limiar(modelo_logistico(VARIAVEIS_FINAIS, []), X_treino, y_treino)
    return modelo, limiar


def exportar_parametros(modelo, limiar) -> dict:
    # Extrai do pipeline treinado tudo o que a avaliação precisa, em um formato que cabe num JSON
    numericas = modelo.named_steps["preparar"].named_transformers_["num"]
    regressao = modelo.named_steps["modelo"]
    return {
        "variaveis": VARIAVEIS_FINAIS,
        "mediana": numericas.named_steps["imputar"].statistics_.tolist(),
        "media": numericas.named_steps["padronizar"].mean_.tolist(),
        "desvio": numericas.named_steps["padronizar"].scale_.tolist(),
        "coeficientes": regressao.coef_[0].tolist(),
        "intercepto": float(regressao.intercept_[0]),
        "limiar": limiar,
    }


def avaliar(proposta: dict, parametros: dict) -> dict:
    # Aplica limpeza, atributos e modelo a uma proposta e explica o resultado
    faltando = [c for c in CAMPOS if proposta.get(c) is None]
    if faltando:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(faltando)}")
    if float(proposta["prazo_meses"]) < 1:
        raise ValueError("O prazo deve ser de pelo menos 1 mês")

    # Colunas fora do modelo ficam vazias: a limpeza precisa delas, mas elas não afetam o resultado
    bronze = pd.DataFrame([{c: float(proposta[c]) for c in CAMPOS}])
    bronze[["estado", "escolaridade", "finalidade"]] = None
    prata, log = limpar(bronze)
    ouro = criar_atributos(prata)

    # Mesmas etapas do pipeline: imputação pela mediana, padronização e regressão logística
    x = ouro[parametros["variaveis"]].to_numpy(dtype=float)[0]
    x = np.where(np.isnan(x), parametros["mediana"], x)
    z = (x - np.array(parametros["media"])) / np.array(parametros["desvio"])
    contribuicoes = np.array(parametros["coeficientes"]) * z
    prob = float(1 / (1 + np.exp(-(parametros["intercepto"] + contribuicoes.sum()))))

    # Contribuição de cada variável para o log-odds, em relação a uma proposta média do treino
    fatores = sorted(({"variavel": v, "contribuicao": float(c)}
                      for v, c in zip(parametros["variaveis"], contribuicoes)),
                     key=lambda f: abs(f["contribuicao"]), reverse=True)

    # Avisos dos problemas P3 a P5: o valor informado vira ausente e o modelo usa a mediana do treino
    avisos = log[log["problema"].isin(["P3", "P4", "P5"]) & (log["registros"] > 0)]["tratamento"].tolist()

    comprometimento = ouro.loc[0, "comprometimento_renda"]
    return {
        "probabilidade": prob,
        "limiar": parametros["limiar"],
        "alto_risco": prob >= parametros["limiar"],
        "parcela_estimada": float(ouro.loc[0, "parcela_estimada"]),
        "comprometimento_renda": None if pd.isna(comprometimento) else float(comprometimento),
        "fatores": fatores,
        "avisos": avisos,
    }


if __name__ == "__main__":
    # Gera o arquivo de parâmetros usado pela função do Vercel: python -m credair.simulador
    import json

    from credair.config import RAIZ

    destino = RAIZ / "api" / "modelo_final.json"
    destino.write_text(json.dumps(exportar_parametros(*treinar_modelo_final()), indent=2) + "\n")
    print(f"Parâmetros salvos em {destino.relative_to(RAIZ)}")
