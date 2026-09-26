import atexit
import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from .config import FONTE_UI
from .manager import AppStickerNotes
from . import single_instance


def main():
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

    gerenciador = AppStickerNotes()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()