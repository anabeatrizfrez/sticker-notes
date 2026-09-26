import os
import shutil
import subprocess
import sys
from pathlib import Path

NOME_ARQUIVO_AUTOSTART_LINUX = "sticker-notes-autostart.desktop"
_NOME_TAREFA_WINDOWS       = "StickerNotes"
_NOME_ATALHO_STARTUP       = "Sticker Notes.lnk"
_NOME_CHAVE_REGISTRO       = "StickerNotes"   # legado
_CHAVE_RUN                 = r"Software\Microsoft\Windows\CurrentVersion\Run"


# ── helpers ────────────────────────────────────────────────────────────────

def _comando_executavel():
    """Retorna o comando certo para reabrir o app sozinho."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    caminho = shutil.which("sticker-notes")
    if caminho:
        return f'"{caminho}"'
    if sys.executable:
        return f'"{_sem_console(sys.executable)}" -m sticker_notes'
    return None


def _sem_console(caminho_python):
    if sys.platform != "win32":
        return caminho_python
    candidato = Path(caminho_python).with_name("pythonw.exe")
    return str(candidato) if candidato.exists() else caminho_python


def _pasta_startup_windows():
    import ctypes.wintypes
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 0x0007, None, 0, buf)
    return Path(buf.value) if buf.value else None


def _atalho_startup_existe():
    try:
        pasta = _pasta_startup_windows()
        return pasta is not None and (pasta / _NOME_ATALHO_STARTUP).exists()
    except Exception:
        return False


def _remover_legado_registro():
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _CHAVE_RUN, 0, winreg.KEY_SET_VALUE
        ) as chave:
            winreg.DeleteValue(chave, _NOME_CHAVE_REGISTRO)
    except Exception:
        pass  # já não existe ou sem permissão — tudo bem


# ── API pública ─────────────────────────────────────────────────────────────

def suportado():
    return sys.platform == "win32" or sys.platform.startswith("linux")


def esta_habilitado():
    if sys.platform == "win32":
        return _tarefa_existe() or _atalho_startup_existe()
    if sys.platform.startswith("linux"):
        return _arquivo_autostart_linux().exists()
    return False


def alternar(ativar):
    if sys.platform == "win32":
        return _definir_windows(ativar)
    if sys.platform.startswith("linux"):
        return _definir_linux(ativar)
    return False


# ── Windows: Tarefa Agendada ────────────────────────────────────────────────

def _tarefa_existe():
    try:
        r = subprocess.run(
            ["schtasks", "/Query", "/TN", _NOME_TAREFA_WINDOWS],
            capture_output=True, timeout=5,
        )
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _definir_windows(ativar):
    _remover_legado_registro()
    try:
        if ativar:
            if _atalho_startup_existe():
                return True
            comando = _comando_executavel()
            if not comando:
                return False
            subprocess.run(
                ["schtasks", "/Create", "/SC", "ONLOGON",
                 "/TN", _NOME_TAREFA_WINDOWS,
                 "/TR", comando,
                 "/RL", "LIMITED", "/F"],
                capture_output=True, timeout=5,
            )
        else:
            subprocess.run(
                ["schtasks", "/Delete", "/TN", _NOME_TAREFA_WINDOWS, "/F"],
                capture_output=True, timeout=5,
            )
            try:
                pasta = _pasta_startup_windows()
                if pasta:
                    atalho = pasta / _NOME_ATALHO_STARTUP
                    if atalho.exists():
                        atalho.unlink()
            except Exception:
                pass
        return esta_habilitado() == ativar
    except (OSError, subprocess.SubprocessError):
        return False


# ── Linux: arquivo .desktop em ~/.config/autostart ─────────────────────────

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