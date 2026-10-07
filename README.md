# CredAIR — Análise de Risco de Crédito

Projeto de Ciência de Dados que usa o histórico de propostas de crédito da **CredAIR** (financeira fictícia) para entender os fatores ligados à inadimplência e construir um modelo de **Regressão Logística** que identifique propostas de maior risco.

> Desafio 1 da trilha **Fast Track - IA | Turma 1**. Enunciado original: [desafios/analise-credito](https://github.com/LucasKiraly/fast-track-ia-t1/tree/main/desafios/analise-credito).
> Os dados são **sintéticos** e foram criados apenas para fins educacionais.

## Estrutura do projeto

```text
CredAIR-Alex/
├── data/
│   ├── raw/            # Dados originais. Nunca são alterados.
│   └── processed/      # Dados tratados, gerados pelo notebook (fora do Git)
├── notebooks/          # Notebook principal da análise (entregável)
├── reports/figures/    # Gráficos exportados para a apresentação
├── docs/               # Roadmap e registro de decisões
├── .vscode/            # Configurações e extensões recomendadas do VS Code
├── requirements.txt    # Dependências com versões fixadas
└── README.md
```

## Como executar

Pré-requisitos: **Python 3.11+** e **VS Code** com as extensões recomendadas (o VS Code sugere a instalação ao abrir a pasta).

```bash
# 1. Clonar o repositório
git clone https://github.com/alexlourenc/CredAIR-Alex.git
cd CredAIR-Alex

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

# 3. Instalar as dependências
pip install -r requirements.txt
```

Depois, abra o notebook em `notebooks/` no VS Code e selecione o kernel do `.venv`.

## Andamento

O projeto é desenvolvido em fases. Veja o [roadmap e o registro de decisões](docs/ROADMAP.md).
