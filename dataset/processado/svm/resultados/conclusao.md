**A1 (tabuleiro):** kernel **rbf**, C=100, gamma=0.01 (efetivo: 0.01), 317 vetores de suporte e 9 entradas. F1 macro: treino 0.924, validação 0.747 e teste 0.837; acurácia no teste 83.9%. Diferença treino–validação: 0.177. Treino médio: 22.30 ms; previsão do lote: 1.379 ms.

**A2 (características):** kernel **linear**, C=1, 144 vetores de suporte e 15 entradas. F1 macro: treino 0.964, validação 0.949 e teste 0.958; acurácia no teste 94.6%. Diferença treino–validação: 0.015. Treino médio: 3.85 ms; previsão do lote: 0.512 ms.

**Recomendação para o SVM:** A2 (características), escolhida antes do teste pelo F1 macro de validação (0.949) e pelos critérios de desempate. Nesta medição, A2 (características) teve menor tempo médio de treino e A2 (características) teve menor tempo médio de previsão. Os tempos podem oscilar entre execuções.

**Generalização:** a maior diferença entre treino e validação foi 0.177, em A1 (tabuleiro). A diferença deve ser interpretada junto com os resultados por classe; ela não demonstra, sozinha, presença ou ausência de overfitting. A1 (tabuleiro) reconheceu 3 dos 3 empates do teste. A2 (características) reconheceu 3 dos 3 empates do teste.

**Limitações:** somente dois empates na validação e três no teste; reamostragem não cria novos empates; possíveis simetrias entre divisões; entradas iguais com rótulos diferentes na abordagem 2; busca finita. São resultados desta amostra, sem garantia de desempenho em qualquer partida. A avaliação durante partidas com usuários deve ser registrada separadamente no front end
e apresentada no relatório, pois mede uma situação de uso diferente do teste reservado.
