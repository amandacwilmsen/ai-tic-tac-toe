# ai-tic-tac-toe

Preparação dos dados do trabalho de Inteligência Artificial de Amanda Wilmsen e Kamilah Santos.
O objetivo dos classificadores será reconhecer quatro estados: **Tem jogo**, **Jogador X venceu**,
**Jogador O venceu** e **Empate**.

## Executar o notebook

Na pasta do projeto, instale as dependências no ambiente Python que será usado pelo notebook:

```sh
python -m pip install -r requirements.txt
```

Abra [tic_tac_toe.ipynb](tic_tac_toe.ipynb), selecione esse ambiente como kernel e execute as células
de cima para baixo. O notebook contém as explicações, o código e os resultados das seis etapas
de preparação. A última etapa atualiza os arquivos em `dataset/processado/`.

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
A escassez de empates limita a precisão de sua avaliação; apresentar métricas por classe e médias macro.

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
O treinamento dos classificadores e a comparação das abordagens serão as próximas etapas do trabalho.
