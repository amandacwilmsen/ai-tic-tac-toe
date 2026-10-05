# Jogo da velha — Trabalho 1 de Inteligência Artificial

**Autoras:** Amanda Wilmsen e Kamilah Santos.

O projeto investiga a classificação de estados de um tabuleiro 3×3 em **Tem jogo**,
**Jogador X venceu**, **Jogador O venceu** e **Empate**. O classificador observa o tabuleiro
após cada jogada. Na interface, o jogador humano utiliza X e a máquina utiliza O,
escolhendo suas jogadas aleatoriamente.

O repositório reúne a preparação dos dados, os experimentos e a interface de avaliação.
As etapas ainda necessárias para a entrega estão indicadas ao final deste documento.

## Executar o notebook

Utilize Python 3.11 ou superior. Na raiz do projeto, instale as dependências no ambiente
que será selecionado como kernel dos notebooks:

```sh
python -m pip install -r requirements.txt
```

Abra [tic_tac_toe.ipynb](tic_tac_toe.ipynb), selecione esse ambiente como kernel e execute as células
de cima para baixo. O notebook contém as explicações, o código e os resultados das seis etapas
de preparação. A última etapa atualiza os arquivos em `dataset/processado/`.

A versão do scikit-learn está fixada em `requirements.txt` para corresponder aos modelos
exportados de MLP e SVM e permitir seu carregamento no front end.

Os CSVs preparados já estão disponíveis. As versões usadas para gerá-los estão registradas em
[resumo_preparacao.json](dataset/processado/resumo_preparacao.json).

## Dataset e decisões

Fonte: Aha, D. (1991). *Tic-Tac-Toe Endgame*, UCI Machine Learning Repository,
[DOI 10.24432/C5688J](https://doi.org/10.24432/C5688J), licença CC BY 4.0.
Os arquivos originais em `dataset/` foram preservados.

O original tem 958 tabuleiros finais, sem valores ausentes nem tabuleiros duplicados.
Seus rótulos foram separados em 626 vitórias de X, 316 vitórias de O e 16 empates.
Para acrescentar a classe **Tem jogo**, foram enumerados estados legais com X começando,
alternância de jogadores e interrupção após vitória ou empate.

Selecionamos 200 exemplos de cada uma das três classes mais numerosas e os 16 empates
disponíveis: **616 tabuleiros distintos**. A seleção garante ao menos um exemplo de cada
número de jogadas disponível por classe e completa as vagas por sorteio com semente 42.

A divisão estratificada usa aproximadamente 70% para treino, 15% para validação e 15% para teste.
Somente depois da divisão, os empates do treino foram reamostrados para equilibrar as classes.

| Estado | Treino distinto | Treino após reamostragem | Validação | Teste |
| --- | ---: | ---: | ---: | ---: |
| Tem jogo | 140 | 140 | 30 | 30 |
| Jogador X venceu | 140 | 140 | 30 | 30 |
| Jogador O venceu | 140 | 140 | 30 | 30 |
| Empate | 11 | 140 | 2 | 3 |

Reamostrar repete tabuleiros do treino; não cria novos estados distintos. Os IDs repetidos nesse
conjunto são intencionais. Nenhum ID aparece em mais de uma divisão. Rotações e reflexões
equivalentes podem aparecer em divisões diferentes, pois não houve agrupamento por simetria.
A escassez de empates aumenta a incerteza de sua avaliação. Por esse motivo, os experimentos
apresentam métricas por classe e médias macro, nas quais as quatro classes têm o mesmo peso.

## Arquivos dos dados tratados

Use os CSVs de uma destas pastas em todos os algoritmos:

- [abordagem_1](dataset/processado/abordagem_1): `treino.csv`, `validacao.csv` e `teste.csv`,
  com nove casas numéricas (`b=0`, `x=1`, `o=-1`).
- [abordagem_2](dataset/processado/abordagem_2): os mesmos conjuntos, com 15 características calculadas.

Na abordagem 2, posições ocupadas são nove indicadores binários, um por casa.
“Linhas com 2 X/O” conta exatamente duas marcas nos oito alinhamentos (linhas, colunas e diagonais),
mesmo quando a terceira casa pertence ao adversário. O jogador da vez é calculado pelas contagens:
X=1 quando as contagens são iguais; O=-1 quando X tem uma marca a mais. Em tabuleiros finais,
isso representa o próximo turno hipotético, sem consultar o rótulo.

Exemplo de leitura das entradas e da resposta:

```python
import pandas as pd

treino = pd.read_csv("dataset/processado/abordagem_1/treino.csv")
X_treino = treino.drop(columns=["id_tabuleiro", "estado"])
y_treino = treino["estado"]
```

`id_tabuleiro` é apenas um identificador para auditoria. `estado` é a saída desejada.
As duas abordagens mantêm os mesmos IDs, rótulos e ordem dentro de cada conjunto.
Escolha parâmetros pela validação e avalie a configuração final no teste. Se precisar ajustar
escalas, ajuste o transformador somente no treino. Preserve as divisões entre algoritmos.

A base selecionada e as divisões anteriores à reamostragem estão em `dataset/processado/`.
Mais detalhes estão no [README dos dados](dataset/processado/README.md) e no notebook.

## Experimentos de classificação

Os notebooks usam os mesmos CSVs de treino, validação e teste:

- [k-NN](dataset/processado/knn/knn.ipynb).
- [Árvore de decisão](dataset/processado/arvoreDecisao/arvore_decisao.ipynb).
- [MLP](dataset/processado/mlp/mlp.ipynb): rede neural com padronização ajustada no treino,
  seleção dos parâmetros pela validação, métricas por classe, gráficos e medição de custo.
- [SVM](dataset/processado/svm/svm.ipynb): comparação dos kernels linear e RBF, com
  padronização ajustada no treino e seleção de C e gamma pela validação.

Execute as células de cada notebook na ordem. Na MLP e no SVM, a última etapa salva tabelas,
gráficos, documentação e o modelo com seu padronizador nas respectivas pastas `resultados/`.
Os parâmetros são escolhidos antes da avaliação no teste. A comparação final dos cinco
classificadores ainda faz parte das etapas seguintes do trabalho.

Os tempos registrados medem o ajuste e a previsão do modelo sobre as representações já
preparadas. Eles não incluem leitura dos CSVs, extração das características do tabuleiro
ou comunicação da interface. A comparação deve considerar as condições de execução,
além das métricas de classificação e das diferenças entre treino e validação.

## Front end

Na raiz do projeto, execute `python front_end/servidor.py` no ambiente das dependências
e abra **http://127.0.0.1:8765**. O ambiente precisa corresponder ao utilizado para exportar
os modelos, conforme registrado nos resumos dos experimentos.

Você joga X e a máquina joga O aleatoriamente. A interface mostra a previsão de MLP ou SVM
a cada jogada e contabiliza acertos, erros e acurácia. Uma conferência pelas regras permite
continuar diante de um fim anunciado incorretamente e encerrar diante de um fim não detectado,
como pede o enunciado. Os registros podem ser exportados para o relatório.

Consulte o [README do front end](front_end/README.md) para entender o código, os registros
e como avaliar a solução durante partidas reais. O modelo definitivo poderá ser escolhido
depois da comparação dos cinco classificadores. O seletor atual auxilia a avaliação de
MLP e SVM; a possibilidade de escolher modelos na interface é um recurso adicional.

## Atendimento ao enunciado e etapas de entrega

| Requisito | Situação documentada neste repositório |
| --- | --- |
| Análise e adequação do dataset UCI | Concluídas no notebook de preparação, com justificativas e contagens por classe. |
| Amostragem e balanceamento | 616 tabuleiros distintos; reamostragem somente no treino. A escassez de empates está documentada. |
| Duas abordagens de pré-processamento | Implementadas e avaliadas nos quatro classificadores disponíveis. |
| Mesmas divisões físicas de treino, validação e teste | CSVs compartilhados pelos experimentos; seleção de parâmetros pela validação. |
| Pelo menos cinco classificadores | k-NN, árvore de decisão, MLP e SVM disponíveis; falta o quinto algoritmo. |
| Parâmetros, métricas e análise dos algoritmos | Documentados nos notebooks, incluindo topologias da MLP e explicação do SVM. O quinto algoritmo deve seguir o mesmo procedimento. |
| Comparação geral e escolha do classificador | Falta consolidar tabelas e gráficos dos cinco algoritmos, comparar desempenho e custo e justificar a escolha. |
| Interface, mensagens e contagem de acertos/erros | Implementadas; a configuração definitiva depende da comparação dos algoritmos. |
| Resultados da interação com usuários | A interface exporta registros reais; os resultados devem integrar o relatório e corresponder ao modelo definitivo. |
| Relatório em PPT | Deve reunir introdução, dados, pré-processamento, algoritmos, justificativas, resultados, comparação e conclusão. |
| Vídeo de até 10 minutos | Deve apresentar o processo e o relatório, com todas as integrantes aparecendo e explicando suas partes. |
| Declaração de uso de ferramentas de IA | Registrada abaixo e nos materiais revisados; deve acompanhar a apresentação da entrega. |

O relatório deve explicar o funcionamento dos dois algoritmos de livre escolha e registrar
as dificuldades e os aprendizados. Cada integrante deve desenvolver pelo menos um
classificador e compreender seu código, parâmetros e resultados. A inscrição do grupo,
o prazo e a apresentação devem seguir as orientações do Moodle. O vídeo deve ser gravado
pelas integrantes, sem substituição de suas falas ou imagens por IA; sua entrega é obrigatória.

## Uso de ferramentas de IA

O Codex, da OpenAI, foi utilizado para explicar conceitos, auxiliar na análise e transformação
dos dados, gerar e organizar código e documentação dos notebooks de preparação, MLP e SVM,
executar os experimentos de MLP e SVM, criar e documentar o front end, revisar os textos e
comentários dos notebooks de k-NN e árvore de decisão, ajustar seus caminhos de leitura
e verificar os resultados.
Esse registro identifica as atividades em que houve assistência de IA, conforme solicitado
no enunciado.
