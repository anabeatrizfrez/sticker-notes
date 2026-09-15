from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap


def _pix(tamanho):
    dpr = 2
    pix = QPixmap(int(tamanho * dpr), int(tamanho * dpr))
    pix.setDevicePixelRatio(dpr)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    return pix, p


def _caneta(cor, espessura=1.7):
    pen = QPen(QColor(cor))
    pen.setWidthF(espessura)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _letra(nome, cor, tamanho):
    pix, p = _pix(tamanho)
    fonte = QFont("Segoe UI")
    fonte.setPixelSize(int(tamanho * 0.72))
    if nome == "negrito":
        fonte.setWeight(QFont.Weight.Black)
        texto = "B"
    elif nome == "italico":
        fonte.setItalic(True)
        fonte.setFamily("Georgia")
        texto = "I"
    elif nome == "sublinhado":
        fonte.setUnderline(True)
        texto = "U"
    else:
        fonte.setStrikeOut(True)
        texto = "S"
    p.setFont(fonte)
    p.setPen(QColor(cor))
    p.drawText(QRectF(0, 0, tamanho, tamanho), Qt.AlignmentFlag.AlignCenter, texto)
    p.end()
    return QIcon(pix)


def icone(nome, cor="#292524", tamanho=18):
    if nome in {"negrito", "italico", "sublinhado", "riscado"}:
        return _letra(nome, cor, tamanho)

    pix, p = _pix(tamanho)
    p.setPen(_caneta(cor))
    p.setBrush(Qt.BrushStyle.NoBrush)
    s = float(tamanho)
    m = s * 0.24
    box = QRectF(m, m, s - 2 * m, s - 2 * m)
    cx, cy = s / 2, s / 2

    if nome == "mais":
        p.drawLine(QPointF(cx, m), QPointF(cx, s - m))
        p.drawLine(QPointF(m, cy), QPointF(s - m, cy))
    elif nome == "pontos":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(cor))
        raio = s * 0.055
        for dx in (-1, 0, 1):
            p.drawEllipse(QPointF(cx + dx * s * 0.22, cy), raio, raio)
    elif nome == "fechar":
        inset = m + 0.5
        p.drawLine(QPointF(inset, inset), QPointF(s - inset, s - inset))
        p.drawLine(QPointF(s - inset, inset), QPointF(inset, s - inset))
    elif nome == "duplicar":
        p.drawRoundedRect(QRectF(m + 3.2, m - 0.2, s - 2 * m - 2.4, s - 2 * m - 2.4), 2, 2)
        p.drawRoundedRect(QRectF(m - 0.4, m + 3.4, s - 2 * m - 2.4, s - 2 * m - 2.4), 2, 2)
    elif nome == "pin":
        path = QPainterPath()
        path.moveTo(cx, m)
        path.cubicTo(s - m, m + 0.5, s - m, cy + 1.2, cx + 0.2, s - m - 1.5)
        path.cubicTo(m, cy + 1.2, m, m + 0.5, cx, m)
        p.drawPath(path)
        p.drawLine(QPointF(cx, s - m - 1.2), QPointF(cx, s - m + 1.8))
    elif nome == "pin-on":
        path = QPainterPath()
        path.moveTo(cx, m)
        path.cubicTo(s - m, m + 0.5, s - m, cy + 1.2, cx + 0.2, s - m - 1.5)
        path.cubicTo(m, cy + 1.2, m, m + 0.5, cx, m)
        p.setBrush(QColor(cor))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(path)
        p.setPen(_caneta(cor))
        p.drawLine(QPointF(cx, s - m - 1.2), QPointF(cx, s - m + 1.8))
    elif nome == "gota":
        path = QPainterPath()
        path.moveTo(cx, m - 0.4)
        path.cubicTo(s - m + 0.4, cy, s - m + 0.2, s - m + 0.6, cx, s - m + 0.6)
        path.cubicTo(m - 0.2, s - m + 0.6, m - 0.4, cy, cx, m - 0.4)
        p.drawPath(path)
    elif nome == "tarefa":
        p.drawRoundedRect(box, 2.4, 2.4)
    elif nome == "opacidade":
        p.drawEllipse(box)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(cor))
        path = QPainterPath()
        path.moveTo(cx, box.top())
        path.arcTo(box, 90, 180)
        path.closeSubpath()
        p.drawPath(path)
    else:
        p.drawEllipse(box)

    p.end()
    return QIcon(pix)


def icone_cor(hex_cor, tamanho=18, selecionada=False):
    pix, p = _pix(tamanho)
    cor = QColor(hex_cor)
    margem = 2.4 if selecionada else 3.4
    p.setBrush(cor)
    p.setPen(QPen(QColor(0, 0, 0, 40), 1))
    p.drawEllipse(QRectF(margem, margem, tamanho - margem * 2, tamanho - margem * 2))
    if selecionada:
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 230), 1.5))
        p.drawEllipse(QRectF(5.2, 5.2, tamanho - 10.4, tamanho - 10.4))
    p.end()
    return QIcon(pix)
