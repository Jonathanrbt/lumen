"""Interfaz minima que cualquier proveedor de WhatsApp tiene que cumplir.

Un solo metodo a proposito: recibe el mensaje ya armado (con el copy de
`docs/COPY-SENALES.md`) y el destinatario, y devuelve `(estado, detalle)`.
El proveedor no decide el texto ni el nivel de atencion — eso vive en
`cliente.py`, para que Twilio y Evolution API sean intercambiables sin que
ninguno de los dos sepa nada del dominio de Lumen.
"""

from __future__ import annotations

from typing import Protocol


class WhatsAppClient(Protocol):
    """`estado` es siempre 'enviado' o 'error'. Nunca se fabrica un exito."""

    async def enviar(self, destinatario: str, mensaje: str) -> tuple[str, str | None]: ...
