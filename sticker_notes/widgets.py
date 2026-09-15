from PyQt6.QtCore import QPoint, QPointF, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QPolygon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QSizeGrip,
    QTextEdit,
    QToolButton,
    QWidget,
)

from .config import CORES_NOTA
from .icons import icone


class BotaoNota(QToolButton):
    def __init__(self, dica, parent=None, nome_icone=None, tamanho=28, tamanho_icone=16):
        super().__init__(parent)
        self.nome_icone = nome_icone
        self.setToolTip(dica)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(tamanho, tamanho)
        self.setIconSize(QSize(tamanho_icone, tamanho_icone))
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet("QToolButton { padding: 0; margin: 0; }")

    def pintar(self, cor_tinta, preenchido=None):
        if not self.nome_icone:
            return
        nome = self.nome_icone
        if preenchido is not None and nome in {"pin", "pin-on"}:
            nome = "pin-on" if preenchido else "pin"
        self.setIcon(icone(nome, cor_tinta, 16))


class PontoCor(QWidget):
    clicado = pyqtSignal(str)

    def __init__(self, hex_cor, nome="", parent=None):
        super().__init__(parent)
        self.hex_cor = hex_cor
        self.selecionado = False
        self.setFixedSize(22, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(nome or hex_cor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._hover = False

    def definir_selecionado(self, ativo):
        self.selecionado = ativo
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicado.emit(self.hex_cor)
            event.accept()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)
        if self.selecionado or self._hover:
            anel = QColor(0, 0, 0, 55 if self.selecionado else 30)
            p.setPen(QPen(anel, 1.6))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(self.rect().adjusted(1, 1, -1, -1))
        p.setPen(QPen(QColor(0, 0, 0, 38), 1))
        p.setBrush(QColor(self.hex_cor))
        p.drawEllipse(rect)


class BotaoPersonalizarCor(QWidget):
    clicado = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Escolher outra cor")
        self.cor_tinta = "#44403C"
        self._hover = False

    def pintar(self, cor_tinta):
        self.cor_tinta = cor_tinta
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicado.emit()
            event.accept()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(self.cor_tinta), 1.3))
        p.setBrush(QColor(255, 255, 255, 90 if self._hover else 40))
        p.drawEllipse(self.rect().adjusted(2, 2, -2, -2))
        cx, cy = 11, 11
        p.drawLine(cx, 6, cx, 16)
        p.drawLine(6, cy, 16, cy)


class FaixaCores(QFrame):
    cor_escolhida = pyqtSignal(str)
    personalizar = pyqtSignal()
    COLUNAS = 6

    def __init__(self, parent=None, cores_extras=None):
        super().__init__(parent)
        self.setObjectName("faixaCores")
        self.grade = QGridLayout(self)
        self.grade.setContentsMargins(10, 4, 10, 8)
        self.grade.setHorizontalSpacing(8)
        self.grade.setVerticalSpacing(6)
        self.pontos = []
        for nome, hex_cor in CORES_NOTA:
            self._adicionar_ponto(hex_cor, nome)
        for hex_cor in cores_extras or []:
            self._adicionar_ponto(hex_cor, "Personalizada")
        self.botao_mais = BotaoPersonalizarCor(self)
        self.botao_mais.clicado.connect(self.personalizar.emit)
        self._posicionar_extra()

    def _adicionar_ponto(self, hex_cor, nome):
        if any(p.hex_cor.lower() == hex_cor.lower() for p in self.pontos):
            return
        ponto = PontoCor(hex_cor, nome, self)
        ponto.clicado.connect(self.cor_escolhida.emit)
        indice = len(self.pontos)
        self.grade.addWidget(ponto, indice // self.COLUNAS, indice % self.COLUNAS, Qt.AlignmentFlag.AlignCenter)
        self.pontos.append(ponto)

    def adicionar_cor(self, hex_cor):
        antes = len(self.pontos)
        self._adicionar_ponto(hex_cor, "Personalizada")
        if len(self.pontos) != antes:
            self._posicionar_extra()

    def _posicionar_extra(self):
        total = len(self.pontos)
        self.grade.addWidget(
            self.botao_mais, total // self.COLUNAS, total % self.COLUNAS, Qt.AlignmentFlag.AlignCenter
        )
        linhas = total // self.COLUNAS + 1
        self.setFixedHeight(max(56, 18 + linhas * 30))

    def marcar(self, hex_cor):
        atual = (hex_cor or "").lower()
        bateu = False
        for ponto in self.pontos:
            igual = ponto.hex_cor.lower() == atual
            ponto.definir_selecionado(igual)
            bateu = bateu or igual
        self.botao_mais.setToolTip("Cor personalizada" if not bateu else "Escolher outra cor")


class Redimensionador(QSizeGrip):
    def __init__(self, parent, cor="#8D6E63"):
        super().__init__(parent)
        self.cor = cor

    def definir_cor(self, cor):
        self.cor = cor
        self.update()

    def paintEvent(self, event):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        pintor.setPen(Qt.PenStyle.NoPen)
        pintor.setBrush(QColor(self.cor))
        pintor.setOpacity(0.55)
        pintor.drawPolygon(QPolygon([QPoint(16, 5), QPoint(16, 16), QPoint(5, 16)]))


class BarraNota(QFrame):
    arrastando = pyqtSignal(QPoint)
    soltou = pyqtSignal()

    def __init__(self, nota):
        super().__init__(nota)
        self.nota = nota
        self.ponto_inicial = None
        self._arrastando = False
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setObjectName("barraNota")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        self.botao_cor = BotaoNota("Cor da nota", nome_icone="gota")
        self.botao_cor.setCheckable(True)
        self.botao_cor.clicked.connect(nota.alternar_paleta)
        layout.addWidget(self.botao_cor)

        self.botao_nova = BotaoNota(
            "Nova nota  (Ctrl+N)", nome_icone="mais", tamanho=30, tamanho_icone=18
        )
        self.botao_nova.clicked.connect(lambda: nota.gerenciador.criar_nota())
        layout.addWidget(self.botao_nova)

        layout.addStretch()

        self.botao_menu = BotaoNota("Mais opções", nome_icone="pontos")
        self.botao_menu.clicked.connect(nota.mostrar_menu_do_botao)
        layout.addWidget(self.botao_menu)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            filho = self.childAt(event.position().toPoint())
            if isinstance(filho, QToolButton) or isinstance(filho, PontoCor):
                return
            self.ponto_inicial = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.ponto_inicial is not None:
            if not self._arrastando:
                self._arrastando = True
                self.nota.iniciar_feedback_arraste()
            self.arrastando.emit(event.globalPosition().toPoint() - self.ponto_inicial)
            self.ponto_inicial = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self.ponto_inicial = None
        if self._arrastando:
            self._arrastando = False
            self.nota.finalizar_feedback_arraste()
        self.soltou.emit()
        event.accept()


class BarraFerramentas(QFrame):
    def __init__(self, nota):
        super().__init__(nota)
        self.nota = nota
        self.setObjectName("barraFerramentas")
        self.setFixedHeight(34)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 22, 6)
        layout.setSpacing(1)

        self.botao_negrito = BotaoNota("Negrito  (Ctrl+B)", nome_icone="negrito")
        self.botao_negrito.setCheckable(True)
        self.botao_negrito.clicked.connect(nota.alternar_negrito)
        layout.addWidget(self.botao_negrito)

        self.botao_italico = BotaoNota("Itálico  (Ctrl+I)", nome_icone="italico")
        self.botao_italico.setCheckable(True)
        self.botao_italico.clicked.connect(nota.alternar_italico)
        layout.addWidget(self.botao_italico)

        self.botao_sublinhado = BotaoNota("Sublinhado  (Ctrl+U)", nome_icone="sublinhado")
        self.botao_sublinhado.setCheckable(True)
        self.botao_sublinhado.clicked.connect(nota.alternar_sublinhado)
        layout.addWidget(self.botao_sublinhado)

        layout.addStretch()

    def pintar(self, cor_tinta):
        for botao in (self.botao_negrito, self.botao_italico, self.botao_sublinhado):
            botao.pintar(cor_tinta)


class AreaTexto(QTextEdit):
    def __init__(self, nota):
        super().__init__(nota)
        self.nota = nota
        self.setAcceptRichText(True)
        self.setPlaceholderText("Escreva sua anotação…")
        self.setTabChangesFocus(False)
        self.setUndoRedoEnabled(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.viewport().setCursor(Qt.CursorShape.SizeAllCursor)
        self._ponto_pressionado = None
        self._pos_local_pressionada = None
        self._arrastando_nota = False
        self._clique_pendente = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._clique_em_tarefa(event.pos()):
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            pos_local = event.position().toPoint()
            # Desfocada: a nota inteira é uma alça de arraste (um clique sem
            # mover ainda foca normalmente). Focada: só vira arraste se o
            # clique começar numa área sem nenhum caractere de verdade.
            permite_arraste = not self.hasFocus() or self._ponto_em_area_vazia(pos_local)
            if permite_arraste:
                self._ponto_pressionado = event.globalPosition().toPoint()
                self._pos_local_pressionada = pos_local
                self._arrastando_nota = False
                self._clique_pendente = True
                event.accept()
                return
        self._ponto_pressionado = None
        self._clique_pendente = False
        super().mousePressEvent(event)

    def _ponto_em_area_vazia(self, pos_local):
        ponto_doc = QPointF(
            pos_local.x() + self.horizontalScrollBar().value(),
            pos_local.y() + self.verticalScrollBar().value(),
        )
        posicao = self.document().documentLayout().hitTest(ponto_doc, Qt.HitTestAccuracy.ExactHit)
        return posicao == -1

    def mouseMoveEvent(self, event):
        if self._ponto_pressionado is not None and event.buttons() & Qt.MouseButton.LeftButton:
            ponto_atual = event.globalPosition().toPoint()
            if not self._arrastando_nota:
                distancia = (ponto_atual - self._ponto_pressionado).manhattanLength()
                if distancia < QApplication.startDragDistance():
                    event.accept()
                    return
                self._arrastando_nota = True
                self._clique_pendente = False
                self.viewport().setCursor(Qt.CursorShape.SizeAllCursor)
                self.nota.iniciar_feedback_arraste()
            self.nota.mover_por_arraste(ponto_atual - self._ponto_pressionado)
            self._ponto_pressionado = ponto_atual
            event.accept()
            return
        self._atualizar_cursor_hover(event.position().toPoint())
        super().mouseMoveEvent(event)

    def _atualizar_cursor_hover(self, pos_local):
        if self._area_da_tarefa(pos_local):
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        elif not self.hasFocus():
            self.viewport().setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)

    def mouseReleaseEvent(self, event):
        if self._arrastando_nota:
            self._arrastando_nota = False
            self._ponto_pressionado = None
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
            self.nota.finalizar_feedback_arraste()
            self.nota.emitir_alteracao()
            event.accept()
            return
        if self._clique_pendente:
            self._clique_pendente = False
            self._ponto_pressionado = None
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self.setTextCursor(self.cursorForPosition(self._pos_local_pressionada))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        self.nota.atualizar_cromo()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.viewport().setCursor(Qt.CursorShape.SizeAllCursor)
        QTimer.singleShot(0, self.nota.atualizar_cromo)

    def _area_da_tarefa(self, pos):
        cursor = self.cursorForPosition(pos)
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        texto = cursor.block().text()
        if not _eh_tarefa(texto):
            return False
        area = self.cursorRect(cursor)
        return pos.x() <= area.x() + 26

    def _clique_em_tarefa(self, pos):
        if not self._area_da_tarefa(pos):
            return False
        self.nota.alternar_tarefa()
        return True


def _eh_tarefa(texto):
    return texto.startswith(("[ ]", "[x]", "[X]", "☐ ", "☑ ", "☐", "☑"))
