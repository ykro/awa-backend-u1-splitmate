"""Normalización y orden de nombres de personas."""

import unicodedata

_HIDDEN = {"Cc", "Cf"}

NameKey = tuple[tuple[int, ...], str]


def clean_name(value: str) -> str:
    """Forma NFC, espacios simples y formato título.

    Así "sofi" + acento combinado (NFD) y "sofía" (NFC) quedan iguales: "Sofía".
    """
    text = unicodedata.normalize("NFC", value)
    return " ".join(text.split()).title()


def has_hidden_chars(value: str) -> bool:
    """True si hay caracteres de control (Cc) o de formato invisibles (Cf).

    Ejemplos: el byte nulo o el espacio de ancho cero, que harían que
    "Ana" y "Ana" + espacio invisible parecieran personas distintas.
    """
    return any(unicodedata.category(c) in _HIDDEN for c in value)


def alphabetical_key(name: str) -> NameKey:
    """Orden alfabético en español: sin acentos ni mayúsculas y la ñ después de la n.

    Álvaro va antes que Zoe y Nora antes que Ñusta. En empate decide el original.
    """
    codes = []
    for char in unicodedata.normalize("NFC", name).casefold():
        base = unicodedata.normalize("NFD", char)[0]
        codes.append(2 * ord(base) + (char == "ñ"))
    return tuple(codes), name
