**A1 (tabuleiro):** topologia **9 → 64 → 32 → 4**, ativação `relu`, alpha=1 e 2852 parâmetros. F1 macro: treino 1.000, validação 0.809 e teste 0.717; acurácia no teste 84.9%. Diferença treino–validação: 0.191. Treino médio: 1143.28 ms; previsão do lote: 1.007 ms.

**A2 (características):** topologia **15 → 64 → 32 → 4**, ativação `relu`, alpha=1 e 3236 parâmetros. F1 macro: treino 0.991, validação 0.949 e teste 0.933; acurácia no teste 91.4%. Diferença treino–validação: 0.042. Treino médio: 1098.61 ms; previsão do lote: 0.441 ms.

**Recomendação para a MLP:** A2 (características), escolhida antes do teste pelo F1 macro de validação (0.949) e pelos critérios de desempate. Nesta medição, A2 (características) teve menor tempo médio de treino e A2 (características) teve menor tempo médio de previsão. Diferenças pequenas de tempo podem oscilar entre execuções.

**Interpretação da generalização:** A1 (tabuleiro) teve a maior diferença entre F1 de treino (1.000) e validação (0.809). Essa queda é um indício de possível overfitting e deve ser discutida mesmo com regularização. Uma diferença menor na outra abordagem é favorável, mas não demonstra ausência de overfitting. A1 (tabuleiro) reconheceu 1 dos 3 empates do teste. A2 (características) reconheceu 3 dos 3 empates do teste.

**Limitações:** somente dois empates na validação e três no teste; reamostragem não cria novos empates; possíveis simetrias entre divisões; entradas iguais com rótulos diferentes na abordagem 2; busca finita e apenas uma semente. Estes resultados não demonstram ausência de overfitting nem garantem generalização para qualquer partida. A avaliação durante partidas com usuários deve ser registrada separadamente no front end
e apresentada no relatório, pois mede uma situação de uso diferente do teste reservado.
