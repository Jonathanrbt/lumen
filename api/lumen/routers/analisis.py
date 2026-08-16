"""Endpoints del motor. Dueno: Jonatin (B1).

Nadie mas edita este archivo. Si necesitas algo de aqui, pidelo por el chat.

Estos dos endpoints son el corazon del producto y los comparten los dos modos: el
monitor los llama cuando encuentra un contrato nuevo, y el chat los llama cuando
una persona pregunta. **No hay un segundo motor.** Si alguien empieza a escribir
uno, se salio del plan.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..contracts import AnalizarRequest, Caso, Grafo
from ..croma.client import CromaError, CromaSinRespuesta
from ..senales.motor import analizar as correr_analizar
from ..senales.motor import red as correr_red

router = APIRouter(tags=["motor · B1 Jonatin"])


@router.post("/analizar", response_model=Caso)
async def analizar(peticion: AnalizarRequest) -> Caso:
    """Corre las 8 señales sobre una entidad, un proveedor o un contrato."""
    try:
        return await correr_analizar(peticion)
    except (CromaError, CromaSinRespuesta) as err:
        raise HTTPException(status_code=503, detail=f"Croma no respondió: {err}") from err


@router.get("/red/{nit}", response_model=Grafo)
async def red(nit: str) -> Grafo:
    """Devuelve el subgrafo de actores alrededor de un NIT.

    Curado y pequeño: entre 5 y 12 nodos. Un hairball es peor que no mostrar grafo.
    """
    try:
        return await correr_red(nit)
    except (CromaError, CromaSinRespuesta) as err:
        raise HTTPException(status_code=503, detail=f"Croma no respondió: {err}") from err
