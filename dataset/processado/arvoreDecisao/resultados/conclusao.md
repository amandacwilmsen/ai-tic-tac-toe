**A1 (tabuleiro):** configuração {'criterio': 'gini', 'max_depth': 8, 'min_leaf': 1}. F1 macro: treino 0.946, validação 0.519, teste 0.513; acurácia no teste 66.67%. Diferença treino–validação: 0.427. Treino médio 1.18 ms; previsão do lote 0.228 ms. Reconheceu 0 dos 3 empates do teste.

**A2 (características):** configuração {'criterio': 'gini', 'max_depth': 8, 'min_leaf': 1}. F1 macro: treino 0.980, validação 0.949, teste 0.925; acurácia no teste 90.32%. Diferença treino–validação: 0.032. Treino médio 1.08 ms; previsão do lote 0.248 ms. Reconheceu 3 dos 3 empates do teste.

**Recomendação:** A2 (características), pelo F1 macro de validação (0.949) e pelos critérios de desempate declarados. No teste, A2 superou A1 em 41.19 pontos percentuais de F1 macro. Esse resultado descreve as configurações selecionadas; não prova que A2 seja melhor em qualquer amostra.

**Interpretação:** a maior diferença treino–validação de A1 é um indício de sobreajuste nesta representação. A2 reduziu essa diferença com a mesma profundidade máxima e tamanho mínimo de folha selecionados. O ganho não decorre apenas de aumentar a complexidade da árvore. A estrutura é interpretável, mas a limitação das características impede afirmar ausência de sobreajuste.

**Custo e limitações:** as configurações de A1 e A2 podem ter complexidades diferentes. Interpretamos os tempos junto com seus parâmetros e a dispersão das medições. Há somente dois empates na validação e três no teste; a reamostragem não cria diversidade. A2 possui cinco grupos de entradas iguais com rótulos diferentes no treino. Possíveis simetrias entre divisões também limitam a análise.
