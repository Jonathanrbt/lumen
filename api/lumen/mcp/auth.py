"""Guardia del servidor MCP. Dueno: Cristian (B3).

Envuelve la sub-app ASGI del MCP, **no** es middleware global de FastAPI. Dos
razones (§design.md, decision 3):

1. Un middleware global correria en cada `/health` y en los nueve endpoints
   para luego mirar el path y no hacer nada.
2. Envolver la sub-app hace imposible que un refactor de rutas deje `/mcp`
   sin proteccion por accidente. El guardia esta pegado a lo que protege.

El orden de comprobacion importa y no es arbitrario:

    1. interruptor apagado      -> 503   (apagado es apagado, incluso con token)
    2. sin token configurado    -> 503   (NUNCA abierto por defecto)
    3. bearer ausente o distinto-> 401

El punto 2 es el que evita el fallo mas facil de provocar: olvidar la variable
en Render y dejar la cuota de Croma de los cuatro accesible a cualquiera que
adivine la URL.
"""

from __future__ import annotations

import hmac
import json
import logging

from ..config import get_settings

log = logging.getLogger(__name__)

MENSAJE_APAGADO = (
    "El servidor MCP está desactivado (LUMEN_MCP_HABILITADO=false). "
    "Se apaga desde el dashboard sin redesplegar; el resto de la API sigue funcionando."
)
MENSAJE_SIN_TOKEN = (
    "El servidor MCP no tiene credencial configurada (falta LUMEN_MCP_TOKEN), "
    "así que no acepta conexiones. No se queda abierto a propósito."
)
MENSAJE_NO_AUTORIZADO = (
    "Falta o no coincide la credencial. Manda la cabecera "
    "'Authorization: Bearer <LUMEN_MCP_TOKEN>'."
)


def _token_de_la_peticion(scope: dict) -> str | None:
    """Lee el bearer de las cabeceras crudas del scope ASGI."""
    for nombre, valor in scope.get("headers") or []:
        if nombre.lower() == b"authorization":
            texto = valor.decode("latin-1").strip()
            if texto.lower().startswith("bearer "):
                return texto[7:].strip()
            return None
    return None


async def _responder(send, estado: int, mensaje: str) -> None:
    """Respuesta JSON minima, sin depender de Starlette."""
    cuerpo = json.dumps({"detail": mensaje}, ensure_ascii=False).encode("utf-8")
    cabeceras = [
        (b"content-type", b"application/json; charset=utf-8"),
        (b"content-length", str(len(cuerpo)).encode("ascii")),
    ]
    if estado == 401:
        cabeceras.append((b"www-authenticate", b'Bearer realm="lumen-mcp"'))
    await send({"type": "http.response.start", "status": estado, "headers": cabeceras})
    await send({"type": "http.response.body", "body": cuerpo})


class GuardiaMCP:
    """App ASGI que envuelve el transporte del MCP y le exige credencial.

    Es una clase y no una funcion a proposito: Starlette trata un `endpoint`
    que sea funcion como handler de peticion (le pasaria un `Request`), y como
    app ASGI cualquier otro invocable. Siendo clase, se puede registrar
    directamente como ruta y `/mcp` responde sin redireccion.
    """

    def __init__(self, app) -> None:  # noqa: ANN001 - app ASGI generica
        self.app = app

    async def __call__(self, scope, receive, send) -> None:  # noqa: ANN001
        if scope["type"] != "http":
            # El lifespan tiene que pasar sin tocarse, o el gestor de sesiones
            # del MCP nunca arranca.
            await self.app(scope, receive, send)
            return

        ajustes = get_settings()

        if not ajustes.lumen_mcp_habilitado:
            await _responder(send, 503, MENSAJE_APAGADO)
            return

        esperado = ajustes.lumen_mcp_token
        if not esperado:
            log.warning("Llegó una petición a /mcp pero LUMEN_MCP_TOKEN está vacío.")
            await _responder(send, 503, MENSAJE_SIN_TOKEN)
            return

        # El `or ""` no es cosmetico: hace que el camino "sin cabecera" pase
        # igualmente por compare_digest, y no que salga antes por un
        # cortocircuito. Los dos rechazos tardan lo mismo.
        recibido = _token_de_la_peticion(scope) or ""
        if not hmac.compare_digest(recibido, esperado):
            log.info("Petición a /mcp rechazada: credencial ausente o incorrecta.")
            await _responder(send, 401, MENSAJE_NO_AUTORIZADO)
            return

        await self.app(scope, receive, send)


__all__ = ["GuardiaMCP", "MENSAJE_APAGADO", "MENSAJE_SIN_TOKEN", "MENSAJE_NO_AUTORIZADO"]
