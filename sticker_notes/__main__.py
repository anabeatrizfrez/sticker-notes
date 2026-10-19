import atexit
import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from .config import FONTE_UI
from .manager import AppStickerNotes
from . import single_instance


_AVISOS_IGNORADOS = {
    "does not support setting window opacity",
    "does not support raise",
}


def _filtro_mensagens_qt(tipo, contexto, mensagem):
    if any(trecho in mensagem for trecho in _AVISOS_IGNORADOS):
        return
    print(f"[Qt] {mensagem}", file=sys.stderr)


def main():
    from PyQt6.QtCore import qInstallMessageHandler
    qInstallMessageHandler(_filtro_mensagens_qt)

    app = QApplication(sys.argv)
    app.setApplicationName("Sticker Notes")
    app.setOrganizationName("Sticker Notes")
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    app.setFont(QFont(FONTE_UI, 10))

    if not single_instance.adquirir():
        QMessageBox.information(
            None,
            "Sticker Notes",
            "O Sticker Notes já está aberto.\n"
            "Verifique o ícone na bandeja do sistema.",
        )
        sys.exit(0)

    atexit.register(single_instance.liberar)

    gerenciador = AppStickerNotes()  # noqa: F841
    sys.exit(app.exec())


if __name__ == "__main__":
    main()