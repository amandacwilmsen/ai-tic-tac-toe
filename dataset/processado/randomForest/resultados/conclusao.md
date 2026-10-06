**A1 (tabuleiro):** configuração {'n_arvores': 200, 'max_depth': None, 'min_leaf': 2}. F1 macro: treino 0.993, validação 0.767, teste 0.706; acurácia no teste 75.27%. Diferença treino–validação: 0.226. Treino médio 131.32 ms; previsão do lote 6.066 ms. Reconheceu 2 dos 3 empates do teste.

**A2 (características):** configuração {'n_arvores': 10, 'max_depth': None, 'min_leaf': 1}. F1 macro: treino 0.986, validação 0.940, teste 0.924; acurácia no teste 90.32%. Diferença treino–validação: 0.046. Treino médio 6.84 ms; previsão do lote 0.581 ms. Reconheceu 3 dos 3 empates do teste.

**Recomendação:** A2 (características), pelo F1 macro de validação (0.940) e pelos critérios de desempate declarados. No teste, A2 superou A1 em 21.86 pontos percentuais de F1 macro. Esse resultado descreve as configurações selecionadas; não prova que A2 seja melhor em qualquer amostra.

**Interpretação:** A1 selecionou 200 árvores sem limite de profundidade e pelo menos dois registros por folha; A2 selecionou 10 árvores sem limite e um registro por folha. O maior conjunto de árvores de A1 não produziu a melhor validação. A2 reduziu a diferença treino–validação e melhorou o teste, com menor custo de ajuste nesta execução. O ganho depende conjuntamente da representação e das configurações; não deve ser atribuído somente ao número de árvores. Uma floresta não supera necessariamente uma árvore isolada.

**Custo e limitações:** as configurações de A1 e A2 podem ter complexidades diferentes. Interpretamos os tempos junto com seus parâmetros e a dispersão das medições. Há somente dois empates na validação e três no teste; a reamostragem não cria diversidade. A2 possui cinco grupos de entradas iguais com rótulos diferentes no treino. Possíveis simetrias entre divisões também limitam a análise.
