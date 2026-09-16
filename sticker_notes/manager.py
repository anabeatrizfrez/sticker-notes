import json
from pathlib import Path

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap, QPolygon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import autostart
from .config import HEX_CORES, cor_valida
from .note import NotaWindow
from .paths import diretorio_dados, restringir_permissoes


def _icone_bandeja():
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(pix)
    pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
    pintor.setBrush(QColor("#FFE566"))
    pintor.setPen(QColor("#D4A017"))
    pintor.drawRoundedRect(8, 6, 48, 52, 8, 8)
    pintor.setBrush(QColor("#F5C518"))
    pintor.setPen(Qt.PenStyle.NoPen)
    pintor.drawPolygon(QPolygon([QPoint(36, 6), QPoint(56, 6), QPoint(56, 26)]))
    pintor.setPen(QColor("#A16207"))
    pintor.drawLine(18, 28, 46, 28)
    pintor.drawLine(18, 38, 42, 38)
    pintor.drawLine(18, 48, 38, 48)
    pintor.end()
    return QIcon(pix)


class AppStickerNotes:
    def __init__(self):
        self.arquivo_dados = diretorio_dados() / "notas.json"
        self.notas = []
        self.cores_personalizadas = []
        self.timer_salvamento = QTimer()
        self.timer_salvamento.setSingleShot(True)
        self.timer_salvamento.setInterval(400)
        self.timer_salvamento.timeout.connect(self.salvar_dados)
        QApplication.instance().setQuitOnLastWindowClosed(False)
        self._configurar_bandeja()
        self.carregar_dados()

    def _configurar_bandeja(self):
        self.bandeja = QSystemTrayIcon(_icone_bandeja())
        self.bandeja.setToolTip("Sticker Notes")
        menu = QMenu()
        nova = QAction("Nova nota", menu)
        nova.triggered.connect(lambda: self.criar_nota())
        menu.addAction(nova)
        mostrar = QAction("Mostrar todas", menu)
        mostrar.triggered.connect(lambda: self.mostrar_todas())
        menu.addAction(mostrar)
        ocultar = QAction("Ocultar todas", menu)
        ocultar.triggered.connect(lambda: self.ocultar_todas())
        menu.addAction(ocultar)
        if autostart.suportado():
            menu.addSeparator()
            self.acao_iniciar_com_sistema = QAction("Iniciar com o sistema", menu)
            self.acao_iniciar_com_sistema.setCheckable(True)
            self.acao_iniciar_com_sistema.setChecked(autostart.esta_habilitado())
            self.acao_iniciar_com_sistema.triggered.connect(self._alternar_autostart)
            menu.addAction(self.acao_iniciar_com_sistema)
        menu.addSeparator()
        sair = QAction("Sair", menu)
        sair.triggered.connect(lambda: self.encerrar())
        menu.addAction(sair)
        self.bandeja.setContextMenu(menu)
        self.bandeja.activated.connect(self._clique_bandeja)
        self.bandeja.show()

    def _clique_bandeja(self, motivo):
        if motivo == QSystemTrayIcon.ActivationReason.Trigger:
            if any(nota.isVisible() for nota in self.notas):
                self.ocultar_todas()
            else:
                self.mostrar_todas()
        elif motivo == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.criar_nota()

    def carregar_dados(self):
        dados = {}
        try:
            if self.arquivo_dados.exists():
                with self.arquivo_dados.open("r", encoding="utf-8") as arquivo:
                    dados = json.load(arquivo)
        except (OSError, json.JSONDecodeError):
            dados = {}

        lista = dados.get("notas") if isinstance(dados, dict) else None
        if isinstance(dados, dict):
            self.cores_personalizadas = [
                c for c in dados.get("cores_personalizadas", []) if cor_valida(c)
            ]
        if isinstance(dados, list):
            lista = dados
        if not isinstance(lista, list):
            lista = [{"texto": dados.get("texto", "")}] if isinstance(dados, dict) else []
        if not lista:
            lista = [{"texto": "", "x": 120, "y": 120, "cor": HEX_CORES[0]}]
        for nota_dados in lista:
            if isinstance(nota_dados, dict):
                normalizado = dict(nota_dados)
                if "text" in normalizado and "texto" not in normalizado:
                    normalizado["texto"] = normalizado.get("text", "")
                if "width" in normalizado and "largura" not in normalizado:
                    normalizado["largura"] = normalizado.get("width")
                if "height" in normalizado and "altura" not in normalizado:
                    normalizado["altura"] = normalizado.get("height")
                if "color" in normalizado and "cor" not in normalizado:
                    normalizado["cor"] = normalizado.get("color")
                self.criar_nota(normalizado)

    def criar_nota(self, dados=None):
        dados = dados or {
            "texto": "",
            "x": 120 + len(self.notas) * 28,
            "y": 120 + len(self.notas) * 28,
            "cor": HEX_CORES[len(self.notas) % len(HEX_CORES)],
        }
        nota = NotaWindow(self, dados)
        nota.alterada.connect(self.agendar_salvamento)
        self.notas.append(nota)
        nota.show()
        nota.raise_()
        nota.activateWindow()
        nota.area_texto.setFocus()
        self.agendar_salvamento()
        return nota

    def adicionar_cor_personalizada(self, hex_cor):
        if not cor_valida(hex_cor):
            return
        hex_cor = hex_cor.upper()
        conhecidas = {c.upper() for c in HEX_CORES} | {c.upper() for c in self.cores_personalizadas}
        if hex_cor in conhecidas:
            return
        self.cores_personalizadas.append(hex_cor)
        for nota in self.notas:
            nota.faixa_cores.adicionar_cor(hex_cor)
        self.agendar_salvamento()

    def _alternar_autostart(self, marcado):
        sucesso = autostart.alternar(marcado)
        # Nunca confia no clique por si só: relê o estado real do sistema
        # (registro/arquivo) e sincroniza a caixinha com ele, pra nunca
        # mostrar "ativado" quando na prática não gravou nada.
        self.acao_iniciar_com_sistema.setChecked(autostart.esta_habilitado())
        if marcado and not sucesso:
            self.bandeja.showMessage(
                "Sticker Notes",
                "Não foi possível ativar o início automático nesta instalação.",
                QSystemTrayIcon.MessageIcon.Warning,
            )

    def remover_nota(self, nota):
        if nota not in self.notas:
            return
        self.notas.remove(nota)
        nota.close()
        nota.deleteLater()
        self.agendar_salvamento()
        if not self.notas:
            self.criar_nota()

    def mostrar_todas(self):
        for nota in self.notas:
            nota.show()
            nota.raise_()

    def ocultar_todas(self):
        self.salvar_dados()
        for nota in self.notas:
            nota.hide()

    def encerrar(self):
        self.salvar_dados()
        self.bandeja.hide()
        QApplication.instance().quit()

    def agendar_salvamento(self):
        self.timer_salvamento.start()

    def salvar_dados(self):
        dados = {
            "versao": 3,
            "notas": [nota.dados_atualizados() for nota in self.notas],
            "cores_personalizadas": self.cores_personalizadas,
        }
        try:
            temporario = self.arquivo_dados.with_suffix(".tmp")
            with temporario.open("w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            temporario.replace(self.arquivo_dados)
            restringir_permissoes(self.arquivo_dados)
        except OSError:
            pass