**A1 (tabuleiro):** configuração {'k': 7, 'metrica': 'manhattan', 'pesos': 'uniform'}. F1 macro: treino 0.829, validação 0.652, teste 0.517; acurácia no teste 65.59%. Diferença treino–validação: 0.177. Treino médio 0.72 ms; previsão do lote 1.001 ms. Reconheceu 0 dos 3 empates do teste.

**A2 (características):** configuração {'k': 3, 'metrica': 'manhattan', 'pesos': 'uniform'}. F1 macro: treino 0.948, validação 0.886, teste 0.907; acurácia no teste 88.17%. Diferença treino–validação: 0.061. Treino médio 1.30 ms; previsão do lote 1.128 ms. Reconheceu 3 dos 3 empates do teste.

**Recomendação:** A2 (características), pelo F1 macro de validação (0.886) e pelos critérios de desempate declarados. No teste, A2 superou A1 em 39.00 pontos percentuais de F1 macro. Esse resultado descreve as configurações selecionadas; não prova que A2 seja melhor em qualquer amostra.

**Interpretação:** A2 selecionou três vizinhos e a distância de Manhattan. O F1 de treino superior ao de validação sugere atenção à generalização. As repetições de empates participam dos votos, e características iguais podem tornar a decisão sensível a empates entre vizinhos. A padronização de A2 pertence ao Pipeline e foi ajustada apenas no treino.

**Custo e limitações:** as configurações de A1 e A2 podem ter complexidades diferentes. Interpretamos os tempos junto com seus parâmetros e a dispersão das medições. Há somente dois empates na validação e três no teste; a reamostragem não cria diversidade. A2 possui cinco grupos de entradas iguais com rótulos diferentes no treino. Possíveis simetrias entre divisões também limitam a análise.
