# Jogo da velha — Trabalho 1 de Inteligência Artificial

**Autoras:** Amanda Wilmsen e Kamilah Santos.

Classificamos o estado de um tabuleiro 3×3 em **Tem jogo**, **Jogador X venceu**,
**Jogador O venceu** ou **Empate**. O classificador observa o tabuleiro após cada
jogada. Na interface, a pessoa joga com X e a máquina joga com O aleatoriamente.

## Instalação e execução

Use Python 3.11 ou superior e instale as dependências na raiz do projeto:

```sh
python -m pip install -r requirements.txt
```

Selecione esse ambiente como kernel dos notebooks. O scikit-learn está fixado em
1.9.0 para corresponder aos modelos exportados e permitir seu carregamento no front.

Os dados, modelos e resultados já estão salvos. Para reproduzir o processo,
execute as células de cada notebook de cima para baixo, nesta sequência:

1. [Preparação dos dados](tic_tac_toe.ipynb).
2. Experimentos individuais dos cinco classificadores, em qualquer ordem.
3. [Comparação dos classificadores](dataset/processado/comparacao/comparacao_classificadores.ipynb).
4. Avaliação durante partidas no front end.

## Dados preparados

Fonte: Aha, D. (1991). *Tic-Tac-Toe Endgame*, UCI Machine Learning Repository,
[DOI 10.24432/C5688J](https://doi.org/10.24432/C5688J), licença CC BY 4.0.
Os arquivos originais em `dataset/` foram preservados.

O original contém 958 tabuleiros finais: 626 vitórias de X, 316 vitórias de O e
16 empates. Acrescentamos estados intermediários legais e selecionamos **616
tabuleiros distintos**, com semente 42. A divisão é estratificada, com aproximadamente
70% para treino, 15% para validação e 15% para teste. O balanceamento repete apenas
os empates do treino, depois da divisão.

| Classe | Treino distinto | Treino balanceado | Validação | Teste |
| --- | ---: | ---: | ---: | ---: |
| Tem jogo | 140 | 140 | 30 | 30 |
| Jogador X venceu | 140 | 140 | 30 | 30 |
| Jogador O venceu | 140 | 140 | 30 | 30 |
| Empate | 11 | 140 | 2 | 3 |

As pastas [abordagem_1](dataset/processado/abordagem_1) e
[abordagem_2](dataset/processado/abordagem_2) contêm `treino.csv`, `validacao.csv`
e `teste.csv`, com os mesmos IDs, rótulos e ordem. A1 utiliza nove casas numéricas
(`b=0`, `x=1`, `o=-1`); A2 utiliza 15 características derivadas.

`id_tabuleiro` serve apenas para auditoria, e `estado` é a resposta: ambas as
colunas são excluídas das entradas. A padronização, quando utilizada, é ajustada
somente no treino. Os parâmetros são escolhidos pela validação.

As contagens, definições das características e limitações estão no
[README dos dados](dataset/processado/README.md). A reamostragem não cria novos
empates; possíveis simetrias entre divisões e poucos empates na avaliação limitam
a interpretação dos resultados.

## Experimentos e comparação

| Classificador | Notebook |
| --- | --- |
| k-NN | [knn.ipynb](dataset/processado/knn/knn.ipynb) |
| Árvore de decisão | [arvore_decisao.ipynb](dataset/processado/arvoreDecisao/arvore_decisao.ipynb) |
| Random Forest | [random_forest.ipynb](dataset/processado/randomForest/random_forest.ipynb) |
| MLP | [mlp.ipynb](dataset/processado/mlp/mlp.ipynb) |
| SVM | [svm.ipynb](dataset/processado/svm/svm.ipynb) |

Cada experimento documenta parâmetros, métricas, treino e validação nas duas
abordagens. Sua pasta `resultados/` reúne tabelas, previsões, relatórios por classe,
gráficos, conclusão e o modelo da abordagem selecionada.

A [comparação geral](dataset/processado/comparacao/README.md) reúne as dez
configurações, acurácia, precisão, recall, F1 macro e tempos medidos sob o mesmo
protocolo. Os CSVs e PNGs em `comparacao/resultados/` podem ser utilizados no relatório.

Recomendamos **SVM com A2, kernel linear e C=1**: combina validação próxima à da
MLP, menor diferença entre treino e validação e baixo custo de ajuste. No teste,
obteve **94,62% de acurácia e 0,9575 de F1 macro**. A justificativa e os limites
da comparação estão na [conclusão](dataset/processado/comparacao/resultados/conclusao.md).

## Front end

Na raiz do projeto, execute:

```sh
python front_end/servidor.py
```

Abra **http://127.0.0.1:8765**. A interface inicia com MLP; selecione **SVM antes
da primeira jogada** para avaliar o modelo recomendado. As cinco opções continuam
disponíveis. O placar registra acertos, erros e acurácia por jogada e por modelo.
Os botões de exportação salvam os registros para análise no relatório.

O [README do front](front_end/README.md) explica a conferência das previsões,
os registros e os comandos de verificação. Os registros locais de partidas são
ignorados pelo Git; inclua explicitamente os arquivos escolhidos para a entrega.

Ferramentas de apoio: Claude, Gemini e Codex.
