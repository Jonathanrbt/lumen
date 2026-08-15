"""Cliente de Croma, la fuente unica de datos de Lumen.

## Lo que hay que saber antes de tocar esto

Croma **no es una API REST**. Es un servidor MCP remoto: habla JSON-RPC sobre HTTP
y responde en formato SSE (`text/event-stream`), autenticado con
`Authorization: Bearer <token>`.

La buena noticia, verificada contra el servidor real el 15.ago.2026 a las 17:20:

> **El servidor es stateless.** No hace falta handshake ni cabecera
> `Mcp-Session-Id`. Un solo POST con `method: "tools/call"` devuelve el resultado.

Por eso este cliente no depende del SDK de MCP: son `httpx` y un parseo de SSE.
Menos dependencias, menos cosas que fallen a las tres de la manana.

## Como se usa

```python
async with CromaClient() as croma:
    datos = await croma.call_tool("rues_entities_by_name", {"name": "Conalvias"})
```

`call_tool` sirve para **cualquiera** de las herramientas que expone Croma. No hay
que anadir un metodo por herramienta ni modificar este archivo para usar una nueva.
El inventario de las que necesitan nuestras 8 senales esta en `HERRAMIENTAS.md`.
"""

from __future__ import annotations

import asyncio
import json
import logging
from types import TracebackType
from typing import Any

import httpx

from ..config import get_settings

log = logging.getLogger(__name__)

TIMEOUT_SEGUNDOS = 90.0
MAX_INTENTOS_POLL = 30
ESPERA_ENTRE_POLLS = 2.0


class CromaError(RuntimeError):
    """Croma respondio, pero con un error.

    Distinto de un fallo de red o de autenticacion: aqui la llamada llego y el
    servidor dijo que no. Suele ser un argumento mal formado.
    """


class CromaSinRespuesta(RuntimeError):
    """No se pudo extraer un resultado del stream SSE.

    Casi siempre significa token invalido o URL equivocada. Revisa `CROMA_API_KEY`
    en tu `.env` antes de buscar por otro lado.
    """


def _parsear_sse(cuerpo: str) -> dict[str, Any]:
    """Extrae el objeto JSON-RPC del stream SSE.

    La respuesta llega como lineas `event: message` y `data: {...}`. Solo nos
    interesan las de datos, y el ultimo mensaje es el que trae el resultado.
    """
    ultimo: dict[str, Any] | None = None

    for linea in cuerpo.splitlines():
        linea = linea.strip()
        if not linea.startswith("data:"):
            continue
        carga = linea[len("data:") :].strip()
        if not carga or carga == "[DONE]":
            continue
        try:
            ultimo = json.loads(carga)
        except json.JSONDecodeError:
            log.warning("Croma devolvió una línea de datos que no es JSON: %s", carga[:200])

    if ultimo is None:
        raise CromaSinRespuesta(
            "El stream de Croma no traía ningún mensaje utilizable. "
            "Lo más probable es que CROMA_API_KEY esté vacía o sea inválida."
        )
    return ultimo


def _desempaquetar_contenido(resultado: dict[str, Any]) -> Any:
    """Saca el dato util de la envoltura MCP.

    MCP devuelve `{"content": [{"type": "text", "text": "<json como string>"}]}`.
    Lo que a nosotros nos importa es ese JSON ya parseado.
    """
    if resultado.get("isError"):
        raise CromaError(f"Croma reportó un error en la herramienta: {resultado}")

    bloques = resultado.get("content") or []
    textos = [b.get("text", "") for b in bloques if b.get("type") == "text"]

    if not textos:
        # Algunas herramientas devuelven contenido estructurado directamente.
        return resultado.get("structuredContent", resultado)

    crudo = "\n".join(textos)
    try:
        return json.loads(crudo)
    except json.JSONDecodeError:
        # Herramientas como las de busqueda web pueden devolver texto plano.
        return crudo


class CromaClient:
    """Cliente asincrono de Croma.

    Usalo como context manager para que la conexion se cierre sola:

    ```python
    async with CromaClient() as croma:
        ...
    ```
    """

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        timeout: float = TIMEOUT_SEGUNDOS,
    ) -> None:
        ajustes = get_settings()
        self.url = url or ajustes.croma_mcp_url
        self.api_key = api_key if api_key is not None else ajustes.croma_api_key
        self._id = 0
        self._http = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
            },
        )

    async def __aenter__(self) -> "CromaClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    def _siguiente_id(self) -> int:
        self._id += 1
        return self._id

    async def _rpc(self, metodo: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        cuerpo = {
            "jsonrpc": "2.0",
            "id": self._siguiente_id(),
            "method": metodo,
            "params": params or {},
        }
        respuesta = await self._http.post(self.url, json=cuerpo)
        respuesta.raise_for_status()

        mensaje = _parsear_sse(respuesta.text)

        if "error" in mensaje:
            raise CromaError(f"Croma respondió con error en '{metodo}': {mensaje['error']}")

        return mensaje.get("result", {})

    async def initialize(self) -> dict[str, Any]:
        """Handshake MCP.

        No hace falta para llamar herramientas (el servidor es stateless), pero es
        la forma mas barata de comprobar que el token sirve. Es lo que usa
        `/health/croma`.
        """
        return await self._rpc(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "lumen", "version": "0.1.0"},
            },
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        """Inventario de herramientas con su esquema de entrada.

        Util cuando no recuerdas como se llama un parametro y no quieres abrir la
        documentacion.
        """
        resultado = await self._rpc("tools/list")
        return resultado.get("tools", [])

    async def call_tool(
        self,
        nombre: str,
        argumentos: dict[str, Any] | None = None,
        esperar_pendientes: bool = True,
    ) -> Any:
        """Llama una herramienta de Croma y devuelve su dato ya parseado.

        Args:
            nombre: la herramienta, ej. `"rues_entity_by_nit"`.
            argumentos: sus parametros. El esquema de cada una sale de `list_tools()`.
            esperar_pendientes: las consultas lentas devuelven un trabajo pendiente
                con un `status_url`. Si es True, se hace polling hasta que termine.

        Devuelve `found: false` cuando el sujeto no tiene registro. **Eso es una
        respuesta definitiva, no un error**: significa que la fuente oficial no
        tiene nada sobre esa empresa o persona, y para una senal eso puede ser
        justo el dato relevante.
        """
        resultado = await self._rpc(
            "tools/call", {"name": nombre, "arguments": argumentos or {}}
        )
        datos = _desempaquetar_contenido(resultado)

        if esperar_pendientes and isinstance(datos, dict) and datos.get("status_url"):
            datos = await self._esperar_trabajo(datos)

        return datos

    async def _esperar_trabajo(self, pendiente: dict[str, Any]) -> Any:
        """Hace polling de un trabajo lento hasta que Croma lo termina.

        Croma avisa en sus instrucciones que las consultas lentas devuelven un
        trabajo pendiente con un `status_url`. Esto lo resuelve de forma
        defensiva: si la forma de la respuesta no es la esperada, devuelve lo que
        haya en vez de romper.
        """
        status_url = pendiente["status_url"]
        log.info("Croma devolvió un trabajo pendiente, esperando: %s", status_url)

        for intento in range(MAX_INTENTOS_POLL):
            await asyncio.sleep(ESPERA_ENTRE_POLLS)
            try:
                respuesta = await self._http.get(status_url)
                respuesta.raise_for_status()
                actual = respuesta.json()
            except (httpx.HTTPError, json.JSONDecodeError) as err:
                log.warning("Falló el polling del trabajo de Croma: %s", err)
                return pendiente

            estado = str(actual.get("status", "")).lower()
            if estado not in {"pending", "running", "queued", "in_progress"}:
                return actual

        log.warning(
            "El trabajo de Croma seguía pendiente tras %s intentos. Devuelvo el pendiente.",
            MAX_INTENTOS_POLL,
        )
        return pendiente


async def probar_conexion() -> dict[str, Any]:
    """Comprueba que el token de Croma de esta máquina funciona de verdad.

    Hace una llamada real al servidor, no un ping. Es lo que respalda
    `/health/croma`, el primer verde que tienen que ver los cuatro al arrancar.
    """
    ajustes = get_settings()
    if not ajustes.croma_configurado:
        return {
            "estado": "sin_configurar",
            "detalle": "CROMA_API_KEY está vacía. Copia .env.example a .env y pega el valor del chat privado.",
        }

    try:
        async with CromaClient() as croma:
            info = await croma.initialize()
            herramientas = await croma.list_tools()
    except Exception as err:  # noqa: BLE001 - en el health queremos el motivo, no el stacktrace
        return {"estado": "error", "detalle": f"{type(err).__name__}: {err}"}

    servidor = info.get("serverInfo", {})
    return {
        "estado": "ok",
        "servidor": f"{servidor.get('name', '?')} {servidor.get('version', '')}".strip(),
        "herramientas_disponibles": len(herramientas),
    }
