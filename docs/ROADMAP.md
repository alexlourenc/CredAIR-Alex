# Roadmap e registro de decisões

## Visão geral

O projeto evolui em três blocos. Cada um só começa quando o anterior estiver concluído.

| Bloco | Objetivo | Fases |
|---|---|---|
| **A. Análise (entregável do desafio)** | Notebook completo e executável + apresentação | 0 a 9 |
| **B. Código reutilizável** | Transformar o que foi validado no notebook em módulos Python testados | 10 |
| **C. Aplicação** | Disponibilizar o modelo para uso (ex.: simulador de propostas) | 11 |

**Por que nessa ordem?** O notebook é onde **exploramos e decidimos**; o código em módulos é onde **consolidamos** o que já foi decidido. Criar a aplicação antes de entender os dados seria construir em cima de suposições. Além disso, o notebook é o entregável obrigatório do desafio, então ele vem primeiro.

## Fases

| # | Fase | Commit esperado | Status |
|---|---|---|---|
| 0 | Setup do projeto | `chore: estrutura inicial do projeto` | ✅ |
| 0.1 | Estrutura em camadas (medalhão) | `chore: adota estrutura de dados em camadas medalhao` | ✅ |
| 1 | Entendimento do problema | `docs: entendimento do problema` | ⬜ |
| 2 | Diagnóstico de qualidade dos dados | `feat: diagnostico de qualidade dos dados` | ⬜ |
| 3 | Limpeza e preparação → gera camada 🥈 prata | `feat: realiza limpeza dos dados` | ⬜ |
| 4 | Análise exploratória | `feat: adiciona analise exploratoria` | ⬜ |
| 5 | Engenharia de atributos → gera camada 🥇 ouro | `feat: cria atributos para o modelo` | ⬜ |
| 6 | Preparação para modelagem | `feat: prepara dados para modelagem` | ⬜ |
| 7 | Modelagem (baseline + Regressão Logística) | `feat: desenvolve modelo` | ⬜ |
| 8 | Avaliação e interpretação | `feat: adiciona avaliacao do modelo` | ⬜ |
| 9 | Conclusão e apresentação | `docs: adiciona conclusao e apresentacao` | ⬜ |
| 10 | Refatoração para `src/` + testes | `refactor: extrai pipeline para modulo` | ⬜ |
| 11 | Aplicação | `feat: cria aplicacao de simulacao` | ⬜ |

## Registro de decisões

Cada decisão importante fica registrada aqui com o contexto, a escolha feita e o motivo. Esse registro também serve de roteiro para a apresentação.

### D01 — Ferramenta de desenvolvimento: VS Code + notebook Jupyter
- **Contexto:** o desafio exige um notebook; existe a intenção de evoluir para uma aplicação.
- **Decisão:** desenvolver no VS Code, com notebooks pela extensão Jupyter.
- **Motivo:** o mesmo editor atende à análise (notebook) e ao código de aplicação (arquivos `.py`, testes, Git integrado). O Colab seria mais simples no início, mas dificultaria a fase de aplicação.

### D02 — Estrutura de pastas separando dados brutos de dados tratados *(substituída pela D06)*
- **Decisão:** `data/raw/` (imutável, versionado) e `data/processed/` (gerado, fora do Git).
- **Motivo:** garante que a análise sempre possa ser refeita do zero a partir do dado original. Se o dado bruto fosse sobrescrito, perderíamos a referência para auditar a limpeza.

### D03 — Dataset mantido com o nome original `dataset.csv`
- **Contexto:** o enunciado cita `credito.csv`, mas o arquivo fornecido se chama `dataset.csv`.
- **Decisão:** manter o nome original.
- **Motivo:** dado bruto deve ser preservado exatamente como recebido (inclusive o nome), facilitando a rastreabilidade. A divergência fica documentada.
- **Integridade (SHA-256):** `5f50b73c2ece0d0ad9baeafef685e4e555c2cabfa2e80e0e3eac38546c8d6724`

### D04 — Dependências com versões fixadas
- **Decisão:** `requirements.txt` com `==` em cada biblioteca, dentro de um ambiente virtual (`.venv`).
- **Motivo:** reprodutibilidade. O enunciado exige que o notebook rode do início ao fim; versões diferentes de pandas/scikit-learn podem mudar resultados ou quebrar código.

### D05 — Estrutura mínima, sem pastas antecipadas
- **Decisão:** `src/`, `tests/` e `app/` só serão criados nas fases 10 e 11.
- **Motivo:** evitar estrutura vazia "para o futuro". Cada pasta surge quando houver conteúdo real para ela.

### D06 — Modelo medalhão (bronze, prata, ouro) em versão leve
- **Contexto:** a D02 separava apenas dado bruto e dado tratado. Na prática, existem dois "tratados" diferentes: o dado **limpo** (Fase 3) e o dado **pronto para o modelo** (Fase 5). Além disso, a futura aplicação precisará reaplicar as mesmas regras a propostas novas.
- **Decisão:** organizar os dados em três camadas:
  - 🥉 `data/bronze/`: dado como recebido; versionado e nunca alterado.
  - 🥈 `data/silver/`: dado limpo e validado, saída da Fase 3.
  - 🥇 `data/gold/`: tabela de modelagem com variáveis derivadas, saída da Fase 5.
- **Motivo:** cada camada tem uma responsabilidade única, o que facilita auditar ("por que este registro sumiu?" → compare bronze e prata), contar a história da análise e reaproveitar as regras na aplicação.
- **Por que "leve":** o medalhão nasceu em *lakehouses* (Spark, Delta Lake) com muitas fontes e cargas incrementais. Com um CSV de 5.000 linhas, pastas e arquivos bastam; usar essa infraestrutura seria complexidade sem ganho.
- **Formato:** Parquet nas camadas prata e ouro, porque preserva os tipos das colunas (o CSV não guarda tipos: ao reler, o pandas precisa adivinhá-los, e uma categoria ou data pode voltar como texto). Exige a dependência `pyarrow`.
- **Versionamento:** prata e ouro ficam fora do Git, pois são reproduzíveis a partir da bronze executando o notebook.
- **⚠️ Regra contra vazamento de dados (data leakage):** a camada ouro guarda apenas transformações **determinísticas, linha a linha** (ex.: `comprometimento_renda = parcela / renda`). Transformações que **aprendem estatísticas** dos dados, como imputação pela mediana, padronização e *one-hot encoding*, ficam no `Pipeline` do scikit-learn e são ajustadas **somente no conjunto de treino**, depois da divisão treino/teste. Se ficassem na ouro, o modelo "veria" informações do teste e as métricas sairiam otimistas.
