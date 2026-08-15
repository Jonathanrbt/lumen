"""Aplicacion FastAPI de Lumen.

Dueno de este archivo: Cristian (B3). Ya esta montado, asi que tocarlo deberia ser
raro. Cada persona trabaja dentro de su propio router:

    routers/analisis.py    -> Jonatin (B1)
    routers/ia.py          -> Freddy  (B2)
    routers/plataforma.py  -> Cristian (B3)

Asi cuatro personas meten commits al mismo backend sin editar nunca el mismo
archivo.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import VERSION, get_settings
from .contracts import HealthCromaResponse, HealthResponse
from .croma.client import probar_conexion
from .routers import analisis, ia, plataforma

ajustes = get_settings()

logging.basicConfig(
    level=getattr(logging, ajustes.lumen_log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)

app = FastAPI(
    title="Lumen API",
    version=VERSION,
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
