"""Cifras para el veedor: pesos redondeados y meses, nunca notación técnica."""

from __future__ import annotations

from datetime import date, datetime


def a_fecha(valor: object) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor).strip()[:10]
    if len(texto) < 10:
        return None
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


def meses_entre(inicio: date, fin: date) -> int:
    if fin < inicio:
        return 0
    meses = (fin.year - inicio.year) * 12 + (fin.month - inicio.month)
    if fin.day < inicio.day:
        meses -= 1
    return max(meses, 0)


def pesos_redondeados(valor: float) -> str:
    """$X millones / $X mil millones. Sin decimales técnicos."""
    if valor >= 1_000_000_000:
        miles = round(valor / 1_000_000_000)
        return f"${miles:,} mil millones".replace(",", ".")
    if valor >= 1_000_000:
        millones = round(valor / 1_000_000)
        return f"${millones:,} millones".replace(",", ".")
    miles = max(round(valor / 1_000), 1)
    return f"${miles:,} mil".replace(",", ".")


def porcentaje_entero(parte: float, total: float) -> int | None:
    if total <= 0:
        return None
    return max(round(100 * parte / total), 0)
