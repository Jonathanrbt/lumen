"""Proveedor Evolution API. Esqueleto — segundo proveedor, sin probar todavia.

Twilio va primero esta noche porque el equipo ya tiene cuenta y sandbox
verificado. Este cliente queda listo para activarse con
`LUMEN_WHATSAPP_PROVIDER=evolution` en cuanto se levante una instancia real y
se confirme el formato exacto de respuesta (varia entre versiones de
Evolution API). Hasta entonces, `configurado` es `False` sin las tres
variables y el endpoint asumido (`POST {url}/message/sendText/{instancia}`)
es el mas comun mirando la documentacion publica de Evolution API, no algo
verificado contra un servidor real.
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
