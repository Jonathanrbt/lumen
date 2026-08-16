"""S10 — deudor moroso del Estado (BDME) que sigue contratando."""

from __future__ import annotations

from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_CONTADURIA, fuente

NOMBRE = "Deudor moroso del Estado contratando"


def evaluar(bdme: Any, contratos: list[dict[str, Any]], consultado_en) -> Senal | None:
    if not extraer.es_encontrado(bdme) or not isinstance(bdme, dict):
        return None
    filas = extraer.lista(bdme, "debtors", "records", "data")
    banderas = [
        bdme.get("delinquent"),
        bdme.get("is_delinquent"),
        bdme.get("moroso"),
        bdme.get("ley_901"),
        bdme.get("state_debtor"),
    ]
    esta = any(b is True for b in banderas) or bool(filas)
    if not esta:
        return None
    if not contratos:
        return None
    return Senal(
        codigo=CodigoSenal.S10,
        nombre=NOMBRE,
        nivel=NivelAtencion.ALTO,
        regla_legible=copy.s10(),
        datos_usados={
            "registros_bdme": len(filas) or int(esta),
            "contratos_vistos": len(contratos),
        },
        fuente=fuente("contaduria_state_delinquent_debtors", URL_CONTADURIA, consultado_en),
    )
