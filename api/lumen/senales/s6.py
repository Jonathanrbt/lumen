"""S6 — fraccionamiento: contratos parecidos, fechas cercanas, bajo umbral.

Umbral de cuantía menor usado hoy: 130 millones COP (datos_usados lo declara).
Ventana: 14 días. Mínimo 2 contratos.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ..contracts import CodigoSenal, NivelAtencion, Senal
from . import copy, extraer
from .fuentes import URL_SECOP, fuente
from .pesos import a_fecha

NOMBRE = "Fraccionamiento"
UMBRAL_CUANTIA_MENOR = 130_000_000.0
VENTANA_DIAS = 14
PREFIJO_OBJETO = 40


def _clave_objeto(texto: str | None) -> str:
    if not texto:
        return ""
    return " ".join(texto.lower().split())[:PREFIJO_OBJETO]


def evaluar(contratos: list[dict[str, Any]], consultado_en) -> Senal | None:
    bajos: list[dict[str, Any]] = []
    for c in contratos:
        valor = extraer.numero(c.get("value") or c.get("base_price"))
        if valor is None or valor <= 0 or valor >= UMBRAL_CUANTIA_MENOR:
            continue
        if a_fecha(c.get("sign_date") or c.get("published_date") or c.get("start_date")) is None:
            continue
        bajos.append(c)
    grupos: dict[str, list[dict[str, Any]]] = {}
    for c in bajos:
        clave = _clave_objeto(extraer.texto(c.get("object") or c.get("name")))
        if len(clave) < 12:
            continue
        grupos.setdefault(clave, []).append(c)

    ganador: list[dict[str, Any]] = []
    for miembros in grupos.values():
        miembros.sort(
            key=lambda x: a_fecha(x.get("sign_date") or x.get("published_date") or x.get("start_date"))
            or date.min
        )
        for i, a in enumerate(miembros):
            fa = a_fecha(a.get("sign_date") or a.get("published_date") or a.get("start_date"))
            if fa is None:
                continue
            cluster = [a]
            for b in miembros[i + 1 :]:
                fb = a_fecha(b.get("sign_date") or b.get("published_date") or b.get("start_date"))
                if fb is None:
                    continue
                if abs((fb - fa).days) <= VENTANA_DIAS:
                    cluster.append(b)
            if len(cluster) > len(ganador):
                ganador = cluster

    if len(ganador) < 2:
        return None
    return Senal(
        codigo=CodigoSenal.S6,
        nombre=NOMBRE,
        nivel=NivelAtencion.MEDIO,
        regla_legible=copy.s6(len(ganador)),
        datos_usados={
            "contratos_en_grupo": len(ganador),
            "umbral_cuantia_menor": UMBRAL_CUANTIA_MENOR,
            "ventana_dias": VENTANA_DIAS,
        },
        fuente=fuente("secop_contracts_by_provider", URL_SECOP, consultado_en),
    )
