"""Despachador del canal de alerta. Dueno: Freddy (B2).

Punto de entrada único para `POST /alerta` (Cristian) y para el monitor: la
regla de `nivel_atencion` y el armado del mensaje se aplican una sola vez
aquí, y de ahí para abajo se elige el canal con `LUMEN_CANAL_ALERTA`
("telegram" o "whatsapp"). Cambiar de canal por defecto es cambiar una
variable de entorno, no el código que llama.

`api/lumen/telegram/` y `api/lumen/whatsapp/` siguen siendo paquetes
completos y usables por separado — este módulo solo los conecta.
"""

from __future__ import annotations

from . import telegram
from .config import get_settings
from .contracts import Caso, NivelAtencion
from .whatsapp.cliente import seleccionar_cliente
from .whatsapp.copy import armar_mensaje


async def enviar_alerta(caso: Caso, destinatario: str) -> tuple[str, str | None]:
    """Intenta el envío real por el canal activo. Devuelve `(estado, detalle)`.

    `estado` es 'enviado', 'omitido' o 'error' — nunca fabricado.
    """
    if caso.nivel_atencion == NivelAtencion.BAJO:
        return "omitido", "Nivel de atención bajo: no amerita alertar."

    ajustes = get_settings()
    mensaje = armar_mensaje(caso)

    if ajustes.lumen_canal_alerta == "whatsapp":
        return await seleccionar_cliente(ajustes).enviar(destinatario, mensaje)
    return await telegram.enviar(destinatario, mensaje)
