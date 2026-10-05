"""Regras do jogo, extração de características e registro das avaliações.

A máquina escolhe uma casa aleatória. O modelo apenas classifica o tabuleiro.
As regras fornecem um gabarito independente para conferir cada previsão da IA.
"""

import csv
import io
import json
import random
import threading
from datetime import datetime
from pathlib import Path
from uuid import uuid4

TEM_JOGO = "Tem jogo"
CLASSES = [TEM_JOGO, "Jogador X venceu", "Jogador O venceu", "Empate"]
COLUNAS = [
    "superior_esquerda", "superior_centro", "superior_direita",
    "meio_esquerda", "meio_centro", "meio_direita",
    "inferior_esquerda", "inferior_centro", "inferior_direita",
]
ALINHAMENTOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6),
]


def conferir_tabuleiro(tabuleiro):
    """Verifica o tamanho e os símbolos; a sessão garante jogadas legais e alternadas."""
    if len(tabuleiro) != 9 or not set(tabuleiro).issubset({"x", "o", "b"}):
        raise ValueError("O tabuleiro precisa de nove casas com x, o ou b.")


def estado_real(tabuleiro):
    """Calcula o gabarito pelas regras, sem chamar o classificador."""
    conferir_tabuleiro(tabuleiro)
    for jogador, classe in [("x", CLASSES[1]), ("o", CLASSES[2])]:
        if any(all(tabuleiro[p] == jogador for p in linha) for linha in ALINHAMENTOS):
            return classe
    return TEM_JOGO if "b" in tabuleiro else "Empate"


def extrair_entradas(tabuleiro, abordagem):
    """Usa exatamente as convenções dos dois pré-processamentos do notebook."""
    conferir_tabuleiro(tabuleiro)
    if abordagem == "abordagem_1":
        codificacao = {"b": 0, "x": 1, "o": -1}
        return {coluna: codificacao[casa] for coluna, casa in zip(COLUNAS, tabuleiro)}
    if abordagem != "abordagem_2":
        raise ValueError("Abordagem de entrada desconhecida.")
    n_x, n_o = tabuleiro.count("x"), tabuleiro.count("o")
    entradas = {"quantidade_x": n_x, "quantidade_o": n_o}
    entradas.update({f"ocupada_{coluna}": int(casa != "b")
                     for coluna, casa in zip(COLUNAS, tabuleiro)})
    for jogador in ["x", "o"]:
        entradas[f"linhas_com_2_{jogador}"] = sum(
            sum(tabuleiro[p] == jogador for p in linha) == 2 for linha in ALINHAMENTOS
        )
    entradas["casas_vazias"] = tabuleiro.count("b")
    entradas["jogador_da_vez"] = 1 if n_x == n_o else -1
    return entradas


def interpretar_previsao(real, previsto):
    """Compara a classe prevista ao gabarito e descreve os erros de fim de jogo."""
    if real == previsto:
        return "acerto", (
            "A IA acertou. A partida continua." if real == TEM_JOGO
            else f"A IA acertou: {real}. Partida encerrada."
        )
    if real == TEM_JOGO:
        return "fim_incorreto", "A IA anunciou um fim incorreto. Ainda há jogo; vamos continuar."
    if previsto == TEM_JOGO:
        return "fim_nao_detectado", f"A IA não detectou o fim. {real}; a partida será encerrada."
    return "classe_incorreta", f"A IA confundiu o resultado. {real}; a partida será encerrada."


def calcular_score(eventos, partidas):
    """Calcula acurácia por jogada e resultados das partidas pelas regras."""
    total = len(eventos)
    acertos = sum(e["acertou"] for e in eventos)
    concluidas = [p for p in partidas if p["situacao"] == "concluida"]
    return {
        "avaliacoes": total, "acertos": acertos, "erros": total - acertos,
        "acuracia": acertos / total if total else None,
        "partidas_concluidas": len(concluidas),
        "vitorias_x": sum(p["resultado"] == CLASSES[1] for p in concluidas),
        "vitorias_o": sum(p["resultado"] == CLASSES[2] for p in concluidas),
        "empates": sum(p["resultado"] == "Empate" for p in concluidas),
    }


class Sessao:
    """Mantém partidas e contagens de um navegador, separadas por modelo."""

    def __init__(self, prever, modelos, pasta_registros, modelo="mlp", rng=None):
        self.id = uuid4().hex
        self.lock = threading.RLock()
        self.prever = prever
        self.modelos = modelos
        self.pasta = Path(pasta_registros)
        self.rng = rng if rng is not None else random.Random()
        self.eventos = []
        self.partidas = []
        self.inicio = datetime.now().astimezone().isoformat()
        self.nome_registro = f"interacoes_{datetime.now():%Y%m%d_%H%M%S}_{self.id[:8]}"
        self.nova_partida(modelo)

    def nova_partida(self, modelo=None):
        modelo = modelo or getattr(self, "modelo", "mlp")
        if modelo not in self.modelos:
            raise ValueError("Escolha um dos modelos disponíveis.")
        # O tabuleiro inicial é classificado para exibição, sem contar como jogada avaliada.
        inicial = self.prever(modelo, ["b"] * 9)
        if inicial not in CLASSES:
            raise ValueError("O classificador retornou uma classe desconhecida.")
        if self.partidas and self.partidas[-1]["situacao"] == "em_andamento":
            self.partidas[-1]["situacao"] = "interrompida"
        self.modelo = modelo
        self.tabuleiro = ["b"] * 9
        self.turno = "x"
        self.terminou = False
        self.previsto = inicial
        self.historico = []
        self.tipo_aviso, self.aviso = interpretar_previsao(TEM_JOGO, inicial)
        if self.tipo_aviso == "acerto":
            self.aviso = "Você começa com X. Escolha uma casa livre."
        self.partida = uuid4().hex
        self.partidas.append({"id": self.partida, "modelo": modelo,
                              "situacao": "em_andamento", "resultado": None})
        if self.eventos:
            self._salvar_resumo()

    def trocar_modelo(self, modelo):
        if modelo not in self.modelos:
            raise ValueError("Escolha um dos modelos disponíveis.")
        if self.historico and not self.terminou:
            raise ValueError("Termine a partida ou comece uma nova antes de trocar o modelo.")
        self.nova_partida(modelo)

    def jogar(self, posicao, jogador="x"):
        """Aplica uma jogada válida, classifica o novo estado e registra sua avaliação."""
        if self.terminou:
            raise ValueError("Esta partida terminou. Comece uma nova partida.")
        if jogador != self.turno:
            raise ValueError("Espere a sua vez de jogar.")
        if type(posicao) is not int or not 0 <= posicao < 9:
            raise ValueError("Escolha uma casa entre 1 e 9.")
        if self.tabuleiro[posicao] != "b":
            raise ValueError("Essa casa já está ocupada. Escolha outra.")

        novo = self.tabuleiro.copy()
        novo[posicao] = jogador
        previsto = self.prever(self.modelo, novo)
        if previsto not in CLASSES:
            raise ValueError("O classificador retornou uma classe desconhecida.")
        real = estado_real(novo)
        tipo, aviso = interpretar_previsao(real, previsto)
        evento = {
            "sessao": self.id, "partida": self.partida,
            "data_hora": datetime.now().astimezone().isoformat(),
            "modelo": self.modelo, "abordagem": self.modelos[self.modelo]["abordagem"],
            "jogada": len(self.historico) + 1, "jogador": jogador.upper(),
            "casa": posicao + 1, "id_tabuleiro": "".join(novo),
            "estado_previsto": previsto, "estado_real": real,
            "acertou": real == previsto, "tipo": tipo, "fim_real": real != TEM_JOGO,
        }
        self.tabuleiro = novo
        self.previsto = previsto
        self.tipo_aviso, self.aviso = tipo, aviso
        # O gabarito aplica as exceções do enunciado: fim real encerra; fim falso continua.
        # A previsão original permanece na tela e no registro, inclusive quando incorreta.
        self.terminou = real != TEM_JOGO
        self.turno = None if self.terminou else ("o" if jogador == "x" else "x")
        self.eventos.append(evento)
        self.historico.append(evento)
        if self.terminou:
            self.partidas[-1].update(situacao="concluida", resultado=real)
        self._salvar_evento(evento)

    def jogar_maquina(self):
        """Sorteia uma casa livre para O, sem usar o classificador na escolha."""
        if self.terminou or self.turno != "o":
            raise ValueError("Não é a vez da máquina.")
        livres = [i for i, casa in enumerate(self.tabuleiro) if casa == "b"]
        self.jogar(self.rng.choice(livres), "o")

    def resumo(self):
        return {
            "sessao": self.id, "inicio": self.inicio,
            "atualizado_em": datetime.now().astimezone().isoformat(),
            "origem": "interacao_humano_maquina_aleatoria",
            "unidade_avaliacao": "uma previsão após cada jogada válida",
            "modelos": self.modelos,
            "score_geral": calcular_score(self.eventos, self.partidas),
            "score_por_modelo": {
                chave: calcular_score([e for e in self.eventos if e["modelo"] == chave],
                                      [p for p in self.partidas if p["modelo"] == chave])
                for chave in self.modelos
            },
            "partidas": self.partidas,
        }

    def estado(self):
        real = estado_real(self.tabuleiro)
        linha_vitoria = next((list(linha) for linha in ALINHAMENTOS
                              if self.tabuleiro[linha[0]] != "b"
                              and len({self.tabuleiro[p] for p in linha}) == 1), [])
        return {
            "modelo": self.modelo, "modelos": [{"id": k, "nome": v["nome"]}
                                                 for k, v in self.modelos.items()],
            "tabuleiro": self.tabuleiro.copy(), "turno": self.turno, "terminou": self.terminou,
            "estado_previsto": self.previsto, "estado_real": real,
            "tipo_aviso": self.tipo_aviso, "aviso": self.aviso,
            "historico": self.historico.copy(), "linha_vitoria": linha_vitoria,
            "score": self.resumo()["score_por_modelo"][self.modelo],
        }

    def csv_interacoes(self):
        buffer = io.StringIO(newline="")
        campos = ["sessao", "partida", "data_hora", "modelo", "abordagem", "jogada", "jogador",
                  "casa", "id_tabuleiro", "estado_previsto", "estado_real", "acertou", "tipo", "fim_real"]
        escritor = csv.DictWriter(buffer, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(self.eventos)
        return buffer.getvalue()

    def _salvar_evento(self, evento):
        self.pasta.mkdir(parents=True, exist_ok=True)
        caminho = self.pasta / f"{self.nome_registro}.csv"
        novo_arquivo = not caminho.exists()
        with caminho.open("a", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=list(evento))
            if novo_arquivo:
                escritor.writeheader()
            escritor.writerow(evento)
        self._salvar_resumo()

    def _salvar_resumo(self):
        self.pasta.mkdir(parents=True, exist_ok=True)
        caminho = self.pasta / f"{self.nome_registro}.json"
        temporario = caminho.with_suffix(".tmp")
        temporario.write_text(json.dumps(self.resumo(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporario.replace(caminho)
