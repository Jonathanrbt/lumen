"""Unico punto de entrada al LLM. Dueno: Freddy (B2).

Todo lo que habla con un modelo pasa por aqui y solo por aqui: si a las tres
de la manana el consumo se dispara o la latencia mata el chat, se cambia de
proveedor en veinte minutos y no en seis horas.

Las seis reglas de presupuesto del handoff, todas viven en este modulo:

1. Un solo llm_client (este).
2. `cwd` apunta a `LUMEN_SCRATCH_DIR`, nunca a la raiz del repo: un agente
   suelto sobre el repo lee archivos que nadie pidio y quema presupuesto.
3. `setting_sources=[]` siempre.
4. Los 6 casos del catalogo se precomputan y cachean en otra capa (no aqui):
   durante la grabacion, cero llamadas al LLM en vivo.
5. `AsyncClient.launch_bridge`, nunca mezclar clientes sync y async en el
   mismo path — el SDK es sincrono por dentro, FastAPI es async.
6. El agente siempre se dispone con context manager, o se filtran procesos.

Un septimo hallazgo, medido en vivo (16.ago, ~01:15): sin restringir
herramientas, cada llamada carga ~11k tokens de entrada en definiciones de
herramientas que este producto nunca usa (no leemos ni escribimos archivos
del repo, solo analizamos texto). Con `tools=[]` baja a ~3.3k. Por eso
`tools=[]` es el default aqui y no una opcion.

Higiene de errores, para no perder una hora confundiendolos:
`CursorAgentError` significa que el run NUNCA arranco (auth, config o red).
Un `resultado.status == "error"` significa que arranco y fallo. Este modulo
deja que `CursorAgentError` se propague tal cual, y convierte el segundo caso
en `LLMEjecucionError` para que quien llama nunca los confunda.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from enum import Enum
from typing import AsyncIterator

from cursor_sdk import (
    AgentOptions,
    AsyncAgent,
    AsyncClient,
    CursorAgentError,
    LocalAgentOptions,
)

from ..config import Settings, get_settings

__all__ = ["CursorAgentError", "LLMEjecucionError", "Modelo", "preguntar"]


class Modelo(str, Enum):
    """Cual de los dos IDs fijados en `.env` usar. Nunca un ID de modelo suelto
    en el codigo de negocio — eso vive solo aqui."""

    RAPIDO = "rapido"  # narracion, resolucion de entidades
    FUERTE = "fuerte"  # lector de justificaciones: pocas llamadas, la feature que gana los 25 puntos


class LLMEjecucionError(RuntimeError):
    """El agente arranco pero `resultado.status` no fue 'finished'.

    Distinto de `CursorAgentError` (el run nunca arranco). Confundir los dos
    cuesta una hora, segun el handoff — por eso son dos excepciones distintas.
    """


def _id_modelo(ajustes: Settings, modelo: Modelo) -> str:
    id_modelo = ajustes.lumen_modelo_rapido if modelo is Modelo.RAPIDO else ajustes.lumen_modelo_fuerte
    if not id_modelo:
        raise CursorAgentError(
            f"Falta configurar LUMEN_MODELO_{'RAPIDO' if modelo is Modelo.RAPIDO else 'FUERTE'} "
            "en el entorno."
        )
    return id_modelo


@asynccontextmanager
async def _cliente(ajustes: Settings) -> AsyncIterator[AsyncClient]:
    client = await AsyncClient.launch_bridge(workspace=ajustes.lumen_scratch_dir)
    try:
        yield client
    finally:
        await client.aclose()


async def preguntar(prompt: str, modelo: Modelo) -> str:
    """Un solo turno, sin memoria entre llamadas. Devuelve el texto de la respuesta.

    `CursorAgentError` se propaga sin envolver: es un problema de configuracion
    (auth, red), no del contenido. Si el agente corre pero no termina bien, se
    levanta `LLMEjecucionError` con el detalle.
    """
    ajustes = get_settings()
    id_modelo = _id_modelo(ajustes, modelo)

    async with _cliente(ajustes) as client:
        resultado = await AsyncAgent.prompt(
            prompt,
            AgentOptions(
                model=id_modelo,
                local=LocalAgentOptions(cwd=ajustes.lumen_scratch_dir, setting_sources=[]),
                tools=[],
            ),
            client=client,
        )

    if resultado.status != "finished":
        raise LLMEjecucionError(
            f"El agente ({id_modelo}) corrio y no termino bien: status={resultado.status!r}"
        )

    return resultado.result
