"""Servidor local da interface e das ações de jogo, com sessões por navegador.

Execute na raiz: python front_end/servidor.py. Endereço: http://127.0.0.1:8765.
"""

import argparse
import json
import sys
import threading
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

# Permite executar tanto como arquivo quanto com python -m front_end.servidor.
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from front_end.jogo import Sessao
from front_end.modelos import Classificadores

PASTA_FRONT = Path(__file__).resolve().parent


def criar_servidor(classificadores, pasta_registros, porta=8765):
    """Serve a interface e coordena o acesso às sessões e aos registros de avaliação."""
    sessoes = {}
    lock_sessoes = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def responder(self, corpo, tipo="application/json; charset=utf-8", status=200, nome=None):
            if not isinstance(corpo, bytes):
                corpo = corpo.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            if getattr(self, "nova_sessao", None):
                self.send_header("Set-Cookie", f"velha_sessao={self.nova_sessao}; Path=/; HttpOnly; SameSite=Strict")
            if nome:
                self.send_header("Content-Disposition", f'attachment; filename="{nome}"')
            self.end_headers()
            self.wfile.write(corpo)

        def responder_json(self, dados, status=200):
            self.responder(json.dumps(dados, ensure_ascii=False), status=status)

        def obter_sessao(self):
            cookie = SimpleCookie()
            cookie.load(self.headers.get("Cookie", ""))
            sid = cookie["velha_sessao"].value if "velha_sessao" in cookie else None
            with lock_sessoes:
                if sid not in sessoes:
                    sessao = Sessao(classificadores.prever, classificadores.informacoes, pasta_registros)
                    sessoes[sessao.id] = sessao
                    self.nova_sessao = sessao.id
                    return sessao
                return sessoes[sid]

        def do_GET(self):
            rota = urlsplit(self.path).path
            estaticos = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/estilo.css": ("estilo.css", "text/css; charset=utf-8"),
                "/app.js": ("app.js", "text/javascript; charset=utf-8"),
            }
            if rota in estaticos:
                arquivo, tipo = estaticos[rota]
                self.responder((PASTA_FRONT / arquivo).read_bytes(), tipo)
            elif rota in ["/api/estado", "/api/exportar.csv", "/api/exportar.json"]:
                sessao = self.obter_sessao()
                with sessao.lock:
                    if rota == "/api/estado":
                        self.responder_json(sessao.estado())
                    elif rota.endswith(".csv"):
                        self.responder(sessao.csv_interacoes(), "text/csv; charset=utf-8",
                                       nome=f"{sessao.nome_registro}.csv")
                    else:
                        self.responder(json.dumps(sessao.resumo(), ensure_ascii=False, indent=2),
                                       nome=f"{sessao.nome_registro}.json")
            elif rota == "/favicon.ico":
                self.responder(b"", status=204)
            else:
                self.responder_json({"erro": "Página não encontrada."}, 404)

        def do_POST(self):
            rota = urlsplit(self.path).path
            if rota not in ["/api/jogada", "/api/maquina", "/api/nova", "/api/modelo"]:
                self.responder_json({"erro": "Ação não encontrada."}, 404)
                return
            try:
                tamanho = int(self.headers.get("Content-Length", "0"))
                if not 0 <= tamanho <= 4096:
                    raise ValueError("Pedido inválido.")
                pedido = json.loads(self.rfile.read(tamanho) or b"{}")
                if not isinstance(pedido, dict):
                    raise ValueError("Pedido inválido.")
                sessao = self.obter_sessao()
                with sessao.lock:
                    if rota == "/api/jogada":
                        sessao.jogar(pedido.get("posicao"))
                    elif rota == "/api/maquina":
                        sessao.jogar_maquina()
                    elif rota == "/api/modelo":
                        sessao.trocar_modelo(pedido.get("modelo"))
                    else:
                        sessao.nova_partida()
                    self.responder_json(sessao.estado())
            except (ValueError, json.JSONDecodeError) as erro:
                self.responder_json({"erro": str(erro)}, 400)
            except Exception as erro:
                print(f"Falha no front end: {erro}", file=sys.stderr)
                self.responder_json({"erro": "Não foi possível concluir a ação. Recarregue a página."}, 500)

    return ThreadingHTTPServer(("127.0.0.1", porta), Handler)


def main():
    parser = argparse.ArgumentParser(description="Jogo da velha com avaliação dos cinco classificadores.")
    parser.add_argument("--porta", type=int, default=8765)
    parser.add_argument("--registros", type=Path, default=PASTA_FRONT / "resultados")
    args = parser.parse_args()
    try:
        modelos = Classificadores(RAIZ)
        servidor = criar_servidor(modelos, args.registros, args.porta)
    except (ValueError, FileNotFoundError, OSError) as erro:
        parser.exit(1, f"Não foi possível iniciar: {erro}\n")
    print(f"Abra http://127.0.0.1:{servidor.server_port}", flush=True)
    print("Para encerrar, pressione Ctrl+C.", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
