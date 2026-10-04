# Dados preparados para os experimentos

Gerados pelo notebook tic_tac_toe.ipynb. Execute-o de cima para baixo para reproduzir. Os arquivos originais foram preservados.

Fonte: Aha, D. (1991), Tic-Tac-Toe Endgame, UCI, https://doi.org/10.24432/C5688J (CC BY 4.0).
Problemas encontrados: duas classes originais, ausência de estados intermediários e somente 16 empates distintos.
As verificações iniciais não encontraram valores ausentes ou tabuleiros duplicados. O símbolo b foi preservado como casa vazia.
Tratamento: verificação dos símbolos; rotulagem; geração legal de estados intermediários; amostragem; divisão; reamostragem do treino; duas representações numéricas.
A geração começa com X, alterna os jogadores e encerra cada caminho após vitória ou empate.
A seleção inclui ao menos um tabuleiro de cada número de jogadas disponível por classe, com as demais vagas sorteadas.
Semente: 42. Divisão estratificada: aproximadamente 70% treino, 15% validação, 15% teste.

## Arquivos

- base_selecionada.csv: tabuleiros distintos escolhidos, com origem e número de jogadas.
- divisoes/treino.csv, validacao.csv e teste.csv: separação anterior ao balanceamento.
- divisoes/treino_balanceado.csv: treino com repetições intencionais de classes menores.
- abordagem_1/ e abordagem_2/: treino.csv, validacao.csv e teste.csv para os classificadores.
- resumo_preparacao.json: contagens, convenções, versões e limitações.

## Contagens

| Estado | Selecionados distintos | Treino distintos | Treino com repetições | Validação | Teste |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tem jogo | 200 | 140 | 140 | 30 | 30 |
| Jogador X venceu | 200 | 140 | 140 | 30 | 30 |
| Jogador O venceu | 200 | 140 | 140 | 30 | 30 |
| Empate | 16 | 11 | 140 | 2 | 3 |

## Estrutura e uso dos dados

Use os CSVs dentro de abordagem_1/ ou abordagem_2/ para todos os algoritmos.
Entradas: todas as colunas exceto id_tabuleiro e estado. Saída: estado.
O identificador é a concatenação das nove casas: serve para auditoria e não é uma característica de entrada.
Os IDs e rótulos seguem a mesma ordem nas duas abordagens, inclusive no treino reamostrado.
Casas na abordagem 1: b=0, x=1, o=-1 (9 características).
A abordagem 2 usa 15 características. Ocupação tem nove indicadores; linhas com duas marcas incluem linhas, colunas e diagonais, independentemente da terceira casa.
Turno: X=1 quando nX=nO; O=-1 quando nX=nO+1, inclusive como turno hipotético em estados finais.
Se precisar ajustar escalas, ajuste o transformador somente no treino e aplique-o aos outros conjuntos.
Escolha parâmetros com validação e avalie a configuração final no teste. Preserve as divisões entre algoritmos.
Os CSVs das abordagens foram relidos e comparados às tabelas em memória, incluindo IDs, rótulos e ordem.

## Limitações

- Somente 16 empates distintos; a reamostragem do treino nao cria novos estados.
- Validacao e teste possuem poucos empates; apresentar metricas por classe e medias macro.
- Rotacoes e reflexoes equivalentes podem aparecer em conjuntos diferentes.
- As caracteristicas da abordagem 2 perdem parte da informacao do tabuleiro.
