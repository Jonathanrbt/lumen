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

# PUNTO DE ENGANCHE 22:14: WhatsApp se reasignó a Freddy (B2), ver docs/PLAN.md
# y docs/handoff/FREDDY-B2.md. Su cliente real vive en `api/lumen/whatsapp/`.
# `..plataforma.whatsapp` es el envío de respaldo escrito antes de esa
# reasignación — en cuanto el módulo de Freddy exista, este import es lo único
# que cambia: `from ..whatsapp import enviar_alerta` (o el nombre que él fije).
from ..plataforma.whatsapp import enviar_alerta

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
) -> list[Caso]:
    """Los contratos nuevos que el monitor encontró y convirtió en casos.

    El monitor pide a Croma los contratos con causal de urgencia en los
    departamentos afectados desde el 11 de agosto, descarta lo que ya está en base
    y solo procesa lo nuevo.

    Ojo con la zona horaria: Render corre en UTC y nosotros razonamos en Bogotá
    (UTC-5). Las fechas van explícitas.
    """
    try:
        return await monitor_nuevos(desde)
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
