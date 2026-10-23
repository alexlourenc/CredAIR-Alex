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
| 1 | Entendimento do problema | `feat: inicia analise com entendimento do problema` | ✅ |
| 2 | Diagnóstico de qualidade dos dados | `feat: adiciona diagnostico de qualidade dos dados` | ✅ |
| 3 | Limpeza e preparação → gera camada 🥈 prata | `feat: realiza limpeza dos dados e gera camada prata` | ✅ |
| 4 | Análise exploratória | `feat: adiciona analise exploratoria` | ✅ |
| 5 | Engenharia de atributos → gera camada 🥇 ouro | `feat: cria atributos e gera camada ouro` | ✅ |
| 6 | Preparação para modelagem | `feat: prepara dados para modelagem` | ✅ |
| 7 | Modelagem (baseline + Regressão Logística) | `feat: desenvolve modelo de regressao logistica` | ✅ |
| 8 | Avaliação e interpretação | `feat: adiciona avaliacao e interpretacao do modelo` | ✅ |
| 9 | Conclusão e apresentação | `docs: adiciona conclusao da analise` + `docs: adiciona roteiro da apresentacao` | ✅ |
| 10 | Refatoração para `src/` + testes | `refactor: extrai pipeline para modulo` | ✅ |
| 11 | Aplicação | `feat: cria aplicacao de simulacao` | ✅ |

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

### D07 — Problemas de qualidade marcados como ausentes, e não removidos nem "corrigidos"
- **Contexto:** idades de 210 a 750 anos, tempo de emprego ≥ idade e rendas artificiais (R$ 100 a R$ 550, de 50 em 50).
- **Decisão:** converter esses valores em `NaN` e imputar pela **mediana dentro do pipeline**, ajustada só no treino.
- **Alternativas descartadas:** remover a linha (perderia as outras colunas, que estão corretas) e dividir a idade por 10 (suposição que gera novas incoerências com o tempo de emprego).
- **Mantidos:** ~690 casos de início de trabalho antes dos 14 anos, para não enviesar a base contra os jovens (registrado como limitação), e valores repetidos plausíveis (renda de R$ 900 e R$ 30 mil, valor de R$ 50 mil).

### D08 — Variável derivada `comprometimento_renda`
- **Construção:** `(valor_solicitado / prazo_meses) / renda_mensal`, a fração da renda comprometida com a parcela, sem juros.
- **Motivo:** explica o "paradoxo do prazo" (prazos curtos geram parcelas pesadas). É a 2ª variável mais discriminante sozinha (AUC 0,667) e eleva a AUC do modelo de 0,769 para 0,793 na validação cruzada.

### D09 — `estado` excluído do modelo
- **Motivo:** sem associação significativa (qui-quadrado, p = 0,60), 26 *dummies* com risco de sobreajuste e **risco ético e regulatório** de discriminação regional. Testado na validação cruzada: não melhora o modelo (AUC 0,788).

### D10 — Modelo final só com variáveis numéricas (parcimônia)
- **Motivo:** retirar `escolaridade` e `finalidade` não altera o desempenho (AUC 0,794 contra 0,793, dentro do desvio). O modelo mais simples é mais explicável e menos sujeito a sobreajuste.

### D11 — Configurações comparadas com validação cruzada; teste usado só no final
- **Motivo:** escolher o modelo pelo teste o tornaria otimista. Validação cruzada estratificada com 5 partes no treino, métrica ROC-AUC (independe do limiar).

### D12 — Limiar de decisão escolhido no treino (F1 máximo nas previsões fora da amostra)
- **Resultado:** limiar de 0,31. No teste, o recall sobe de 45% para 74%, e a precisão cai de 68% para 56%.
- **Motivo:** o falso negativo (aprovar um mau pagador) é o erro mais caro. O limiar final é uma **decisão de negócio** e deve ser revisto com os custos reais.

### D13 — Regras do notebook consolidadas no pacote `credair`
- **Contexto:** a Fase 11 (aplicação) precisa aplicar a uma proposta nova exatamente as mesmas regras de limpeza, atributos e modelo do notebook. Copiar o código para a aplicação criaria duas versões que podem divergir.
- **Decisão:** mover `limpar`, `criar_atributos`, `modelo_logistico`, `metricas` e a escolha do limiar para `src/credair/`, com as constantes (caminhos, semente, listas de variáveis) em `config.py`. O notebook importa o pacote e mostra o código das funções principais com `inspect.getsource`, para continuar legível como entregável.
- **Instalação:** `pyproject.toml` + linha `-e .` no `requirements.txt`. O modo editável faz alterações em `src/` valerem sem reinstalar.
- **Testes:** `pytest` com dados pequenos montados à mão (um exemplo de cada problema P1 a P5) e um **teste de regressão** que refaz o pipeline inteiro a partir da bronze e confere ROC-AUC 0,781, recall 73,8% e limiar 0,31. Se uma mudança futura alterar os resultados, o teste avisa. Os testes rodam no GitHub Actions a cada push.
- **Conferência:** o notebook foi reexecutado do zero depois da mudança. As saídas e os 11 gráficos ficaram idênticos aos anteriores.

### D14 — Simulador publicado no Vercel, sem o scikit-learn na execução
- **Contexto:** a aplicação precisa ser acessível por um link, para que outras pessoas testem o modelo sem instalar nada.
- **Decisão:** página estática (`public/`) e uma função Python no Vercel (`api/simular.py`) que importa o pacote `credair` e aplica `limpar` e `criar_atributos` à proposta. A pasta `app/` prevista na D05 virou `api/` e `public/`, os nomes que o Vercel reconhece.
- **Por que sem o scikit-learn:** com scikit-learn, scipy, pandas e numpy a função ficou com 263 MB, acima do limite do Vercel. Uma regressão logística só precisa de medianas, médias, desvios, coeficientes e limiar, que são exportados do pipeline treinado para `api/modelo_final.json` (`python -m credair.simulador`). A conta feita com esses parâmetros reproduz exatamente o `predict_proba` do scikit-learn, e a função cai para cerca de 100 MB.
- **Alternativa descartada:** calcular tudo em JavaScript no navegador. Seria mais rápido, mas exigiria reescrever a limpeza e os atributos, criando a segunda versão das regras que a D13 quis evitar.
- **Testes:** conferem que a probabilidade calculada com o JSON é igual à do scikit-learn, que o JSON está atualizado em relação ao treino, que a limpeza (P3 a P5) é aplicada e que a função responde e rejeita propostas inválidas.
- **Explicação do resultado:** a página mostra a contribuição de cada variável (coeficiente × valor padronizado) em relação a uma proposta média do treino, para que a decisão não seja uma caixa-preta.
