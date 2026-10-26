"""Aritmética monetaria exacta con Decimal para SplitMate API."""

from decimal import ROUND_HALF_UP, Decimal

from app.names import alphabetical_key  # noqa: F401 (la usarás en split_evenly)

CENT = Decimal("0.01")
ZERO = Decimal("0.00")

Shares = dict[str, Decimal]


def to_money(value: Decimal) -> Decimal:
    """Cuantiza a 2 decimales con redondeo comercial (ROUND_HALF_UP)."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def split_evenly(amount: Decimal, names: list[str]) -> Shares:
    """Reparte amount entre names sin perder centavos.

    Los centavos sobrantes van, de uno en uno, a los primeros
    nombres en orden alfabético (sin distinguir acentos).
    """
    # TALLER, paso 4 del codelab:
    # 1. Convierte amount a centavos enteros: int(to_money(amount) / CENT).
    # 2. divmod(centavos, len(names)) da la cuota base y los centavos sobrantes.
    # 3. Ordena con sorted(names, key=alphabetical_key): Álvaro antes que Zoe, ñ tras n.
    # 4. Los primeros "sobrantes" reciben un centavo más.
    # 5. Devuelve {nombre: centavos * CENT} para que cada cuota sea Decimal.
    raise NotImplementedError("Taller: implementa split_evenly en app/money.py")
