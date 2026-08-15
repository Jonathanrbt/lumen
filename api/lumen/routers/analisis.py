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

router = APIRouter(tags=["motor · B1 Jonatin"])


@router.post("/analizar", response_model=Caso)
async def analizar(peticion: AnalizarRequest) -> Caso:
    """Corre las 8 señales sobre una entidad, un proveedor o un contrato.

    Pasos 3 a 7 del flujo: enriquecer con Croma, evaluar las reglas, calcular el
    nivel de atención y armar el Caso. Cada señal disparada guarda su regla
    legible, el dato que la disparó y la fuente oficial con fecha de consulta.
    """
    raise HTTPException(status_code=501, detail="Pendiente: B1 (Jonatin). Motor de las 8 señales.")


@router.get("/red/{nit}", response_model=Grafo)
async def red(nit: str) -> Grafo:
    """Devuelve el subgrafo de actores alrededor de un NIT.

    Curado y pequeño: entre 5 y 12 nodos. Un hairball es peor que no mostrar grafo.
    """
    raise HTTPException(status_code=501, detail="Pendiente: B1 (Jonatin). Grafo de actores.")
