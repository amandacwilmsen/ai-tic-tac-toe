# Comparação dos classificadores

O [notebook de comparação](comparacao_classificadores.ipynb) reúne os cinco
classificadores nas duas representações de entrada. Execute-o depois dos
experimentos individuais, usando as dependências da raiz do projeto.

Ele confere os CSVs e as previsões exportadas, reúne as configurações já
selecionadas pela validação e mede o custo sob condições comuns. Não altera
as divisões, não realiza outra busca de parâmetros e não sobrescreve os modelos.

## Resultados para avaliação e relatório

| Arquivo em `resultados/` | Conteúdo |
| --- | --- |
| [comparacao_completa.csv](resultados/comparacao_completa.csv) | Dez configurações: métricas de treino, validação e teste, diferença treino–validação e tempos |
| [configuracoes.csv](resultados/configuracoes.csv) | Parâmetros selecionados e topologias da MLP |
| [custo_representacoes.csv](resultados/custo_representacoes.csv) | Custo de obter A1 e A2 a partir dos tabuleiros |
| [metricas_teste.png](resultados/metricas_teste.png) | Acurácia, precisão, recall e F1 das duas abordagens |
| [treino_validacao.png](resultados/treino_validacao.png) | F1 de treino e validação da mesma configuração |
| [custo_controlado.png](resultados/custo_controlado.png) | Ajuste, previsão e extração das características com previsão |
| [custo_representacoes.png](resultados/custo_representacoes.png) | Comparação do custo de preparar as entradas |
| [conclusao.md](resultados/conclusao.md) | Justificativa da escolha do SVM e limitações |
| [resumo_comparacao.json](resultados/resumo_comparacao.json) | Versões, condições das medições e hashes das fontes |

Precisão, recall e F1 utilizam média macro. Os tempos apresentam média e desvio
padrão de 20 repetições, com uma thread. A previsão usa um lote de 93 tabuleiros;
esse tempo não equivale à latência de uma jogada no navegador.

Os tempos dos experimentos individuais também são preservados nas colunas
`tempo_*_notebook_ms`. Para comparar algoritmos, use as medições comuns deste
notebook, distinguindo o custo do modelo do custo de preparar suas entradas.

O modelo recomendado é **SVM, A2, kernel linear, C=1**. A MLP teve F1 de validação
ligeiramente maior, mas o SVM apresenta menor diferença treino–validação e menor
custo de ajuste. O teste descreve os modelos já avaliados; não representa uma
nova avaliação independente após a escolha final.
