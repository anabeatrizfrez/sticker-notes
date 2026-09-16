# Iniciar o Sticker Notes automaticamente ao ligar o computador 

import os
import shutil
import subprocess
import sys
from pathlib import Path

NOME_ARQUIVO_AUTOSTART_LINUX = "sticker-notes-autostart.desktop"
_NOME_TAREFA_WINDOWS = "StickerNotes"


def _comando_executavel():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    caminho = shutil.which("sticker-notes")
    if caminho:
        return f'"{caminho}"'

    if sys.executable:
        interprete = _sem_console(sys.executable)
        return f'"{interprete}" -m sticker_notes'

    return None


def _sem_console(caminho_python):
    if sys.platform != "win32":
        return caminho_python
    candidato = Path(caminho_python).with_name("pythonw.exe")
    return str(candidato) if candidato.exists() else caminho_python


def suportado():
    return sys.platform in ("win32",) or sys.platform.startswith("linux")


def esta_habilitado():
    if sys.platform == "win32":
        return _esta_habilitado_windows()
    if sys.platform.startswith("linux"):
        return _arquivo_autostart_linux().exists()
    return False


def alternar(ativar):
    if sys.platform == "win32":
        return _definir_windows(ativar)
    if sys.platform.startswith("linux"):
        return _definir_linux(ativar)
    return False


# --- Windows: Gatilho "ao fazer logon" ---


def _esta_habilitado_windows():
    try:
        resultado = subprocess.run(
            ["schtasks", "/Query", "/TN", _NOME_TAREFA_WINDOWS],
            capture_output=True,
            timeout=5,
        )
        return resultado.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _definir_windows(ativar):
    try:
        if ativar:
            comando = _comando_executavel()
            if not comando:
                return False
            subprocess.run(
                [
                    "schtasks", "/Create", "/SC", "ONLOGON",
                    "/TN", _NOME_TAREFA_WINDOWS,
                    "/TR", comando,
                    "/RL", "LIMITED",
                    "/F",
                ],
                capture_output=True,
                timeout=5,
            )
        else:
            subprocess.run(
                ["schtasks", "/Delete", "/TN", _NOME_TAREFA_WINDOWS, "/F"],
                capture_output=True,
                timeout=5,
            )
        return esta_habilitado() == ativar
    except (OSError, subprocess.SubprocessError):
        return False


# --- Linux: arquivo .desktop em ~/.config/autostart ---


def _arquivo_autostart_linux():
    base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "autostart" / NOME_ARQUIVO_AUTOSTART_LINUX


def _definir_linux(ativar):
    caminho = _arquivo_autostart_linux()
    if not ativar:
        try:
            caminho.unlink()
        except FileNotFoundError:
            pass
        return True
    comando = _comando_executavel()
    if not comando:
        return False
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Sticker Notes\n"
            f"Exec={comando}\n"
            "X-GNOME-Autostart-enabled=true\n"
            "NoDisplay=true\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def _arquivo_autostart_linux():
    base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "autostart" / NOME_ARQUIVO_AUTOSTART_LINUX


def _definir_linux(ativar):
    caminho = _arquivo_autostart_linux()
    if not ativar:
        try:
            caminho.unlink()
        except FileNotFoundError:
            pass
        return True
    comando = _comando_executavel()
    if not comando:
        return False
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Sticker Notes\n"
            f"Exec={comando}\n"
            "X-GNOME-Autostart-enabled=true\n"
            "NoDisplay=true\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False