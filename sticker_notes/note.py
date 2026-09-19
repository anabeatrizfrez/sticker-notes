from PyQt6.QtCore import QPoint, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QKeySequence, QTextCharFormat
from PyQt6.QtWidgets import (
    QApplication,
    QColorDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QMainWindow,
    QMenu,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from .config import (
    ALTURA_MINIMA,
    ALTURA_PADRAO,
    CORES_NOTA,
    FONTE_UI,
    HEX_CORES,
    LARGURA_MINIMA,
    LARGURA_PADRAO,
    MARGEM_SOMBRA,
    OPACIDADE_MINIMA,
    OPACIDADE_PADRAO,
    TAMANHO_FONTE,
    cor_valida,
    numero_seguro,
)
from .icons import icone_cor
from .widgets import AreaTexto, BarraFerramentas, BarraNota, FaixaCores, Redimensionador


NIVEIS_OPACIDADE = (1.0, 0.88, 0.72)


def _luminancia(hex_cor):
    cor = QColor(hex_cor)
    return (0.299 * cor.red() + 0.587 * cor.green() + 0.114 * cor.blue()) / 255


def _cor_texto(hex_cor):
    return "#1C1917" if _luminancia(hex_cor) > 0.55 else "#FAFAF9"


def _cor_suave(hex_cor, fator=112):
    return QColor(hex_cor).darker(fator).name()


class NotaWindow(QMainWindow):
    alterada = pyqtSignal()

    def __init__(self, gerenciador, dados):
        super().__init__()
        self.gerenciador = gerenciador
        self.dados = dados if isinstance(dados, dict) else {}
        # Checa tipos de dados
        opacidade_lida = numero_seguro(self.dados.get("opacidade"), OPACIDADE_PADRAO)
        self.opacidade = max(OPACIDADE_MINIMA, min(1.0, opacidade_lida))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setMinimumSize(LARGURA_MINIMA + MARGEM_SOMBRA * 2, ALTURA_MINIMA + MARGEM_SOMBRA * 2)
        x = int(numero_seguro(self.dados.get("x"), 100))
        y = int(numero_seguro(self.dados.get("y"), 100))
        largura = int(numero_seguro(self.dados.get("largura"), LARGURA_PADRAO))
        altura = int(numero_seguro(self.dados.get("altura"), ALTURA_PADRAO))
        self.setGeometry(
            x,
            y,
            max(LARGURA_MINIMA, largura) + MARGEM_SOMBRA * 2,
            max(ALTURA_MINIMA, altura) + MARGEM_SOMBRA * 2,
        )
        cor_lida = self.dados.get("cor", HEX_CORES[0])
        self.cor = cor_lida if cor_valida(cor_lida) else HEX_CORES[0]
        self.configurar_interface()
        if self.dados.get("html"):
            self.area_texto.setHtml(self.dados["html"])
        else:
            self.area_texto.setPlainText(self.dados.get("texto", ""))
        self.setWindowOpacity(self.opacidade)
        if self.dados.get("sempre_visivel", False):
            self.alternar_sempre_visivel(True)

    def configurar_interface(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Sticker Notes")

        raiz = QWidget()
        raiz.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        envelope = QVBoxLayout(raiz)
        envelope.setContentsMargins(MARGEM_SOMBRA, MARGEM_SOMBRA, MARGEM_SOMBRA, MARGEM_SOMBRA)
        envelope.setSpacing(0)

        self.container = QFrame()
        self.container.setObjectName("containerNota")
        self.container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.sombra = QGraphicsDropShadowEffect(self.container)
        self.sombra.setBlurRadius(26)
        self.sombra.setOffset(0, 3)
        self.sombra.setColor(QColor(0, 0, 0, 38))
        self.container.setGraphicsEffect(self.sombra)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._chrome_travado = False

        self.barra = BarraNota(self)
        self.barra.arrastando.connect(self.mover_por_arraste)
        self.barra.soltou.connect(self.emitir_alteracao)
        self.barra.hide()
        layout.addWidget(self.barra)

        self.faixa_cores = FaixaCores(self, self.gerenciador.cores_personalizadas)
        self.faixa_cores.cor_escolhida.connect(self.mudar_cor)
        self.faixa_cores.personalizar.connect(self.escolher_cor)
        self.faixa_cores.hide()
        layout.addWidget(self.faixa_cores)

        self.area_texto = AreaTexto(self)
        self.area_texto.textChanged.connect(self.emitir_alteracao)
        self.area_texto.currentCharFormatChanged.connect(self.atualizar_botoes_formato)
        layout.addWidget(self.area_texto)

        self.ferramentas = BarraFerramentas(self)
        self.ferramentas.hide()
        layout.addWidget(self.ferramentas)

        self.redimensionador = Redimensionador(self.container)
        self.redimensionador.setFixedSize(18, 18)
        self.redimensionador.setStyleSheet("background: transparent;")

        envelope.addWidget(self.container)
        self.setCentralWidget(raiz)
        self.aplicar_estilo()
        self.configurar_atalhos()
        self.configurar_menu_contexto()
        self._posicionar_redimensionador()
        QTimer.singleShot(0, self._posicionar_redimensionador)

    def configurar_atalhos(self):
        atalhos = [
            ("Ctrl+N", self.gerenciador.criar_nota),
            ("Ctrl+D", self.duplicar),
            ("Ctrl+S", self.gerenciador.salvar_dados),
            ("Ctrl+W", self.pedir_exclusao),
            ("Ctrl+T", self.adicionar_lista_tarefas),
            ("Ctrl+P", lambda: self.alternar_sempre_visivel(not self.esta_fixada())),
            ("Ctrl+Shift+C", self.proxima_cor),
            ("Ctrl+B", self.ferramentas.botao_negrito.click),
            ("Ctrl+I", self.ferramentas.botao_italico.click),
            ("Ctrl+U", self.ferramentas.botao_sublinhado.click),
            (
                "Ctrl+Shift+X",
                lambda: self.alternar_riscado(not self.area_texto.currentCharFormat().fontStrikeOut()),
            ),
        ]
        for tecla, destino in atalhos:
            acao = QAction(self)
            acao.setShortcut(QKeySequence(tecla))
            acao.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            acao.triggered.connect(lambda _, fn=destino: fn())
            self.addAction(acao)

    def aplicar_estilo(self):
        borda = _cor_suave(self.cor, 108)
        texto = _cor_texto(self.cor)
        linha = QColor(texto)
        linha.setAlpha(28)
        linha_css = f"rgba({linha.red()}, {linha.green()}, {linha.blue()}, {linha.alpha()})"
        self.redimensionador.definir_cor(QColor(texto).name())
        self.faixa_cores.marcar(self.cor)
        self.faixa_cores.botao_mais.pintar(texto)
        self._pintar_icones(texto)
        self.setStyleSheet(
            f"""
            QMainWindow {{ background: transparent; }}
            QFrame#containerNota {{
                background-color: {self.cor};
                border: 1px solid {borda};
                border-radius: 12px;
            }}
            QFrame#barraNota {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {linha_css};
            }}
            QFrame#faixaCores {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {linha_css};
            }}
            QFrame#barraFerramentas {{
                background: transparent;
                border: none;
                border-top: 1px solid {linha_css};
            }}
            QTextEdit {{
                background: transparent;
                border: none;
                padding: 8px 14px 4px 14px;
                font-family: '{FONTE_UI}';
                font-size: {TAMANHO_FONTE}pt;
                color: {texto};
                selection-background-color: rgba(0, 0, 0, 28);
            }}
            QToolButton {{
                background: transparent;
                border: none;
                border-radius: 7px;
                padding: 0;
            }}
            QToolButton:hover {{ background: rgba(0, 0, 0, 0.08); }}
            QToolButton:checked {{ background: rgba(0, 0, 0, 0.12); }}
            QMenu {{
                background: #FFFEF8;
                border: 1px solid #E7E5E4;
                border-radius: 10px;
                padding: 6px;
                font-family: '{FONTE_UI}';
                color: #3A362E;
            }}
            QMenu::item {{ padding: 6px 16px; border-radius: 6px; color: #3A362E; }}
            QMenu::item:disabled {{ color: #B9B4A8; }}
            QMenu::item:selected {{ background: rgba(0, 0, 0, 0.08); color: #3A362E; }}
            QMenu::separator {{ height: 1px; background: #E7E5E4; margin: 6px 4px; }}
            """
        )

    def _pintar_icones(self, tinta):
        self.barra.botao_cor.pintar(tinta)
        self.barra.botao_nova.pintar(tinta)
        self.barra.botao_menu.pintar(tinta)
        self.ferramentas.pintar(tinta)
        self.redimensionador.definir_cor(tinta)

    def atualizar_cromo(self):
        visivel = self.area_texto.hasFocus() or self._chrome_travado
        self.barra.setVisible(visivel)
        self.ferramentas.setVisible(visivel)
        if not visivel:
            self.faixa_cores.hide()
            self.barra.botao_cor.setChecked(False)

    def mostrar_menu_do_botao(self):
        botao = self.barra.botao_menu
        ponto = botao.mapToGlobal(QPoint(0, botao.height()))
        self._exibir_menu(ponto)

    def configurar_menu_contexto(self):
        for widget in (self.container, self.barra, self.area_texto, self.ferramentas):
            widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            widget.customContextMenuRequested.connect(self.mostrar_menu)

    def mover_por_arraste(self, delta):
        self.move(self.pos() + delta)

    def iniciar_feedback_arraste(self):
        self.sombra.setBlurRadius(38)
        self.sombra.setOffset(0, 10)
        self.sombra.setColor(QColor(0, 0, 0, 70))
        self.setWindowOpacity(min(self.opacidade, 0.94))

    def finalizar_feedback_arraste(self):
        self.sombra.setBlurRadius(26)
        self.sombra.setOffset(0, 3)
        self.sombra.setColor(QColor(0, 0, 0, 38))
        self.setWindowOpacity(self.opacidade)

    def emitir_alteracao(self):
        self.alterada.emit()

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, "dados"):
            self.emitir_alteracao()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._posicionar_redimensionador()
        if hasattr(self, "dados"):
            self.emitir_alteracao()

    def _posicionar_redimensionador(self):
        if not hasattr(self, "redimensionador"):
            return
        largura_container = self.width() - MARGEM_SOMBRA * 2
        altura_container = self.height() - MARGEM_SOMBRA * 2
        self.redimensionador.move(
            largura_container - self.redimensionador.width() - 4,
            altura_container - self.redimensionador.height() - 4,
        )
        self.redimensionador.raise_()

    def esta_fixada(self):
        return bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)

    def alternar_paleta(self, visivel=None):
        if visivel is None or not isinstance(visivel, bool):
            visivel = self.faixa_cores.isHidden()
        self.faixa_cores.setVisible(visivel)
        self.barra.botao_cor.setChecked(visivel)
        if visivel:
            self.faixa_cores.marcar(self.cor)

    def mostrar_menu(self, pos):
        origem = self.sender()
        ponto = origem.mapToGlobal(pos) if isinstance(origem, QWidget) else self.mapToGlobal(pos)
        self._exibir_menu(ponto)

    def _exibir_menu(self, ponto_global):
        menu = QMenu(self)
        self._preparar_menu_translucido(menu)
        nova = menu.addAction("Nova nota")
        nova.setShortcut(QKeySequence("Ctrl+N"))
        nova.triggered.connect(lambda: self.gerenciador.criar_nota())
        duplicar = menu.addAction("Duplicar")
        duplicar.setShortcut(QKeySequence("Ctrl+D"))
        duplicar.triggered.connect(lambda: self.duplicar())
        menu.addSeparator()

        riscado = QAction("Riscado", self)
        riscado.setCheckable(True)
        riscado.setChecked(self.area_texto.currentCharFormat().fontStrikeOut())
        riscado.triggered.connect(self.alternar_riscado)
        menu.addAction(riscado)

        tarefa = menu.addAction("Nova tarefa")
        tarefa.setShortcut(QKeySequence("Ctrl+T"))
        tarefa.triggered.connect(lambda: self.adicionar_lista_tarefas())
        menu.addSeparator()

        cores = menu.addMenu("Cor")
        self._preparar_menu_translucido(cores)
        todas_cores = list(CORES_NOTA) + [
            ("Personalizada", hex_cor) for hex_cor in self.gerenciador.cores_personalizadas
        ]
        for nome, hex_cor in todas_cores:
            acao = QAction(icone_cor(hex_cor, 16, hex_cor.lower() == self.cor.lower()), nome, self)
            acao.triggered.connect(lambda _, valor=hex_cor: self.mudar_cor(valor))
            cores.addAction(acao)
        cores.addSeparator()
        cores.addAction("Escolher outra…").triggered.connect(lambda: self.escolher_cor())

        pin = QAction("Manter na frente", self)
        pin.setCheckable(True)
        pin.setChecked(self.esta_fixada())
        pin.triggered.connect(self.alternar_sempre_visivel)
        menu.addAction(pin)

        opacidade = menu.addMenu("Transparência")
        self._preparar_menu_translucido(opacidade)
        for nivel in NIVEIS_OPACIDADE:
            rotulo = f"{int(nivel * 100)}%"
            acao = QAction(rotulo, self)
            acao.setCheckable(True)
            acao.setChecked(abs(self.opacidade - nivel) < 0.02)
            acao.triggered.connect(lambda _, valor=nivel: self.definir_opacidade(valor))
            opacidade.addAction(acao)

        menu.addSeparator()
        copiar = menu.addAction("Copiar texto")
        copiar.triggered.connect(lambda: QApplication.clipboard().setText(self.area_texto.toPlainText()))
        menu.addSeparator()
        excluir = menu.addAction("Excluir esta nota")
        excluir.triggered.connect(lambda: self.pedir_exclusao())

        self._chrome_travado = True
        self.atualizar_cromo()
        menu.exec(ponto_global)
        self._chrome_travado = False
        self.atualizar_cromo()

    def mostrar_menu_formatacao(self, pos=None):
        self.alternar_paleta(True)

    def adicionar_lista_tarefas(self):
        cursor = self.area_texto.textCursor()
        texto = cursor.selectedText().replace("\u2029", " ").strip() or "Nova tarefa"
        if not cursor.atBlockStart():
            cursor.movePosition(cursor.MoveOperation.EndOfBlock)
            cursor.insertText("\n")
        cursor.insertText("☐ " + texto)
        if not texto:
            cursor.insertText("\n")
        self.area_texto.setTextCursor(cursor)
        self.emitir_alteracao()

    def alternar_tarefa(self, cursor=None):
        cursor = self.area_texto.textCursor() if cursor is None else cursor

        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)
        linha = cursor.selectedText()
        formato = QTextCharFormat()
        if linha.startswith("☐ "):
            nova = "☑ " + linha[2:]
            formato.setFontStrikeOut(True)
        elif linha.startswith("☑ "):
            nova = "☐ " + linha[2:]
            formato.setFontStrikeOut(False)
        elif linha.startswith("[ ] "):
            nova = "[x] " + linha[4:]
            formato.setFontStrikeOut(True)
        elif linha.startswith("[x] ") or linha.startswith("[X] "):
            nova = "[ ] " + linha[4:]
            formato.setFontStrikeOut(False)
        elif linha.startswith("☐"):
            nova = "☑" + linha[1:]
            formato.setFontStrikeOut(True)
        elif linha.startswith("☑"):
            nova = "☐" + linha[1:]
            formato.setFontStrikeOut(False)
        else:
            nova = "☑ " + linha
            formato.setFontStrikeOut(True)
        cursor.insertText(nova, formato)
        self.area_texto.setTextCursor(cursor)
        self.emitir_alteracao()

    def _aplicar_formato(self, ajustar):
        formato = self.area_texto.currentCharFormat()
        ajustar(formato)
        self.area_texto.mergeCurrentCharFormat(formato)
        self.emitir_alteracao()

    def alternar_negrito(self, ativado):
        self._aplicar_formato(
            lambda f: f.setFontWeight(QFont.Weight.Bold if ativado else QFont.Weight.Normal)
        )

    def alternar_italico(self, ativado):
        self._aplicar_formato(lambda f: f.setFontItalic(ativado))

    def alternar_sublinhado(self, ativado):
        self._aplicar_formato(lambda f: f.setFontUnderline(ativado))

    def alternar_riscado(self, ativado):
        self._aplicar_formato(lambda f: f.setFontStrikeOut(ativado))

    def atualizar_botoes_formato(self, formato):
        self.ferramentas.botao_negrito.setChecked(formato.fontWeight() >= QFont.Weight.Bold)
        self.ferramentas.botao_italico.setChecked(formato.fontItalic())
        self.ferramentas.botao_sublinhado.setChecked(formato.fontUnderline())

    def _preparar_menu_translucido(self, menu):
        menu.setWindowFlags(
            menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def escolher_cor(self):
        cor = QColorDialog.getColor(QColor(self.cor), None, "Escolher cor da nota")
        if cor.isValid():
            self.gerenciador.adicionar_cor_personalizada(cor.name())
            self.mudar_cor(cor.name())

    def mudar_cor(self, cor):
        if not cor_valida(cor):
            return
        self.cor = cor
        self.aplicar_estilo()
        self.emitir_alteracao()

    def proxima_cor(self):
        atual = self.cor.lower()
        hexes = [c.lower() for c in HEX_CORES]
        try:
            indice = hexes.index(atual)
        except ValueError:
            indice = -1
        self.mudar_cor(HEX_CORES[(indice + 1) % len(HEX_CORES)])

    def ciclo_opacidade(self):
        try:
            indice = min(
                range(len(NIVEIS_OPACIDADE)),
                key=lambda i: abs(NIVEIS_OPACIDADE[i] - self.opacidade),
            )
        except ValueError:
            indice = 0
        self.definir_opacidade(NIVEIS_OPACIDADE[(indice + 1) % len(NIVEIS_OPACIDADE)])

    def definir_opacidade(self, valor):
        self.opacidade = max(OPACIDADE_MINIMA, min(1.0, float(valor)))
        self.setWindowOpacity(self.opacidade)
        self.emitir_alteracao()

    def alternar_sempre_visivel(self, ativado=None):
        if ativado is None or not isinstance(ativado, bool):
            ativado = not self.esta_fixada()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, ativado)
        self.show()
        self.emitir_alteracao()

    def duplicar(self):
        dados = self.dados_atualizados()
        dados["x"] = dados["x"] + 28
        dados["y"] = dados["y"] + 28
        self.gerenciador.criar_nota(dados)

    def pedir_exclusao(self):
        if self.area_texto.toPlainText().strip():
            resposta = QMessageBox.question(
                self,
                "Excluir nota",
                "Excluir esta nota? O texto não poderá ser recuperado.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if resposta != QMessageBox.StandardButton.Yes:
                return
        self.gerenciador.remover_nota(self)

    def dados_atualizados(self):
        geometria = self.geometry()
        return {
            "texto": self.area_texto.toPlainText(),
            "html": self.area_texto.toHtml(),
            "x": geometria.x(),
            "y": geometria.y(),
            "largura": max(LARGURA_MINIMA, geometria.width() - MARGEM_SOMBRA * 2),
            "altura": max(ALTURA_MINIMA, geometria.height() - MARGEM_SOMBRA * 2),
            "cor": self.cor,
            "sempre_visivel": self.esta_fixada(),
            "opacidade": self.opacidade,
        }
