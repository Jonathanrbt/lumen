"""Endpoints de plataforma. Dueno: Cristian (B3).

Nadie mas edita este archivo. Si necesitas algo de aqui, pidelo por el chat.

Aqui vive el ensamblado: persistencia, monitor y salida al mundo. Es lo que
convierte el motor en un producto que le avisa a alguien.
"""

from __future__ import annotations

from datetime import date

import httpx
from fastapi import APIRouter, HTTPException, Query

from ..contracts import AlertaRequest, AlertaResponse, Caso
from ..croma.client import CromaError, CromaSinRespuesta
from ..plataforma.casos import obtener_caso
from ..plataforma.monitor import monitor_nuevos
from ..plataforma.supabase_client import SupabaseNoConfigurado

# Canal de alerta: Freddy (B2), ver docs/PLAN.md y docs/handoff/FREDDY-B2.md.
# `..alertas` decide Telegram o WhatsApp según LUMEN_CANAL_ALERTA; misma firma
# que el respaldo original que reemplazó.
from ..alertas import enviar_alerta

router = APIRouter(tags=["plataforma · B3 Cristian"])


@router.get("/caso/{caso_id}", response_model=Caso)
async def obtener_caso_endpoint(caso_id: str) -> Caso:
    """Devuelve un caso ya calculado.

    Es el enlace que abre el ciudadano desde el WhatsApp, así que tiene que
    responder al instante: lee de Supabase, o del dump JSON si
    `LUMEN_USAR_DUMP_LOCAL` está activo.
    """
    try:
        caso = obtener_caso(caso_id)
    except SupabaseNoConfigurado as err:
        raise HTTPException(status_code=503, detail=str(err)) from err

    if caso is None:
        raise HTTPException(status_code=404, detail=f"No existe un caso con id '{caso_id}'.")
    return caso


@router.get("/monitor/nuevos", response_model=list[Caso])
async def monitor_nuevos_endpoint(
    desde: date | None = Query(default=None, description="Fecha mínima de publicación"),
    forzar: bool = Query(
        default=False,
        description="Re-analiza aunque el contrato ya esté en base (caro: ~80-100 s por entidad)",
    ),
) -> list[Caso]:
    """Los contratos que el monitor encontró en las entidades afectadas.

    El monitor pide a Croma los contratos con causal de urgencia en los
    departamentos afectados desde el 11 de agosto. Lo que ya está en base no se
    vuelve a analizar, pero **sí se devuelve**: el mismo documento se puede
    consultar varias veces sin que la respuesta se quede vacía. Con
    `?forzar=true` se re-analiza todo desde cero.

    Ojo con la zona horaria: Render corre en UTC y nosotros razonamos en Bogotá
    (UTC-5). Las fechas van explícitas.
    """
    try:
        return await monitor_nuevos(desde, forzar=forzar)
    except SupabaseNoConfigurado as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    except (CromaError, CromaSinRespuesta, httpx.HTTPError) as err:
        raise HTTPException(status_code=503, detail=f"Croma no respondió: {err}") from err


@router.post("/alerta", response_model=AlertaResponse)
async def alerta(peticion: AlertaRequest) -> AlertaResponse:
    """Envía el aviso al suscriptor.

    Máximo 5 líneas, lenguaje ciudadano, con enlace a la ficha del caso.

    Twilio está sin resolver y es el hard-cut #3: si no sale, el video muestra la
    alerta dentro de la plataforma. **No se mockea un WhatsApp falso.**
    """
    try:
        caso = obtener_caso(peticion.caso_id)
    except SupabaseNoConfigurado as err:
        raise HTTPException(status_code=503, detail=str(err)) from err

    if caso is None:
        raise HTTPException(
            status_code=404, detail=f"No existe un caso con id '{peticion.caso_id}'."
        )

    estado, detalle = await enviar_alerta(caso, peticion.destinatario)
    return AlertaResponse(estado=estado, detalle=detalle)
