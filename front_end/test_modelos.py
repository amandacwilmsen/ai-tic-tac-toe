"""Confere as entradas e previsões da interface contra os experimentos exportados."""

import unittest
from pathlib import Path

import pandas as pd

from front_end.jogo import extrair_entradas
from front_end.modelos import MODELOS, Classificadores


class TestModelos(unittest.TestCase):
    def test_cinco_modelos_preservam_entradas_e_previsoes_dos_experimentos(self):
        raiz = Path(__file__).resolve().parent.parent
        classificadores = Classificadores(raiz)
        for chave, (_, diretorio, _) in MODELOS.items():
            with self.subTest(modelo=chave):
                info = classificadores.informacoes[chave]
                preparado = pd.read_csv(
                    raiz / "dataset/processado" / info["abordagem"] / "teste.csv"
                )
                entradas_front = pd.DataFrame(
                    [extrair_entradas(list(tabuleiro), info["abordagem"])
                     for tabuleiro in preparado["id_tabuleiro"]],
                    columns=info["features"],
                )
                pd.testing.assert_frame_equal(
                    entradas_front, preparado[info["features"]], check_dtype=False,
                )
                registros = pd.read_csv(
                    raiz / "dataset/processado" / diretorio / "resultados/previsoes_teste.csv"
                )
                registros = registros[registros["abordagem"] == info["abordagem"]]
                self.assertEqual(len(registros), len(preparado))
                self.assertEqual(registros["id_tabuleiro"].tolist(), preparado["id_tabuleiro"].tolist())
                self.assertEqual(registros["estado_real"].tolist(), preparado["estado"].tolist())
                previsto = [classificadores.prever(chave, list(tabuleiro))
                            for tabuleiro in preparado["id_tabuleiro"]]
                self.assertEqual(previsto, registros["estado_previsto"].tolist())


if __name__ == "__main__":
    unittest.main()
