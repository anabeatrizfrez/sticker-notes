import os
import shutil
import subprocess
import sys
from pathlib import Path

NOME_ARQUIVO_AUTOSTART_LINUX = "sticker-notes-autostart.desktop"
_NOME_ATALHO_STARTUP         = "Sticker Notes.lnk"
_NOME_TAREFA_WINDOWS         = "StickerNotes"
_NOME_CHAVE_REGISTRO         = "StickerNotes"
_CHAVE_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"


# ── helpers ────────────────────────────────────────────────────────────────

def _executavel_windows():
    if getattr(sys, "frozen", False):
        return sys.executable
    caminho = shutil.which("sticker-notes")
    if caminho:
        return caminho
    return None


def _pasta_startup():
    try:
        import ctypes, ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 0x0007, None, 0, buf)
        return Path(buf.value) if buf.value else None
    except Exception:
        return None


def _atalho_path():
    pasta = _pasta_startup()
    return (pasta / _NOME_ATALHO_STARTUP) if pasta else None


def _criar_atalho(destino: str) -> bool:
    atalho = _atalho_path()
    if not atalho:
        return False
    script = (
        f'Set oWS = WScript.CreateObject("WScript.Shell")\n'
        f'sLinkFile = "{atalho}"\n'
        f'Set oLink = oWS.CreateShortcut(sLinkFile)\n'
        f'oLink.TargetPath = "{destino}"\n'
        f'oLink.WindowStyle = 7\n'
        f'oLink.Save\n'
    )
    vbs = Path(os.environ.get("TEMP", "C:\\Temp")) / "sticker_notes_startup.vbs"
    try:
        vbs.write_text(script, encoding="utf-8")
        resultado = subprocess.run(
            ["cscript", "//Nologo", str(vbs)],
            capture_output=True, timeout=10,
        )
        return resultado.returncode == 0 and atalho.exists()
    except (OSError, subprocess.SubprocessError):
        return False
    finally:
        try:
            vbs.unlink()
        except OSError:
            pass


def _limpar_legados():
    try:
        subprocess.run(
            ["schtasks", "/Delete", "/TN", _NOME_TAREFA_WINDOWS, "/F"],
            capture_output=True, timeout=5,
        )
    except Exception:
        pass
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _CHAVE_RUN, 0, winreg.KEY_SET_VALUE
        ) as chave:
            winreg.DeleteValue(chave, _NOME_CHAVE_REGISTRO)
    except Exception:
        pass


# ── API pública ─────────────────────────────────────────────────────────────

def suportado():
    return sys.platform == "win32" or sys.platform.startswith("linux")


def esta_habilitado():
    if sys.platform == "win32":
        atalho = _atalho_path()
        return atalho is not None and atalho.exists()
    if sys.platform.startswith("linux"):
        return _arquivo_autostart_linux().exists()
    return False


def alternar(ativar):
    if sys.platform == "win32":
        return _definir_windows(ativar)
    if sys.platform.startswith("linux"):
        return _definir_linux(ativar)
    return False


# ── Windows: atalho na pasta Startup ───────────────────────────────────────

def _definir_windows(ativar):
    _limpar_legados()
    if not ativar:
        try:
            atalho = _atalho_path()
            if atalho and atalho.exists():
                atalho.unlink()
        except OSError:
            pass
        return not esta_habilitado()

    exe = _executavel_windows()
    if not exe:
        return False
    return _criar_atalho(exe)


# ── Linux: arquivo .desktop em ~/.config/autostart ─────────────────────────

def _arquivo_autostart_linux():
    base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "autostart" / NOME_ARQUIVO_AUTOSTART_LINUX


def _sem_console(caminho_python):
    if sys.platform != "win32":
        return caminho_python
    candidato = Path(caminho_python).with_name("pythonw.exe")
    return str(candidato) if candidato.exists() else caminho_python


def _definir_linux(ativar):
    caminho = _arquivo_autostart_linux()
    if not ativar:
        try:
            caminho.unlink()
        except FileNotFoundError:
            pass
        return True
    if getattr(sys, "frozen", False):
        cmd = f'"{sys.executable}"'
    else:
        exe = shutil.which("sticker-notes")
        cmd = f'"{exe}"' if exe else f'"{_sem_console(sys.executable)}" -m sticker_notes'
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Sticker Notes\n"
            f"Exec={cmd}\n"
            "X-GNOME-Autostart-enabled=true\n"
            "NoDisplay=true\n",
            encoding="utf-8",
        )
        return True
    except OSError:
        return False