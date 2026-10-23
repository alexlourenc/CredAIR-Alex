import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import numpy as np
import pandas as pd
import pytest

from credair.config import RAIZ, VARIAVEIS_FINAIS
from credair.simulador import avaliar, exportar_parametros, treinar_modelo_final

PROPOSTA = {"idade": 30, "renda_mensal": 3000, "tempo_emprego_anos": 5, "score_credito": 700,
            "valor_solicitado": 12000, "prazo_meses": 24, "dividas_ativas": 0}


@pytest.fixture(scope="module")
def treinado():
    return treinar_modelo_final()


@pytest.fixture(scope="module")
def parametros(treinado):
    return exportar_parametros(*treinado)


def test_usa_o_limiar_do_notebook(parametros):
    assert parametros["limiar"] == pytest.approx(0.31)


def test_json_do_vercel_esta_atualizado(parametros):
    # Se este teste falhar, rode `python -m credair.simulador` para regenerar o arquivo
    salvo = json.loads((RAIZ / "api" / "modelo_final.json").read_text())
    assert salvo.keys() == parametros.keys()
    assert salvo["variaveis"] == parametros["variaveis"]
    for chave in salvo.keys() - {"variaveis"}:
        # Tolerância pequena: o treino pode variar na última casa decimal entre máquinas
        assert salvo[chave] == pytest.approx(parametros[chave], rel=1e-6), chave


@pytest.mark.parametrize("ajuste", [{}, {"score_credito": 400, "dividas_ativas": 5},
                                    {"idade": 250, "renda_mensal": 300}, {"prazo_meses": 6}])
def test_mesma_probabilidade_do_scikit_learn(treinado, parametros, ajuste):
    # A conta feita com os parâmetros exportados reproduz o pipeline treinado
    from credair import criar_atributos, limpar
    proposta = {**PROPOSTA, **ajuste}
    bronze = pd.DataFrame([proposta]).assign(estado=None, escolaridade=None, finalidade=None)
    ouro = criar_atributos(limpar(bronze)[0])
    esperado = treinado[0].predict_proba(ouro[VARIAVEIS_FINAIS])[0, 1]
    assert avaliar(proposta, parametros)["probabilidade"] == pytest.approx(esperado)


def test_avalia_proposta(parametros):
    r = avaliar(PROPOSTA, parametros)
    assert 0 < r["probabilidade"] < 1
    assert r["alto_risco"] == (r["probabilidade"] >= r["limiar"])
    # 12.000 em 24 meses = parcela de 500; 500 / 3.000 de renda = 1/6
    assert r["parcela_estimada"] == pytest.approx(500)
    assert r["comprometimento_renda"] == pytest.approx(1 / 6)
    assert r["avisos"] == []


def test_contribuicoes_somam_o_log_odds(parametros):
    r = avaliar(PROPOSTA, parametros)
    log_odds = parametros["intercepto"] + sum(f["contribuicao"] for f in r["fatores"])
    assert 1 / (1 + np.exp(-log_odds)) == pytest.approx(r["probabilidade"])


def test_score_baixo_aumenta_o_risco(parametros):
    risco = avaliar({**PROPOSTA, "score_credito": 400}, parametros)
    assert risco["probabilidade"] > avaliar(PROPOSTA, parametros)["probabilidade"]


def test_aplica_a_limpeza_do_notebook(parametros):
    # P3 e P5: idade de 250 anos e renda de R$ 300 viram ausentes e o modelo usa a mediana
    r = avaliar({**PROPOSTA, "idade": 250, "renda_mensal": 300}, parametros)
    assert len(r["avisos"]) == 2
    assert r["comprometimento_renda"] is None
    assert 0 < r["probabilidade"] < 1


@pytest.mark.parametrize("ajuste", [{"idade": None}, {"prazo_meses": 0}, {"renda_mensal": "abc"}])
def test_rejeita_proposta_invalida(parametros, ajuste):
    with pytest.raises(ValueError):
        avaliar({**PROPOSTA, **ajuste}, parametros)


def test_funcao_do_vercel(parametros):
    from api.simular import handler
    servidor = ThreadingHTTPServer(("localhost", 0), handler)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    url = f"http://localhost:{servidor.server_port}/api/simular"
    try:
        pedido = urllib.request.Request(url, data=json.dumps(PROPOSTA).encode(), method="POST")
        with urllib.request.urlopen(pedido) as resposta:
            esperado = avaliar(PROPOSTA, parametros)["probabilidade"]
            assert json.load(resposta)["probabilidade"] == pytest.approx(esperado)
        pedido = urllib.request.Request(url, data=json.dumps({**PROPOSTA, "prazo_meses": 0}).encode(), method="POST")
        with pytest.raises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(pedido)
        assert erro.value.code == 400
    finally:
        servidor.shutdown()
