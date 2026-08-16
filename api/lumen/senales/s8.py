"""S8 — contratación directa recurrente del mismo proveedor con la misma entidad."""

from __future__ import annotations

from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_SECOP, fuente
from .pesos import porcentaje_entero

NOMBRE = "Contratación directa recurrente"
MINIMO_DIRECTOS = 2


def _es_directa(modalidad: str | None) -> bool:
    if not modalidad:
        return False
    t = modalidad.lower()
    return "directa" in t or "directo" in t


def evaluar(contratos: list[dict[str, Any]], consultado_en) -> Senal | None:
    directos = [c for c in contratos if _es_directa(extraer.texto(c.get("modality")))]
    if len(directos) < MINIMO_DIRECTOS:
        return None
    valor_dir = sum(extraer.numero(c.get("value")) or 0 for c in directos)
    valor_tot = sum(extraer.numero(c.get("value")) or 0 for c in contratos)
    pct = porcentaje_entero(valor_dir, valor_tot) or 0
    return Senal(
        codigo=CodigoSenal.S8,
        nombre=NOMBRE,
        nivel=NivelAtencion.MEDIO,
        regla_legible=copy.s8(pct, 1),
        datos_usados={
            "contratos_directos": len(directos),
            "contratos_totales": len(contratos),
            "porcentaje_valor_directo": pct,
            "minimo_directos": MINIMO_DIRECTOS,
        },
        fuente=fuente("secop_contracts_by_provider", URL_SECOP, consultado_en),
    )
