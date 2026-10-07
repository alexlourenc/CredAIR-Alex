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
| 1 | Entendimento do problema | `docs: entendimento do problema` | ⬜ |
| 2 | Diagnóstico de qualidade dos dados | `feat: diagnostico de qualidade dos dados` | ⬜ |
| 3 | Limpeza e preparação | `feat: realiza limpeza dos dados` | ⬜ |
| 4 | Análise exploratória | `feat: adiciona analise exploratoria` | ⬜ |
| 5 | Engenharia de atributos | `feat: cria atributos para o modelo` | ⬜ |
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

### D02 — Estrutura de pastas separando dados brutos de dados tratados
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
