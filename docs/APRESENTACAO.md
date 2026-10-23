# Roteiro da apresentação: CredAIR, análise de risco de crédito

**Formato:** reunião individual no Microsoft Teams, com cerca de 15 minutos de fala.
**Fio condutor:** contar a **história da análise**, deixando claro o **porquê de cada decisão**.

Os slides estão em [`apresentacao.pdf`](apresentacao.pdf). Os gráficos citados estão em `reports/figures/`.

---

## 1. O problema (1 min)
- **Contexto:** a CredAIR quer usar o histórico de propostas para identificar as de **maior risco de inadimplência**.
- **Variável resposta:** `inadimplente` (0/1). É um problema de **classificação binária supervisionada**.
- **O ponto-chave:** os erros não custam o mesmo. **Aprovar um mau pagador** (falso negativo) custa o capital emprestado. **Recusar um bom pagador** (falso positivo) custa os juros e o cliente.
- 📊 `01_distribuicao_alvo.png`: 34,4% de inadimplentes. Quem chuta sempre "adimplente" acerta 66% sem aprender nada, e por isso **a acurácia engana**.

## 2. Como organizei o projeto (1 min)
- Desenvolvimento em **fases**, com um commit por fase (Conventional Commits).
- **Medalhão leve:** 🥉 bronze (dado como recebido), 🥈 prata (limpo) e 🥇 ouro (pronto para o modelo).
- **Regra contra vazamento de dados:** a camada ouro só tem transformações linha a linha. Imputação e escala ficam no `Pipeline` e são ajustadas **só no treino**.

## 3. Qualidade dos dados (2 min)
- **Diagnosticar antes de tratar.** Problemas encontrados:
  - 19 duplicatas e 101 UFs com espaços (`' MG '` virava um estado diferente de `'MG'`);
  - 15 idades impossíveis (210 a 750 anos), 8 tempos de emprego ≥ idade e 10 rendas artificiais (R$ 100 a R$ 550).
- **Decisão: marcar como ausente** e imputar no pipeline, em vez de apagar a linha ou "adivinhar" o valor.
  - *Por que não dividir a idade por 10?* Porque algumas idades corrigidas ficariam incoerentes com o tempo de emprego.
- **Decisão: manter** cerca de 690 casos de início de trabalho antes dos 14 anos. Removê-los enviesaria a base contra os jovens. Ficou registrado como **limitação**.

## 4. O que os dados mostram (3 min)
- 📊 `03_taxa_por_quintil.png`: **score** (56% → 16% de inadimplência) e **renda** (53% → 21%) são os sinais mais fortes.
- 📊 `04_taxa_por_categoria.png`: mais **dívidas ativas** significam mais risco (27% → 61%). **Prazos curtos** têm mais inadimplência (55% em 6 meses), um resultado contraintuitivo.
- **Estado, escolaridade e finalidade:** o teste qui-quadrado não mostrou associação significativa (p de 0,23 a 0,60).
- *Ressalva:* correlação não é causalidade.

## 5. A variável que criei (2 min), o ponto alto da análise
- **Hipótese:** o prazo curto não é arriscado por si mesmo; ele gera uma **parcela pesada**.
- **`comprometimento_renda` = (valor ÷ prazo) ÷ renda**, a fração da renda que vai para a parcela.
- 📊 `06_comprometimento_renda.png`: a inadimplência sobe de 21% para **71%** do menor para o maior decil.
- Resultado: é a 2ª variável mais forte sozinha e **eleva a AUC de 0,769 para 0,793**.

## 6. Modelagem (2 min)
- Treino/teste 80/20 **estratificado**. O teste só é usado no final.
- **Referências:** classe majoritária (AUC 0,50) e regra só com score (AUC 0,68 na validação cruzada; no teste, 0,695).
- **Validação cruzada (5 partes)** para comparar as configurações:
  - incluir `estado` não ajuda e ainda tem **risco ético**, então ficou fora;
  - escolaridade e finalidade não acrescentam nada, então ficou o **modelo mais simples (parcimônia)**, com 8 variáveis numéricas.

## 7. Resultados (3 min)
- 📊 `07_curva_roc.png`: **AUC de 0,781 no teste**, contra 0,695 da regra só com score no mesmo conjunto de teste. O valor fica próximo do 0,794 da validação cruzada, ou seja, o modelo **generaliza**.
- 📊 `08_matriz_confusao_05.png`: no limiar 0,5, o modelo pega só **45%** dos inadimplentes.
- 📊 `09_precisao_recall_limiar.png` e `10_matriz_confusao_sugerido.png`: com o **limiar 0,31**, escolhido no treino e não no teste, o modelo pega **74%** dos inadimplentes. A precisão cai de 68% para 56%.
- **O limiar é uma decisão de negócio.** A sugestão é mandar os casos sinalizados para **análise manual** ou ajustar as condições, em vez de recusar automaticamente.
- 📊 `11_coeficientes.png`, lido como odds ratio por desvio-padrão:
  - comprometimento da renda **2,78×** (fator de risco mais forte);
  - score **0,44×** (fator de proteção mais forte);
  - dívidas ativas **1,60×**.
- *Curiosidade:* o prazo "troca de sinal" no modelo multivariado. O efeito do prazo curto era, na verdade, o efeito da parcela pesada.

## 8. Conclusões, limitações e cuidados (1 min)
- **Ação prática:** para clientes no limite, oferecer **prazo maior ou valor menor** reduz o comprometimento e, com ele, o risco.
- **Limitações:**
  - dados sintéticos;
  - viés de seleção (só temos as propostas que foram analisadas);
  - parcela calculada sem juros;
  - nenhuma dimensão temporal.
- **Cuidados em produção:**
  - o modelo apoia a decisão, não decide sozinho;
  - justiça e LGPD;
  - monitorar *drift* e retreinar o modelo;
  - aplicar as mesmas regras de limpeza e atributos do treino.
- **Próximos passos:** levar o pipeline para um módulo testado e construir uma **aplicação de simulação** de propostas.

---

## Perguntas prováveis e respostas curtas

| Pergunta | Resposta |
|---|---|
| Por que não usou acurácia? | Com 34% de inadimplentes, quem chuta sempre "adimplente" tem 66% de acurácia. A AUC e o recall mostram se o modelo realmente separa as classes. |
| Por que imputar com a mediana? | Ela é robusta a valores extremos. Além disso, só 33 valores estavam ausentes, menos de 1% da base. |
| Por que padronizar? | A regressão logística regularizada penaliza os coeficientes. Sem escala, variáveis com unidades grandes, como a renda, seriam penalizadas de forma desigual. A escala também torna os coeficientes comparáveis. |
| O que é vazamento de dados? | É quando informação do teste "vaza" para o treino. Por exemplo, calcular a mediana com a base toda. As métricas ficam otimistas demais. O `Pipeline` evita isso. |
| Por que excluir o estado? | Não tem associação significativa, piora levemente o modelo e pode **discriminar regiões**. |
| Por que o limiar de 0,31? | Ele maximiza o F1 nas previsões de validação cruzada do treino. Prioriza pegar mais inadimplentes, que é o erro mais caro, mas a decisão final é do negócio. |
| O modelo está sobreajustado? | Não. A AUC no teste (0,781) é próxima da validação cruzada (0,794), e o desvio entre as partes é pequeno (±0,016). |
