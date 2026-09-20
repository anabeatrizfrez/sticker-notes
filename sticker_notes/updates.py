# Verifica se existe uma versão mais recente publicada nas Releases do GitHub

import json
import time
import urllib.request
from urllib.error import URLError

from PyQt6.QtCore import QThread, pyqtSignal

REPOSITORIO = "anabeatrizfrez/sticker-notes"

# "version" - pyproject.toml
VERSAO_ATUAL = "1.0.0"

_URL_API = f"https://api.github.com/repos/{REPOSITORIO}/releases/latest"


# Tentativas de verificação de atualizações caso a rede ainda não esteja disponível logo após inicialização
_TENTATIVAS = [(4, 6), (15, 8), (30, 10)]

def _versao_para_tupla(versao):
    partes = []
    for pedaco in versao.strip().lstrip("vV").split("."):
        numero = "".join(c for c in pedaco if c.isdigit())
        partes.append(int(numero) if numero else 0)
    return tuple(partes) or (0,)


def ha_versao_mais_nova(atual, remota):
    return _versao_para_tupla(remota) > _versao_para_tupla(atual)


class VerificadorAtualizacao(QThread):

    encontrada = pyqtSignal(str, str)

    def run(self):
        for espera, timeout in _TENTATIVAS:
            time.sleep(espera)
            try:
                requisicao = urllib.request.Request(
                    _URL_API,
                    headers={
                        "Accept": "application/vnd.github+json",
                        "User-Agent": "sticker-notes-update-check",
                    },
                )
                with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
                    dados = json.loads(resposta.read().decode("utf-8"))
            except (URLError, TimeoutError, ValueError, OSError):
                continue
 
            tag = dados.get("tag_name") or ""
            url = dados.get("html_url") or f"https://github.com/{REPOSITORIO}/releases"
            if tag and ha_versao_mais_nova(VERSAO_ATUAL, tag):
                self.encontrada.emit(tag, url)
            return