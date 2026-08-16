"""Verificacion manual: manda un mensaje real y dice si llego.

Es el equivalente de `/health/croma` pero para WhatsApp — no vive como
endpoint del contrato porque no hace falta, es una herramienta de una sola
persona (Freddy) para confirmar que el proveedor activo funciona antes de
grabar. No manda nada si `LUMEN_USAR_DUMP_LOCAL` u otra bandera lo evita:
siempre es un envio real, nunca simulado.

Uso, desde `api/`:

    python -m lumen.whatsapp.verificar +573001112233
    python -m lumen.whatsapp.verificar +573001112233 "mensaje de prueba"

Lee el proveedor y las credenciales de `.env` (via `get_settings()`), igual
que el resto de la app.
"""

from __future__ import annotations

import asyncio
import sys

from ..config import get_settings
from .cliente import seleccionar_cliente


async def _verificar(destinatario: str, mensaje: str) -> None:
    ajustes = get_settings()
    cliente = seleccionar_cliente(ajustes)
    print(f"Proveedor activo: {ajustes.lumen_whatsapp_provider}")
    print(f"Enviando a {destinatario}: {mensaje!r}")

    estado, detalle = await cliente.enviar(destinatario, mensaje)

    print(f"estado={estado}")
    if detalle:
        print(f"detalle={detalle}")

    if estado != "enviado":
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python -m lumen.whatsapp.verificar <telefono E.164> [mensaje]")
        sys.exit(2)

    destinatario = sys.argv[1]
    mensaje = sys.argv[2] if len(sys.argv) > 2 else (
        "Prueba de Lumen: si ves esto, el canal de WhatsApp funciona."
    )
    asyncio.run(_verificar(destinatario, mensaje))


if __name__ == "__main__":
    main()
