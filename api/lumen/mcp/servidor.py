"""Arma el servidor MCP y lo deja listo para montar. Dueno: Cristian (B3).

Dos cosas que hay que saber del SDK antes de tocar esto, las dos comprobadas
contra `mcp==2.0.0` y no supuestas:

1. **`streamable_http_app()` auto-activa proteccion DNS-rebinding cuando `host`
   es localhost** (su valor por defecto). En Render el `Host` es
   `algo.onrender.com`, asi que con el default TODAS las peticiones se
   rechazarian. Por eso se pasa `transport_security` explicito.

2. **La app que devuelve trae su propio `lifespan`** (`session_manager.run()`),
   y Starlette NO corre el lifespan de una sub-app montada. Sin arrancarlo a
   mano desde el lifespan de `main.py`, la primera peticion muere con
   "task group is not initialized". Por eso `lifespan_mcp` se exporta y
   `main.py` lo encadena.

Y una tercera, medida montandolo y no supuesta: con `app.mount("/mcp", ...)`,
una peticion a `/mcp` (sin barra final) se iba en **307 hacia `/mcp/`**. El
`Mount` de Starlette compila su ruta como `/mcp/{path:path}`, asi que `/mcp` a
secas no casa y el router redirige. Es justo la URL que la gente va a pegar en
su cliente, y hay clientes que no siguen redirecciones o que sueltan la
cabecera `Authorization` al hacerlo.

Por eso esto NO se monta: se registran las dos rutas exactas (`/mcp` y `/mcp/`)
sobre el ASGI crudo del transporte, que ignora el path porque solo sirve ese
unico endpoint. Cero redirecciones por cualquiera de las dos, y sin tragarse
`/mcp/loquesea` como haria un mount.
"""

from __future__ import annotations

from mcp.server import MCPServer
from mcp.server.streamable_http_manager import StreamableHTTPASGIApp
from mcp.server.transport_security import TransportSecuritySettings

from ..config import VERSION
from .auth import GuardiaMCP
from .herramientas import registrar_herramientas
from .instrucciones import INSTRUCCIONES_SERVIDOR
from .prompts import registrar_prompts

# Las dos formas de escribir la misma URL. Ninguna redirige.
RUTAS_MCP = ("/mcp", "/mcp/")

# Proteccion DNS-rebinding desactivada a conciencia, no por descuido. Existe
# para servidores MCP locales, donde una pagina web puede alcanzar localhost.
# Aqui el servidor es publico y el guardia es el bearer token: un navegador no
# lo tiene, y CORS va con allow_credentials=False. Dejarla activada obligaria a
# mantener el dominio de Render en una variable mas, que es una cosa mas que
# puede faltar a las 02:00.
SEGURIDAD_TRANSPORTE = TransportSecuritySettings(enable_dns_rebinding_protection=False)


def _construir() -> MCPServer:
    servidor = MCPServer(
        name="lumen",
        title="Lumen · vigilancia ciudadana de la contratación pública",
        version=VERSION,
        instructions=INSTRUCCIONES_SERVIDOR,
        website_url="https://docs.usecroma.com",
    )
    registrar_herramientas(servidor)
    registrar_prompts(servidor)
    return servidor


servidor_mcp = _construir()

# Se llama a `streamable_http_app()` por su efecto: es la via publica que
# construye el gestor de sesiones con estos ajustes y lo deja accesible en
# `servidor_mcp.session_manager`. La app Starlette que devuelve se descarta —
# lo unico que aportaba era el enrutado que provoca el 307.
servidor_mcp.streamable_http_app(
    transport_security=SEGURIDAD_TRANSPORTE,
    host="0.0.0.0",  # noqa: S104 - no abre un socket, solo evita el auto-localhost
)

# El ASGI crudo del transporte. Su docstring en el SDK dice que `session_manager`
# se expone precisamente para "montar varias instancias en una sola aplicacion
# FastAPI", asi que esto es la via prevista, no un atajo por dentro.
_app_transporte = StreamableHTTPASGIApp(servidor_mcp.session_manager)

# El guardia va por fuera: primero la credencial, y solo despues se toca nada
# del transporte. Deja pasar el scope de lifespan sin tocarlo, o el gestor de
# sesiones nunca arrancaria.
app_mcp = GuardiaMCP(_app_transporte)


def lifespan_mcp():  # noqa: ANN201 - AbstractAsyncContextManager[None]
    """El gestor de sesiones del MCP, para encadenarlo al lifespan de la app."""
    return servidor_mcp.session_manager.run()


__all__ = ["app_mcp", "lifespan_mcp", "servidor_mcp"]
