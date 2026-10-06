# Front end — jogo da velha e avaliação da IA

A interface abre no navegador e usa os modelos já exportados pelos notebooks.
Você joga **X**, começa a partida e escolhe uma casa livre. A máquina joga **O**
escolhendo uma casa livre aleatoriamente, sem consultar os classificadores.

## Executar

Na raiz do projeto, use o mesmo ambiente Python utilizado para exportar os modelos:

```sh
python front_end/servidor.py
```

Abra **http://127.0.0.1:8765** no navegador. Para encerrar o servidor, use `Ctrl+C`.
O servidor usa a biblioteca padrão do Python e as dependências já registradas em
`requirements.txt`; não precisa instalar um framework de interface. Para escolher
outra porta: `python front_end/servidor.py --porta 8766`.

Os modelos foram salvos com scikit-learn 1.9.0, versão fixada em `requirements.txt`.
O carregamento confere a versão e as colunas esperadas. Para reproduzir o experimento,
consulte também as versões registradas nos respectivos resumos JSON. Caso utilize outro
ambiente para treinar, exporte novamente os modelos e mantenha a mesma versão no front end.

## Modelo utilizado

A MLP é o padrão. O seletor permite escolher **MLP, SVM, k-NN, árvore de decisão ou
Random Forest** antes da primeira jogada ou após o fim da partida. Para mudar durante
uma partida, clique em **Nova partida** e escolha o modelo antes de jogar.
Cada modelo utiliza a abordagem escolhida pela validação de seu notebook e o modelo
salvo, incluindo o padronizador ajustado somente no treino quando ele é utilizado.
O front end não treina nem ajusta parâmetros.

Os cinco modelos e seus resumos estão nas pastas `resultados/` dos respectivos
experimentos. Os notebooks de k-NN, árvore de decisão e Random Forest incluem uma
etapa final de exportação. Ela preserva as configurações selecionadas e registra as
colunas de entrada, a versão do scikit-learn e as previsões de teste para auditoria.
As métricas da interação ficam separadas por modelo, inclusive ao voltar a um modelo
que já foi utilizado na mesma sessão.

Para avaliar o modelo recomendado na
[comparação dos classificadores](../dataset/processado/comparacao/comparacao_classificadores.ipynb),
selecione **SVM** antes da primeira jogada. Ele utiliza A2, kernel linear e C=1.
Para acrescentar outro modelo, exporte seu modelo e metadados e registre-o em
`modelos.py`, preservando as mesmas representações de entrada.

## Funcionamento e conferência das previsões

Após **cada jogada válida de X ou O**, o modelo recebe apenas as características do
tabuleiro. As funções de entrada repetem as convenções do notebook: nove casas
numéricas na abordagem 1 ou 15 características na abordagem 2, incluindo exatamente
duas marcas por alinhamento e o próximo turno hipotético calculado pelas contagens.

Em seguida, conferimos a previsão com um gabarito obtido pelas regras do jogo:

| Situação | Ação |
| --- | --- |
| A IA e as regras indicam que há jogo | Continuar |
| A IA anuncia um fim, mas ainda há jogo | Registrar o erro e continuar |
| A IA indica que há jogo, mas a partida terminou | Registrar o erro e encerrar |
| A partida terminou e a IA reconhece o resultado correto | Registrar o acerto e encerrar |
| A partida terminou, mas a IA confunde o vencedor/empate | Registrar o erro de classe e encerrar |

As regras permitem medir erros e controlar a continuidade da partida. A tela
mostra separadamente a **previsão do modelo** e o **estado real**, preservando as falhas
da IA. O modelo não recebe o gabarito como entrada. Nunca são feitas jogadas após um
fim real, evitando estados ilegais.

## Contabilização e registros para o relatório

Uma avaliação corresponde a uma previsão **após uma jogada**, e não a uma partida inteira.
O tabuleiro vazio recebe uma previsão inicial para exibição, mas ela não entra na contagem.
Tentativas em casas ocupadas, pedidos inválidos e atualizações da página não contam.

`acurácia = acertos / avaliações`. Antes da primeira avaliação, a interface exibe `—`.
O acerto exige que a classe prevista corresponda exatamente à classe real, incluindo
o vencedor correto. A interface também apresenta vitórias de X/O e empates pelas regras.

Uma nova partida mantém as contagens da sessão. Trocar de modelo mantém contagens separadas.
Os registros incluem todas as partidas daquela sessão, inclusive as interrompidas.
Um navegador identifica sua sessão por cookie. Encerrar/reiniciar o servidor inicia
novas sessões; os arquivos anteriores continuam salvos para análise.

Após cada jogada, são gravados em `front_end/resultados/`:

- `interacoes_<data>_<sessao>.csv`: partida, modelo, abordagem, horário, jogador, casa,
  tabuleiro, previsão, gabarito, acerto/erro e tipo de erro.
- `interacoes_<data>_<sessao>.json`: identificação dos modelos (incluindo hash),
  contagens e acurácia geral e por modelo, resultados das partidas e unidade de avaliação.

Os botões **Baixar jogadas** e **Baixar resumo** exportam a sessão atual. Os registros
locais são ignorados pelo Git; inclua os arquivos que desejar entregar explicitamente.
Para o PPT, faça partidas reais e registre total de jogadas, acertos, erros e acurácia,
além dos exemplos de falhas observados. Resultados dos testes automatizados não são
resultados de interação com usuários.

## Entender o código e verificar

| Arquivo | Responsabilidade |
| --- | --- |
| `jogo.py` | Regras, características, partidas, contagens e gravação |
| `modelos.py` | Leitura dos cinco modelos exportados e classificação, sem novo treino |
| `servidor.py` | Serve a página e recebe as ações do navegador |
| `index.html` / `estilo.css` | Estrutura e aparência da interface |
| `app.js` | Cliques, apresentação do estado e turno automático da máquina |
| `test_front_end.py` | Verifica os casos de erro exigidos e a contabilização |
| `test_http.py` | Verifica página, API, sessões e exportação com os modelos reais |
| `test_modelos.py` | Compara características e previsões do front com os experimentos exportados |

Execute os testes de comportamento na raiz:

```sh
python -m unittest front_end.test_front_end -v
python -m unittest front_end.test_modelos -v
python -m unittest front_end.test_http -v
```

Os testes de `test_front_end.py` usam classificadores controlados para reproduzir
situações de erro e verificar o controle da partida. O teste de `test_http.py` utiliza os modelos
reais exportados para verificar a integração entre página, servidor, sessões e registros.
O teste de `test_modelos.py` verifica os 93 tabuleiros de teste para cada um dos cinco
modelos, comparando as entradas com os CSVs preparados e as previsões com os registros
dos experimentos.
Os testes de partidas escrevem somente em pastas temporárias, preservando os resultados
das interações reais. O teste de modelos apenas lê os arquivos dos experimentos.
Essas verificações avaliam o funcionamento do sistema; suas contagens não devem ser
apresentadas como desempenho obtido durante interações com usuários.
