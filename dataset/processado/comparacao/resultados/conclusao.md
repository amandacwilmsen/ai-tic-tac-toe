**Escolha para a aplicação: SVM com A2**, usando padronização do treino, kernel linear e C=1. A entrada tem 15 características; gamma não é um parâmetro ativo do kernel linear.

**Validação e generalização:** o SVM teve F1 macro 0.948533 e acurácia 93.48%. A MLP teve F1 0.949021, uma vantagem numérica de 0.049 pontos percentuais, sem comprovação de significância estatística. A diferença treino–validação foi 0.015 no SVM, 0.042 na MLP e 0.032 na árvore. O menor afastamento do SVM é favorável, mas não prova ausência de sobreajuste.

**Custo:** o ajuste do SVM levou em média 2.81 ms, contra 1064.89 ms da MLP nesta medição. A previsão do lote preparado levou 0.534 ms; incluir a extração e o DataFrame levou 1.376 ms. A escolha não exige que o SVM seja o mais rápido em cada etapa; ela equilibra custo e qualidade.

**Teste:** o SVM alcançou acurácia 94.62%, precisão macro 0.9625, recall macro 0.9583 e F1 macro 0.9575. Foram os maiores valores dessas quatro métricas entre as dez configurações avaliadas nesta amostra. Não usamos esses resultados para redefinir a grade ou reajustar parâmetros.

**A1 (tabuleiro):** diferenças treino–validação de k-NN: 0.177; Árvore de decisão: 0.427; Random Forest: 0.226; MLP: 0.191; SVM: 0.177. As diferenças de A1 foram maiores do que as de A2 nos cinco algoritmos.

**A2 (características):** diferenças treino–validação de k-NN: 0.061; Árvore de decisão: 0.032; Random Forest: 0.046; MLP: 0.042; SVM: 0.015. As diferenças de A1 foram maiores do que as de A2 nos cinco algoritmos.

**Representações:** A2 melhorou o F1 de validação e teste dos cinco algoritmos nesta amostra. Seus 15 atributos resumem contagens e alinhamentos úteis, mas sua extração custa mais do que a codificação das nove casas. O custo completo também depende do classificador e dos parâmetros; não declaramos A2 universalmente mais rápida.

**Limitações e continuidade:** somente dois empates na validação e três no teste; repetição de empates apenas no treino; possíveis simetrias entre divisões; cinco grupos de A2 com características iguais e respostas diferentes; busca finita; medições sensíveis à carga do computador. Os resultados não garantem desempenho em qualquer partida. A avaliação durante as partidas deve ser registrada separadamente no relatório.
