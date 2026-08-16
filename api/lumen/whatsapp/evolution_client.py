"""Proveedor Evolution API. Segundo proveedor — Twilio va primero esta noche
porque el equipo ya tiene cuenta y sandbox.

El endpoint y el payload estan verificados contra la documentacion oficial
v2 (`POST {url}/message/sendText/{instancia}`, header `apikey`, body
`{"number", "text"}`): https://doc.evolution-api.com/v2/api-reference/message-controller/send-text.
Lo que sigue sin probar es un servidor real: Evolution API no es un servicio
cloud como Twilio, hace falta una instancia corriendo (self-hosted o de un
proveedor) con un numero de WhatsApp ya vinculado por QR — eso es trabajo
operativo, no de codigo, y esta detallado en el handoff.
"""

from __future__ import annotations

import logging

import httpx

from ..config import Settings

log = logging.getLogger(__name__)


class EvolutionWhatsAppClient:
    def __init__(self, ajustes: Settings) -> None:
        self._url = ajustes.evolution_api_url.rstrip("/")
        self._api_key = ajustes.evolution_api_key
        self._instance = ajustes.evolution_instance

    @property
    def configurado(self) -> bool:
        return bool(self._url and self._api_key and self._instance)

    async def enviar(self, destinatario: str, mensaje: str) -> tuple[str, str | None]:
        if not self.configurado:
            return "error", "Evolution API no está configurada (faltan EVOLUTION_* en el entorno)."

        numero = destinatario.lstrip("+")
        try:
            async with httpx.AsyncClient(timeout=15.0) as cliente:
                resp = await cliente.post(
                    f"{self._url}/message/sendText/{self._instance}",
                    headers={"apikey": self._api_key},
                    json={"number": numero, "text": mensaje},
                )
                resp.raise_for_status()
        except httpx.HTTPError as err:
            log.error("Evolution API rechazó el envío a %s: %s", destinatario, err)
            return "error", f"Evolution API rechazó el envío: {err}"
        except Exception as err:  # noqa: BLE001 - preferimos el detalle a un 500 ciego
            log.error("Fallo inesperado enviando WhatsApp (Evolution) a %s: %s", destinatario, err)
            return "error", f"{type(err).__name__}: {err}"

        return "enviado", "Mensaje entregado al suscriptor (Evolution API)."
