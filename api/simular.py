"""Função do Vercel: recebe uma proposta em JSON e devolve a avaliação do modelo (Fase 11).

Para testar no computador, rode `python api/simular.py` e abra http://localhost:8000.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# No Vercel o pacote não é instalado em modo editável: importa direto da pasta src/
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from credair import avaliar  # noqa: E402

# Parâmetros do modelo final, gerados com `python -m credair.simulador`
PARAMETROS = json.loads((RAIZ / "api" / "modelo_final.json").read_text())


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            proposta = json.loads(self.rfile.read(tamanho) or b"{}")
            self._responder(200, avaliar(proposta, PARAMETROS))
        except (ValueError, TypeError) as erro:
            self._responder(400, {"erro": str(erro)})

    def do_GET(self):
        # Só usado no teste local: serve a página de public/
        pagina = RAIZ / "public" / "index.html"
        if self.path not in ("/", "/index.html") or not pagina.exists():
            return self._responder(404, {"erro": "Não encontrado"})
        corpo = pagina.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(corpo)

    def _responder(self, status, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(corpo)


if __name__ == "__main__":
    print("Simulador em http://localhost:8000")
    ThreadingHTTPServer(("localhost", 8000), handler).serve_forever()
