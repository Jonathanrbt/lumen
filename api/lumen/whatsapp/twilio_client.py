"""Proveedor Twilio (sandbox de WhatsApp). Primer proveedor, prioridad esta noche.

El SDK de Twilio es sincrono; FastAPI es async. `messages.create` bloquea, asi
que va detras de `asyncio.to_thread` para no congelar el event loop mientras
se manda una alerta.
"""

from __future__ import annotations

import asyncio
import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from ..config import Settings

log = logging.getLogger(__name__)


class TwilioWhatsAppClient:
    def __init__(self, ajustes: Settings) -> None:
        self._account_sid = ajustes.twilio_account_sid
        self._auth_token = ajustes.twilio_auth_token
        self._from = ajustes.twilio_whatsapp_from

    @property
    def configurado(self) -> bool:
        return bool(self._account_sid and self._auth_token and self._from)

    async def enviar(self, destinatario: str, mensaje: str) -> tuple[str, str | None]:
        if not self.configurado:
            return "error", "Twilio no está configurado (faltan TWILIO_* en el entorno)."

        try:
            await asyncio.to_thread(self._enviar_sync, destinatario, mensaje)
        except TwilioRestException as err:
            log.error("Twilio rechazó el envío a %s: %s", destinatario, err)
            return "error", f"Twilio rechazó el envío: {err.msg}"
        except Exception as err:  # noqa: BLE001 - preferimos el detalle a un 500 ciego
            log.error("Fallo inesperado enviando WhatsApp (Twilio) a %s: %s", destinatario, err)
            return "error", f"{type(err).__name__}: {err}"

        return "enviado", "Mensaje entregado al suscriptor (Twilio)."

    def _enviar_sync(self, destinatario: str, mensaje: str) -> None:
        cliente = Client(self._account_sid, self._auth_token)
        cliente.messages.create(
            from_=f"whatsapp:{self._from}",
            to=f"whatsapp:{destinatario}",
            body=mensaje,
        )
