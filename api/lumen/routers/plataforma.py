"""Endpoints de plataforma. Dueno: Cristian (B3).

Nadie mas edita este archivo. Si necesitas algo de aqui, pidelo por el chat.

Aqui vive el ensamblado: persistencia, monitor y salida al mundo. Es lo que
convierte el motor en un producto que le avisa a alguien.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from ..contracts import AlertaRequest, AlertaResponse, Caso

router = APIRouter(tags=["plataforma · B3 Cristian"])


@router.get("/caso/{caso_id}", response_model=Caso)
async def obtener_caso(caso_id: str) -> Caso:
    """Devuelve un caso ya calculado.

    Es el enlace que abre el ciudadano desde el WhatsApp, así que tiene que
    responder al instante: lee de Supabase, o del dump JSON si
    `LUMEN_USAR_DUMP_LOCAL` está activo.
    """
    raise HTTPException(status_code=501, detail="Pendiente: B3 (Cristian). Lectura de casos.")


@router.get("/monitor/nuevos", response_model=list[Caso])
async def monitor_nuevos(
    desde: date | None = Query(default=None, description="Fecha mínima de publicación"),
) -> list[Caso]:
    """Los contratos nuevos que el monitor encontró y convirtió en casos.

    El monitor pide a Croma los contratos con causal de urgencia en los
    departamentos afectados desde el 11 de agosto, descarta lo que ya está en base
    y solo procesa lo nuevo.

    Ojo con la zona horaria: Render corre en UTC y nosotros razonamos en Bogotá
    (UTC-5). Las fechas van explícitas.
    """
    raise HTTPException(status_code=501, detail="Pendiente: B3 (Cristian). Monitor.")


@router.post("/alerta", response_model=AlertaResponse)
async def alerta(peticion: AlertaRequest) -> AlertaResponse:
    """Envía el aviso al suscriptor.

    Máximo 5 líneas, lenguaje ciudadano, con enlace a la ficha del caso.

    Twilio está sin resolver y es el hard-cut #3: si no sale, el video muestra la
    alerta dentro de la plataforma. **No se mockea un WhatsApp falso.**
    """
    raise HTTPException(status_code=501, detail="Pendiente: B3 (Cristian). Envío de alertas.")
