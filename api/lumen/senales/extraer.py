"""Lectura defensiva de respuestas Croma. found:false es dato, no error."""

from __future__ import annotations

from typing import Any


def es_encontrado(datos: Any) -> bool:
    if datos is None:
        return False
    if isinstance(datos, dict) and datos.get("found") is False:
        return False
    return True


def lista(datos: Any, *claves: str) -> list[dict[str, Any]]:
    if not isinstance(datos, dict):
        if isinstance(datos, list):
            return [x for x in datos if isinstance(x, dict)]
        return []
    for clave in claves:
        valor = datos.get(clave)
        if isinstance(valor, list):
            return [x for x in valor if isinstance(x, dict)]
    return []


def numero(valor: Any) -> float | None:
    if valor is None or valor is False:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).replace(",", "").strip()
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def texto(valor: Any) -> str | None:
    if valor is None:
        return None
    t = str(valor).strip()
    return t or None


def nit_limpio(valor: Any) -> str | None:
    crudo = texto(valor)
    if not crudo:
        return None
    solo = "".join(c for c in crudo if c.isdigit())
    return solo or None
