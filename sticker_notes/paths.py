# Local onde os dados do usuário (notas, cores) são salvos

import os
import stat
import sys
from pathlib import Path

NOME_APP_WINDOWS = "StickerNotes"
NOME_APP_LINUX = "sticker-notes"
NOME_APP_MAC = "StickerNotes"


def diretorio_dados() -> Path:
    # Retorna a pasta de dados do usuário para o app, criando se não existir
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        caminho = Path(base) / NOME_APP_WINDOWS
    elif sys.platform == "darwin":
        caminho = Path.home() / "Library" / "Application Support" / NOME_APP_MAC
    else:
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        caminho = Path(base) / NOME_APP_LINUX
 
    caminho.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32":
        try:
            os.chmod(caminho, stat.S_IRWXU)
        except OSError:
            pass
    return caminho


def restringir_permissoes(arquivo: Path) -> None:
    # Apenas donos dos arquivos podem ler/escrever notas (Linux)
    if sys.platform == "win32":
        return
    try:
        os.chmod(arquivo, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass