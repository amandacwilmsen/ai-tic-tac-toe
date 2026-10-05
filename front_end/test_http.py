"""Verifica página, API e exportação com os modelos reais, em registros temporários."""

import csv
import io
import json
import tempfile
import threading
import unittest
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

from front_end.modelos import Classificadores
from front_end.servidor import criar_servidor


class TestHTTP(unittest.TestCase):
    def test_partida_modelos_cookies_e_exportacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            modelos = Classificadores(Path(__file__).resolve().parent.parent)
            servidor = criar_servidor(modelos, pasta, porta=0)
            thread = threading.Thread(target=servidor.serve_forever, daemon=True)
            thread.start()
            cliente = build_opener(HTTPCookieProcessor(CookieJar()))
            base = f"http://127.0.0.1:{servidor.server_port}"

            def pedir(rota, dados=None):
                pedido = Request(base + rota)
                if dados is not None:
                    pedido.data = json.dumps(dados).encode()
                    pedido.add_header("Content-Type", "application/json")
                with cliente.open(pedido, timeout=5) as resposta:
                    return resposta.read().decode(), resposta.headers

            def api(rota, dados=None):
                return json.loads(pedir(rota, dados)[0])

            try:
                for rota, trecho in [("/", "Jogo da velha"), ("/estilo.css", ".tabuleiro"),
                                     ("/app.js", "/api/maquina")]:
                    texto, _ = pedir(rota)
                    self.assertIn(trecho, texto)
                inicial = api("/api/estado")
                self.assertEqual(inicial["tabuleiro"], ["b"] * 9)
                self.assertEqual(inicial["score"]["avaliacoes"], 0)
                self.assertEqual(
                    {modelo["id"] for modelo in inicial["modelos"]},
                    {"mlp", "svm", "knn", "arvore", "random_forest"},
                )

                humano = api("/api/jogada", {"posicao": 4})
                self.assertEqual(humano["tabuleiro"][4], "x")
                self.assertEqual(humano["score"]["avaliacoes"], 1)
                self.assertEqual(humano["turno"], "o")
                with self.assertRaises(HTTPError) as erro:
                    api("/api/jogada", {"posicao": 0})
                self.assertEqual(erro.exception.code, 400)
                with self.assertRaises(HTTPError) as erro:
                    api("/api/modelo", {"modelo": "svm"})
                self.assertEqual(erro.exception.code, 400)
                maquina = api("/api/maquina", {})
                self.assertEqual(maquina["tabuleiro"].count("o"), 1)
                self.assertEqual(maquina["score"]["avaliacoes"], 2)
                self.assertEqual(api("/api/estado")["tabuleiro"], maquina["tabuleiro"])

                outro_cliente = build_opener(HTTPCookieProcessor(CookieJar()))
                with outro_cliente.open(base + "/api/estado", timeout=5) as resposta:
                    outra_sessao = json.load(resposta)
                self.assertEqual(outra_sessao["score"]["avaliacoes"], 0)

                nova = api("/api/nova", {})
                self.assertEqual(nova["historico"], [])
                self.assertEqual(nova["score"]["avaliacoes"], 2)
                for chave in ["svm", "knn", "arvore", "random_forest"]:
                    with self.subTest(modelo=chave):
                        api("/api/nova", {})
                        escolhido = api("/api/modelo", {"modelo": chave})
                        self.assertEqual(escolhido["modelo"], chave)
                        self.assertEqual(escolhido["score"]["avaliacoes"], 0)
                        api("/api/jogada", {"posicao": 0})
                        turno_maquina = api("/api/maquina", {})
                        self.assertEqual(turno_maquina["score"]["avaliacoes"], 2)

                csv_exportado, cabecalhos = pedir("/api/exportar.csv")
                linhas = list(csv.DictReader(io.StringIO(csv_exportado)))
                self.assertEqual(len(linhas), 10)
                self.assertIn("attachment", cabecalhos["Content-Disposition"])
                resumo = api("/api/exportar.json")
                self.assertEqual(resumo["score_geral"]["avaliacoes"], 10)
                for chave in modelos.informacoes:
                    self.assertEqual(resumo["score_por_modelo"][chave]["avaliacoes"], 2)
                for linha in linhas:
                    esperado = modelos.prever(linha["modelo"], list(linha["id_tabuleiro"]))
                    self.assertEqual(linha["estado_previsto"], esperado)
                salvo = list(csv.DictReader(io.StringIO(next(Path(pasta).glob("*.csv")).read_text())))
                self.assertEqual(salvo, linhas)
            finally:
                servidor.shutdown()
                servidor.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
