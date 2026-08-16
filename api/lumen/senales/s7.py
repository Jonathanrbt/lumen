"""S7 — concentración de valor de este proveedor en la entidad.

Usa la página 1 de procesos de la entidad (tope de Croma: 500) como denominador.
"""

from __future__ import annotations

from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_SECOP, fuente
from .pesos import porcentaje_entero

NOMBRE = "Concentración del valor"
UMBRAL_PORCENTAJE = 40


def evaluar(
    contratos_proveedor_entidad: list[dict[str, Any]],
    procesos_entidad: list[dict[str, Any]],
    consultado_en,
) -> Senal | None:
    valor_proveedor = sum(extraer.numero(c.get("value")) or 0 for c in contratos_proveedor_entidad)
    valor_entidad = sum(extraer.numero(p.get("base_price")) or 0 for p in procesos_entidad)
    pct = porcentaje_entero(valor_proveedor, valor_entidad)
    if pct is None or pct < UMBRAL_PORCENTAJE:
        return None
    return Senal(
        codigo=CodigoSenal.S7,
        nombre=NOMBRE,
        nivel=NivelAtencion.MEDIO,
        regla_legible=copy.s7(pct, 1),
        datos_usados={
            "valor_proveedor": valor_proveedor,
            "valor_procesos_entidad_pagina": valor_entidad,
            "porcentaje": pct,
            "umbral_porcentaje": UMBRAL_PORCENTAJE,
            "procesos_evaluados": len(procesos_entidad),
        },
        fuente=fuente("secop_processes_by_entity", URL_SECOP, consultado_en),
    )
