import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from .config import FONTE_UI
from .manager import AppStickerNotes


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sticker Notes")
    app.setOrganizationName("Sticker Notes")
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    app.setFont(QFont(FONTE_UI, 10))
    gerenciador = AppStickerNotes()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
