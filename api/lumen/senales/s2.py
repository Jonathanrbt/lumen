"""S2 — mismo representante en otra empresa que también contrata con la entidad."""

from __future__ import annotations

from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_RUES, fuente

NOMBRE = "Representante legal compartido"


def nits_relacionados(rues: Any) -> list[tuple[str, str]]:
    if not extraer.es_encontrado(rues) or not isinstance(rues, dict):
        return []
    pares: list[tuple[str, str]] = []
    for parte in extraer.lista(rues, "related_parties"):
        nit = extraer.nit_limpio(parte.get("document_number") or parte.get("nit"))
        nombre = extraer.texto(parte.get("name")) or ""
        rol = (extraer.texto(parte.get("role")) or "").lower()
        if nit and "representante" in rol:
            pares.append((nit, nombre))
    return pares


def evaluar(
    rues: Any,
    nit_proveedor: str,
    contratos_hermana: list[dict[str, Any]],
    consultado_en,
) -> Senal | None:
    if not contratos_hermana:
        return None
    relacionados = nits_relacionados(rues)
    if not relacionados:
        return None
    return Senal(
        codigo=CodigoSenal.S2,
        nombre=NOMBRE,
        nivel=NivelAtencion.MEDIO,
        regla_legible=copy.s2(),
        datos_usados={
            "nit_proveedor": nit_proveedor,
            "nits_relacionados": [n for n, _ in relacionados],
            "contratos_de_la_hermana": len(contratos_hermana),
        },
        fuente=fuente("rues_entity_by_nit", URL_RUES, consultado_en),
    )
