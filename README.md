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
├── notebooks/          # Notebook principal da análise (entregável)
├── reports/figures/    # Gráficos exportados para a apresentação
├── docs/               # Roadmap e registro de decisões
├── .vscode/            # Configurações e extensões recomendadas do VS Code
├── requirements.txt    # Dependências com versões fixadas
└── README.md
```

## Arquitetura de dados: modelo medalhão

Os dados passam por três camadas, cada uma com uma responsabilidade:

| Camada | Conteúdo | Gerada na |
|---|---|---|
| 🥉 Bronze | `dataset.csv` exatamente como recebido | (fonte) |
| 🥈 Prata | Dados limpos: tipos corretos, sem duplicatas, inconsistências tratadas | Fase 3 — Limpeza |
| 🥇 Ouro | Tabela para modelagem, com as variáveis derivadas | Fase 5 — Engenharia de atributos |

Transformações que "aprendem" com os dados (padronização, imputação, *one-hot encoding*) **não** ficam na camada ouro: são ajustadas apenas no conjunto de treino, dentro do `Pipeline` do scikit-learn, para evitar vazamento de dados. Detalhes na decisão D06 do [roadmap](docs/ROADMAP.md).

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
