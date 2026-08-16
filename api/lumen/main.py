"""Aplicacion FastAPI de Lumen.

Dueno de este archivo: Cristian (B3). Ya esta montado, asi que tocarlo deberia ser
raro. Cada persona trabaja dentro de su propio router:

    routers/analisis.py    -> Jonatin (B1)
    routers/ia.py          -> Freddy  (B2)
    routers/plataforma.py  -> Cristian (B3)

Asi cuatro personas meten commits al mismo backend sin editar nunca el mismo
archivo.

Ademas de los routers, este archivo monta el servidor MCP en `/mcp`
(`lumen/mcp/`, tambien de Cristian). Son dos transportes sobre el mismo motor:
HTTP para el frontend de Andrew, MCP para agentes externos. Ninguno de los dos
tiene logica propia.

Y por eso este archivo declara un `lifespan`, que antes no tenia: la sub-app
del MCP trae el suyo (el gestor de sesiones del protocolo) y Starlette **no**
corre el lifespan de una sub-app montada. Sin encadenarlo aqui, la primera
peticion a `/mcp` muere con "task group is not initialized" y el resto de la
API ni se entera.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route

from .config import VERSION, get_settings
from .contracts import HealthCromaResponse, HealthResponse
from .croma.client import probar_conexion
from .mcp import RUTAS_MCP, app_mcp, lifespan_mcp
from .routers import analisis, ia, plataforma

ajustes = get_settings()

logging.basicConfig(
    level=getattr(logging, ajustes.lumen_log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Arranca el gestor de sesiones del MCP junto con la app.

    No toca la red ni hace E/S: solo abre el task group que el transporte
    necesita. Aun asi, si esto reventara se caeria toda la API, asi que
    `api/tests/test_mcp.py` levanta la app completa para que un fallo de
    arranque salga en pytest y no en Render.
    """
    async with lifespan_mcp():
        yield


app = FastAPI(
    title="Lumen API",
    version=VERSION,
    lifespan=lifespan,
    description=(
        "Vigilancia ciudadana sobre la contratación pública de la reconstrucción. "
        "Un motor, dos modos: emergencia (push) y vigilancia (pull). "
        "Herramienta de priorización: una señal no es prueba de irregularidad."
    ),
)

# El dominio del frontend lo define Andrew. Cuando lo sepa, entra en
# LUMEN_CORS_ORIGINS aqui y en las variables de entorno de Render.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ajustes.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analisis.router)
app.include_router(ia.router)
app.include_router(plataforma.router)

# Servidor MCP: una app ASGI con su propio protocolo, no un router.
#
# Va como dos rutas exactas y NO como `app.mount("/mcp", ...)`: el mount de
# Starlette compila su ruta como `/mcp/{path:path}`, asi que `/mcp` a secas no
# casaria y el cliente se comeria un 307 hacia `/mcp/` en cada peticion. Ver
# `lumen/mcp/servidor.py` para el detalle.
#
# El guardia de bearer token ya viene puesto desde alli, pegado a lo que
# protege, para que un cambio de rutas aqui no pueda dejarlo abierto.
for _ruta_mcp in RUTAS_MCP:
    app.router.routes.append(Route(_ruta_mcp, endpoint=app_mcp))


@app.get("/health", response_model=HealthResponse, tags=["salud"])
async def health() -> HealthResponse:
    """Responde sin tocar nada externo. Sirve para el health check de Render."""
    return HealthResponse(estado="ok", entorno=ajustes.lumen_env, version=VERSION)


@app.get("/health/croma", response_model=HealthCromaResponse, tags=["salud"])
async def health_croma() -> HealthCromaResponse:
    """Hace una llamada real a Croma y confirma que tu token funciona.

    Es el primer verde que tienen que ver los cuatro en el bloque de arranque. Si
    esto falla, no empieces a codear: revisa CROMA_API_KEY en tu `.env`.
    """
    resultado = await probar_conexion()
    return HealthCromaResponse(**resultado)
