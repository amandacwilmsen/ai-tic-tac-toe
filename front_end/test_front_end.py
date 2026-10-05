"""Testes das regras e da avaliação; os registros ficam em pastas temporárias."""

import csv
import io
import json
import random
import tempfile
import unittest
from pathlib import Path

from front_end.jogo import CLASSES, Sessao, TEM_JOGO, estado_real

MODELOS = {
    "mlp": {"nome": "MLP", "abordagem": "abordagem_2"},
    "svm": {"nome": "SVM", "abordagem": "abordagem_2"},
}
VITORIA_X = [(0, "x"), (3, "o"), (1, "x"), (4, "o"), (2, "x")]
EMPATE = [(0, "x"), (1, "o"), (2, "x"), (4, "o"), (3, "x"),
          (5, "o"), (7, "x"), (6, "o"), (8, "x")]


class TestPartidas(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

    def sessao(self, prever=None):
        return Sessao(prever or (lambda modelo, tabuleiro: estado_real(tabuleiro)), MODELOS,
                      self.temporario.name, rng=random.Random(42))

    def test_fim_incorreto_da_ia_nao_interrompe_partida(self):
        sessao = self.sessao(lambda modelo, tabuleiro: CLASSES[1])
        sessao.jogar(4)
        self.assertFalse(sessao.terminou)
        self.assertEqual(sessao.tipo_aviso, "fim_incorreto")
        self.assertEqual(sessao.estado()["score"]["erros"], 1)
        sessao.jogar_maquina()
        self.assertEqual(sessao.tabuleiro[4], "x")
        self.assertEqual(sessao.tabuleiro.count("o"), 1)
        self.assertEqual(sessao.turno, "x")

    def test_fim_nao_detectado_pela_ia_encerra_partida(self):
        sessao = self.sessao(lambda modelo, tabuleiro: TEM_JOGO)
        for posicao, jogador in VITORIA_X:
            sessao.jogar(posicao, jogador)
        self.assertTrue(sessao.terminou)
        self.assertEqual(sessao.tipo_aviso, "fim_nao_detectado")
        self.assertEqual(sessao.estado()["score"]["acuracia"], 4 / 5)
        self.assertEqual(sessao.estado()["score"]["vitorias_x"], 1)
        with self.assertRaises(ValueError):
            sessao.jogar_maquina()
        self.assertEqual(len(sessao.eventos), 5)

    def test_vencedor_incorreto_conta_erro_e_encerra(self):
        def prever(modelo, tabuleiro):
            real = estado_real(tabuleiro)
            return CLASSES[2] if real == CLASSES[1] else real
        sessao = self.sessao(prever)
        for posicao, jogador in VITORIA_X:
            sessao.jogar(posicao, jogador)
        self.assertTrue(sessao.terminou)
        self.assertEqual(sessao.tipo_aviso, "classe_incorreta")
        self.assertEqual(sessao.estado()["score"]["erros"], 1)

    def test_empate_e_contagem_apos_cada_jogada(self):
        sessao = self.sessao()
        self.assertIsNone(sessao.estado()["score"]["acuracia"])
        for posicao, jogador in EMPATE:
            sessao.jogar(posicao, jogador)
        self.assertEqual(sessao.estado()["estado_real"], "Empate")
        self.assertTrue(sessao.terminou)
        self.assertEqual(sessao.estado()["score"]["avaliacoes"], 9)
        self.assertEqual(sessao.estado()["score"]["acertos"], 9)
        self.assertEqual(sessao.estado()["score"]["empates"], 1)

    def test_jogadas_invalidas_nao_mudam_score_ou_tabuleiro(self):
        sessao = self.sessao()
        for posicao in [-1, 9, True, "0", None]:
            with self.assertRaises(ValueError):
                sessao.jogar(posicao)
        sessao.jogar(0)
        with self.assertRaises(ValueError):
            sessao.jogar(1)  # é a vez de O
        with self.assertRaises(ValueError):
            sessao.jogar(0, "o")  # casa ocupada
        self.assertEqual(len(sessao.eventos), 1)
        self.assertEqual(sessao.tabuleiro, ["x", "b", "b", "b", "b", "b", "b", "b", "b"])

    def test_nova_partida_preserva_score_e_modelos_tem_contagens_separadas(self):
        sessao = self.sessao()
        sessao.jogar(4)
        with self.assertRaises(ValueError):
            sessao.trocar_modelo("svm")
        sessao.nova_partida()
        self.assertEqual(sessao.estado()["score"]["acertos"], 1)
        self.assertEqual(sessao.historico, [])
        sessao.trocar_modelo("svm")
        self.assertEqual(sessao.estado()["score"]["avaliacoes"], 0)
        sessao.jogar(0)
        self.assertEqual(sessao.resumo()["score_por_modelo"]["mlp"]["avaliacoes"], 1)
        self.assertEqual(sessao.resumo()["score_por_modelo"]["svm"]["avaliacoes"], 1)
        self.assertEqual(sessao.resumo()["score_geral"]["avaliacoes"], 2)

    def test_csv_e_resumo_refletem_previsoes_reais(self):
        sessao = self.sessao(lambda modelo, tabuleiro: TEM_JOGO)
        for posicao, jogador in VITORIA_X:
            sessao.jogar(posicao, jogador)
        pasta = Path(self.temporario.name)
        csv_salvo = next(pasta.glob("*.csv")).read_text(encoding="utf-8")
        exportado = list(csv.DictReader(io.StringIO(sessao.csv_interacoes())))
        salvo = list(csv.DictReader(io.StringIO(csv_salvo)))
        self.assertEqual(exportado, salvo)
        self.assertEqual(len(salvo), 5)
        self.assertEqual(salvo[-1]["estado_previsto"], TEM_JOGO)
        self.assertEqual(salvo[-1]["estado_real"], CLASSES[1])
        resumo = json.loads(next(pasta.glob("*.json")).read_text())
        self.assertEqual(resumo["score_por_modelo"]["mlp"]["erros"], 1)

    def test_erro_do_classificador_nao_registra_jogada(self):
        sessao = self.sessao(lambda modelo, tabuleiro: TEM_JOGO if tabuleiro.count("b") == 9 else "inválido")
        with self.assertRaises(ValueError):
            sessao.jogar(0)
        self.assertEqual(sessao.tabuleiro, ["b"] * 9)
        self.assertEqual(sessao.eventos, [])


if __name__ == "__main__":
    unittest.main()
