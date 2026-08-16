"""Punto de entrada unico: `enviar_alerta`. Misma firma que el fallback de
Cristian (`api/lumen/plataforma/whatsapp.py`) a proposito, para que el swap en
`api/lumen/routers/plataforma.py` sea una sola linea de import.
"""

from __future__ import annotations

from ..config import Settings, get_settings
from ..contracts import Caso, NivelAtencion
from .base import WhatsAppClient
from .copy import armar_mensaje
from .evolution_client import EvolutionWhatsAppClient
from .twilio_client import TwilioWhatsAppClient


def _cliente(ajustes: Settings) -> WhatsAppClient:
    proveedor = ajustes.lumen_whatsapp_provider.strip().lower()
    if proveedor == "evolution":
        return EvolutionWhatsAppClient(ajustes)
    return TwilioWhatsAppClient(ajustes)


async def enviar_alerta(caso: Caso, destinatario: str) -> tuple[str, str | None]:
    """Intenta el envio real. Devuelve `(estado, detalle)`.

    `estado` es 'enviado', 'omitido' o 'error' — nunca fabricado. Un caso de
    nivel bajo ni siquiera llega al proveedor: no amerita alertar.
    """
    if caso.nivel_atencion == NivelAtencion.BAJO:
        return "omitido", "Nivel de atención bajo: no amerita alertar."

    ajustes = get_settings()
    mensaje = armar_mensaje(caso)
    return await _cliente(ajustes).enviar(destinatario, mensaje)
