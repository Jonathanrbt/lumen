"""S5 — insolvencia activa y contratos vigentes."""

from __future__ import annotations

from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_SICAAC, fuente

NOMBRE = "Insolvente contratando"


def _casos(datos: Any) -> list[dict[str, Any]]:
    if not extraer.es_encontrado(datos):
        return []
    return extraer.lista(datos, "cases", "data", "insolvency_cases")


def evaluar(sicaac: Any, contratos: list[dict[str, Any]], consultado_en) -> Senal | None:
    casos = _casos(sicaac)
    if not casos:
        return None
    if not contratos:
        return None
    return Senal(
        codigo=CodigoSenal.S5,
        nombre=NOMBRE,
        nivel=NivelAtencion.ALTO,
        regla_legible=copy.s5(),
        datos_usados={"casos_insolvencia": len(casos), "contratos_vistos": len(contratos)},
        fuente=fuente("sicaac_insolvency_cases", URL_SICAAC, consultado_en),
    )
