"""S3 — sanción vigente y contratos posteriores."""

from __future__ import annotations

from datetime import date
from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_CONTRALORIA, URL_PROCURADURIA, URL_SECOP, fuente
from .pesos import a_fecha

NOMBRE = "Sancionado que sigue contratando"


def _sancion_vigente(item: dict[str, Any], hoy: date) -> bool:
    firmeza = a_fecha(item.get("final_date"))
    publicada = a_fecha(item.get("published_date"))
    if firmeza and firmeza >= hoy:
        return True
    if firmeza is None and publicada and publicada <= hoy:
        return True
    return False


def evaluar(
    sanciones: Any,
    procuraduria: Any,
    contraloria: Any,
    contratos: list[dict[str, Any]],
    consultado_en,
    hoy: date | None = None,
) -> Senal | None:
    hoy = hoy or date.today()
    filas = extraer.lista(sanciones, "sanctions")
    vigentes = [s for s in filas if _sancion_vigente(s, hoy)]
    tiene_disciplina = extraer.es_encontrado(procuraduria) and bool(
        extraer.lista(procuraduria, "records", "data") or (procuraduria if isinstance(procuraduria, dict) and procuraduria.get("found") else [])
    )
    tiene_fiscal = extraer.es_encontrado(contraloria) and bool(
        extraer.lista(contraloria, "records", "data")
    )
    if not vigentes and not tiene_disciplina and not tiene_fiscal:
        return None

    fechas_sancion = [a_fecha(s.get("published_date") or s.get("final_date")) for s in vigentes]
    fechas_sancion = [f for f in fechas_sancion if f]
    mas_vieja = min(fechas_sancion) if fechas_sancion else None
    posteriores = []
    for c in contratos:
        firma = a_fecha(c.get("sign_date"))
        if firma and mas_vieja and firma > mas_vieja:
            posteriores.append(c)
        elif mas_vieja is None and firma:
            posteriores.append(c)
    if vigentes and not posteriores:
        return None
    if not vigentes:
        return None

    url = URL_SECOP
    herramienta = "secop_sanctions_by_provider"
    if tiene_disciplina:
        url = URL_PROCURADURIA
        herramienta = "procuraduria_disciplinary_records"
    elif tiene_fiscal:
        url = URL_CONTRALORIA
        herramienta = "contraloria_fiscal_records"

    return Senal(
        codigo=CodigoSenal.S3,
        nombre=NOMBRE,
        nivel=NivelAtencion.ALTO,
        regla_legible=copy.s3(),
        datos_usados={
            "sanciones_vigentes": len(vigentes),
            "contratos_posteriores": len(posteriores),
        },
        fuente=fuente(herramienta, url, consultado_en),
    )
