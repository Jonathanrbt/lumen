"""Canal de Telegram. Dueno: Freddy (B2), desde las ~02:00.

Se vuelve el canal de la demo porque no tiene ninguno de los dolores de
Twilio en 2026: sin trial, sin ContentSid, sin cuenta que pida tarjeta. Crear
el bot es `/newbot` a `@BotFather` y toma un minuto. El "join" equivalente es
que el destinatario le mande cualquier mensaje al bot una vez, para que
`getUpdates` revele su `chat_id` (ver docs/handoff/FREDDY-B2.md).

Misma interfaz minima que `api/lumen/whatsapp/`: `enviar(destinatario,
mensaje) -> (estado, detalle)`, `estado` siempre 'enviado' o 'error', nunca
un exito fabricado.
"""

from __future__ import annotations

from .cliente import enviar

__all__ = ["enviar"]
