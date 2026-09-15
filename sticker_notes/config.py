import re

CORES_NOTA = [
    ("Amarelo", "#E8DFC0"),
    ("Areia", "#E5D9BE"),
    ("Pêssego", "#E8D2C0"),
    ("Terracota", "#E3C2B8"),
    ("Rosa", "#E3C2D2"),
    ("Lilás", "#D4C7E0"),
    ("Azul", "#C2D3E3"),
    ("Menta", "#C3DAC8"),
    ("Salva", "#C8D6C2"),
    ("Cinza", "#DAD7CE"),
]

HEX_CORES = [cor for _, cor in CORES_NOTA]

LARGURA_MINIMA = 220
ALTURA_MINIMA = 160
LARGURA_PADRAO = 280
ALTURA_PADRAO = 250
MARGEM_SOMBRA = 14

FONTE_UI = "Segoe UI"
TAMANHO_FONTE = 13
OPACIDADE_PADRAO = 1.0
OPACIDADE_MINIMA = 0.55

_PADRAO_COR_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def cor_valida(valor):
    #Só aceita strings no formato #RRGGBB.
    return isinstance(valor, str) and bool(_PADRAO_COR_HEX.fullmatch(valor))


def numero_seguro(valor, padrao):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao
