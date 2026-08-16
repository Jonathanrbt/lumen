"""Cliente de la Telegram Bot API. Un solo proveedor: no hace falta la
abstraccion de "elegir proveedor" que tiene `api/lumen/whatsapp/`.

Formato de respuesta confirmado contra la documentacion oficial
(https://core.telegram.org/bots/api#making-requests): `{"ok": bool,
"result": ..., "error_code": int, "description": str}`.
"""

from __future__ import annotations

import logging

import httpx

from ..config import Settings, get_settings

log = logging.getLogger(__name__)

BASE_URL = "https://api.telegram.org"


def _configurado(ajustes: Settings) -> bool:
    return bool(ajustes.telegram_bot_token)


async def enviar(destinatario: str, mensaje: str) -> tuple[str, str | None]:
    ajustes = get_settings()
    if not _configurado(ajustes):
        return "error", "Telegram no está configurado (falta TELEGRAM_BOT_TOKEN en el entorno)."

    url = f"{BASE_URL}/bot{ajustes.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=15.0) as cliente:
            resp = await cliente.post(url, json={"chat_id": destinatario, "text": mensaje})
            cuerpo = resp.json()
    except httpx.HTTPError as err:
        log.error("Telegram no respondió al enviar a %s: %s", destinatario, err)
        return "error", f"Telegram no respondió: {err}"
    except Exception as err:  # noqa: BLE001 - preferimos el detalle a un 500 ciego
        log.error("Fallo inesperado enviando Telegram a %s: %s", destinatario, err)
        return "error", f"{type(err).__name__}: {err}"

    if not cuerpo.get("ok"):
        descripcion = cuerpo.get("description", "sin descripción")
        log.error("Telegram rechazó el envío a %s: %s", destinatario, descripcion)
        return "error", f"Telegram rechazó el envío: {descripcion}"

    return "enviado", "Mensaje entregado al suscriptor (Telegram)."
