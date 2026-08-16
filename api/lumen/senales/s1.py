"""S1 — empresa constituida menos de 365 días antes de ganar el contrato."""

from __future__ import annotations

from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_RUES, fuente
from .pesos import a_fecha, meses_entre

UMBRAL_DIAS = 365
NOMBRE = "Empresa recién creada que gana"


def evaluar(
    rues: Any,
    contrato: dict[str, Any],
    consultado_en,
) -> Senal | None:
    if not extraer.es_encontrado(rues) or not isinstance(rues, dict):
        return None
    entidad = rues.get("entity") if isinstance(rues.get("entity"), dict) else rues
    registro = a_fecha(entidad.get("registration_date"))
    adjudicacion = a_fecha(contrato.get("sign_date") or contrato.get("start_date"))
    if registro is None or adjudicacion is None:
        return None
    dias = (adjudicacion - registro).days
    if dias < 0 or dias >= UMBRAL_DIAS:
        return None
    valor = extraer.numero(contrato.get("value")) or 0.0
    meses = max(meses_entre(registro, adjudicacion), 1)
    return Senal(
        codigo=CodigoSenal.S1,
        nombre=NOMBRE,
        nivel=NivelAtencion.ALTO,
        regla_legible=copy.s1(meses, valor),
        datos_usados={
            "fecha_registro": registro.isoformat(),
            "fecha_adjudicacion": adjudicacion.isoformat(),
            "dias_transcurridos": dias,
            "umbral_dias": UMBRAL_DIAS,
        },
        fuente=fuente("rues_entity_by_nit", URL_RUES, consultado_en),
    )
