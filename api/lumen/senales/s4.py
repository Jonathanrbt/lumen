"""S4 — valor del contrato mayor que los ingresos anuales reportados.

Umbral si no hay ingresos: 100 millones de pesos, escrito en datos_usados.
"""

from __future__ import annotations

from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_RUES, URL_SUPERSOCIEDADES, fuente

NOMBRE = "Contrato desproporcionado"
UMBRAL_SIN_INGRESOS = 100_000_000.0


def _ingresos(rues: Any, estados: Any) -> float | None:
    series: list[dict[str, Any]] = []
    if extraer.es_encontrado(rues) and isinstance(rues, dict):
        series.extend(extraer.lista(rues, "financials"))
    if extraer.es_encontrado(estados) and isinstance(estados, dict):
        series.extend(extraer.lista(estados, "statements", "financials", "data"))
    mejor: float | None = None
    for fila in series:
        ingreso = extraer.numero(fila.get("ordinary_revenue") or fila.get("revenue") or fila.get("ingresos"))
        if ingreso is None:
            continue
        if mejor is None or ingreso > mejor:
            mejor = ingreso
    return mejor


def evaluar(
    rues: Any,
    estados: Any,
    contrato: dict[str, Any],
    consultado_en,
) -> Senal | None:
    valor = extraer.numero(contrato.get("value"))
    if valor is None or valor <= 0:
        return None
    ingresos = _ingresos(rues, estados)
    if ingresos is None:
        if valor < UMBRAL_SIN_INGRESOS:
            return None
        disparo = "sin_estados_y_contrato_grande"
        ingresos_usados = 0.0
    elif ingresos <= 0:
        if valor < UMBRAL_SIN_INGRESOS:
            return None
        disparo = "ingresos_cero"
        ingresos_usados = 0.0
    elif valor > ingresos:
        disparo = "valor_mayor_que_ingresos"
        ingresos_usados = ingresos
    else:
        return None

    herramienta = "rues_entity_by_nit"
    url = URL_RUES
    if extraer.es_encontrado(estados):
        herramienta = "supersociedades_financial_statements"
        url = URL_SUPERSOCIEDADES

    return Senal(
        codigo=CodigoSenal.S4,
        nombre=NOMBRE,
        nivel=NivelAtencion.ALTO,
        regla_legible=copy.s4(),
        datos_usados={
            "valor_contrato": valor,
            "ingresos_anuales": ingresos_usados,
            "umbral_sin_ingresos": UMBRAL_SIN_INGRESOS,
            "como_disparo": disparo,
        },
        fuente=fuente(herramienta, url, consultado_en),
    )
