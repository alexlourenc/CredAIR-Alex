# CredAIR — Análise de Risco de Crédito

Projeto de Ciência de Dados que usa o histórico de propostas de crédito da **CredAIR** (financeira fictícia) para entender os fatores ligados à inadimplência e construir um modelo de **Regressão Logística** que identifique propostas de maior risco.

> Desafio 1 da trilha **Fast Track - IA | Turma 1**. Enunciado original: [desafios/analise-credito](https://github.com/LucasKiraly/fast-track-ia-t1/tree/main/desafios/analise-credito).
> Os dados são **sintéticos** e foram criados apenas para fins educacionais.

## Estrutura do projeto

```text
CredAIR-Alex/
├── data/
│   ├── bronze/         # 🥉 Dado original, como recebido. Nunca é alterado.
│   ├── silver/         # 🥈 Dado limpo e validado (gerado pelo notebook, fora do Git)
│   └── gold/           # 🥇 Dado pronto para modelagem (gerado pelo notebook, fora do Git)
├── notebooks/
│   └── analise_credito.ipynb   # Notebook principal da análise (entregável)
├── src/credair/        # Pacote com as regras validadas no notebook
│   ├── config.py       #   caminhos, semente e listas de variáveis
│   ├── limpeza.py      #   bronze → prata
│   ├── atributos.py    #   prata → ouro
│   ├── modelo.py       #   pipeline, métricas e escolha do limiar
│   └── simulador.py    #   avaliação de uma proposta nova (simulador)
├── api/                # Função do simulador no Vercel + parâmetros do modelo final
├── public/             # Página do simulador
├── tests/              # Testes automatizados (pytest)
├── reports/figures/    # Gráficos exportados para a apresentação
├── docs/               # Roadmap e registro de decisões
├── .vscode/            # Configurações e extensões recomendadas do VS Code
├── vercel.json         # Configuração da publicação no Vercel
├── pyproject.toml      # Torna o pacote credair instalável
├── requirements.txt    # Dependências com versões fixadas (inclui o pacote credair)
└── README.md
```

## Principais resultados

| Modelo | ROC-AUC (teste) | Recall da classe inadimplente |
|---|---|---|
| Referência: classe majoritária | 0,500 | 0% |
| Referência: só score de crédito | 0,695 | 24% |
| **Regressão Logística (8 variáveis)** | **0,781** | **74%** (limiar 0,31) |

- **Fator de risco mais forte:** `comprometimento_renda`, a variável criada no projeto que mede a fração da renda comprometida com a parcela. Odds ratio de 2,78 por desvio-padrão.
- **Fator de proteção mais forte:** `score_credito`. Odds ratio de 0,44 por desvio-padrão.
- `estado`, `escolaridade` e `finalidade` não mostraram associação significativa e ficaram fora do modelo final.

Detalhes no [notebook](notebooks/analise_credito.ipynb), no [registro de decisões](docs/ROADMAP.md) e no [roteiro da apresentação](docs/APRESENTACAO.md).

## Arquitetura de dados: modelo medalhão

Os dados passam por três camadas, cada uma com uma responsabilidade:

| Camada | Conteúdo | Gerada na |
|---|---|---|
| 🥉 Bronze | `dataset.csv` exatamente como recebido | (fonte) |
| 🥈 Prata | Dados limpos: tipos corretos, sem duplicatas, inconsistências tratadas | Fase 3 — Limpeza |
| 🥇 Ouro | Tabela para modelagem, com as variáveis derivadas | Fase 5 — Engenharia de atributos |

Transformações que "aprendem" com os dados (padronização, imputação, *one-hot encoding*) **não** ficam na camada ouro: são ajustadas apenas no conjunto de treino, dentro do `Pipeline` do scikit-learn, para evitar vazamento de dados. Detalhes na decisão D06 do [roadmap](docs/ROADMAP.md).

## Como executar

Pré-requisitos: **Python 3.12+** (o numpy fixado no `requirements.txt` não tem versão para o 3.11) e **VS Code** com as extensões recomendadas (o VS Code sugere a instalação ao abrir a pasta).

```bash
# 1. Clonar o repositório
git clone https://github.com/alexlourenc/CredAIR-Alex.git
cd CredAIR-Alex

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

# 3. Instalar as dependências (inclui o pacote credair, da pasta src/)
pip install -r requirements.txt
```

Depois, abra `notebooks/analise_credito.ipynb` no VS Code, selecione o kernel do `.venv` e use **Run All**. O notebook gera as camadas prata e ouro em `data/` e os gráficos em `reports/figures/`.

O notebook importa as funções do pacote `credair` (pasta `src/`). Para rodar os testes:

```bash
pytest
```

Os testes conferem cada regra de limpeza e de engenharia de atributos e verificam se o modelo continua reproduzindo os resultados publicados acima (ROC-AUC de 0,781 e limiar de 0,31). Eles também rodam automaticamente no GitHub a cada push.

## Simulador de propostas

O simulador (pastas `api/` e `public/`) é uma página onde se informa uma proposta e se vê a probabilidade de inadimplência, a decisão pelo limiar de 0,31 e o que mais pesou na avaliação. Ela aplica as mesmas regras de limpeza e de atributos do pacote `credair` e é publicada no Vercel.

Para testar no computador:

```bash
python api/simular.py          # depois abra http://localhost:8000
```

Se o modelo mudar, regenere os parâmetros usados pelo simulador (um teste avisa quando o arquivo fica desatualizado):

```bash
python -m credair.simulador
```

## Andamento

O projeto é desenvolvido em fases. Veja o [roadmap e o registro de decisões](docs/ROADMAP.md).
