"""Cliente HTTP de Croma, la fuente unica de datos de Lumen.

Croma se consulta por **API HTTP**: `POST https://api.croma.run/co/.../v1` con
JSON y `Authorization: Bearer <CROMA_API_KEY>`. La respuesta util viene en
`{ "data": ... }`. `found: false` es dato, no error.

El MCP de Cursor no entra aqui. Las rutas del corte estan en `HERRAMIENTAS.md`.
Leer la guia de la fuente antes de armar el cuerpo.

```python
async with CromaClient() as croma:
    datos = await croma.consultar("rues_entities_by_name", {"name": "Conalvias"})
```
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
BASE_URL = "https://api.croma.run"

# Alias del corte -> ruta HTTP. Nombres iguales a las senales de HERRAMIENTAS.md.
RUTAS: dict[str, str] = {
    "rues_entities_by_name": "/co/rues/entities-by-name/v1",
    "rues_entity_by_nit": "/co/rues/entity-by-nit/v1",
    "secop_process": "/co/secop/process/v1",
    "secop_contracts_by_provider": "/co/secop/contracts-by-provider/v1",
    "secop_processes_by_entity": "/co/secop/processes-by-entity/v1",
    "secop_contract": "/co/secop/contract/v1",
    "secop_sanctions_by_provider": "/co/secop/sanctions-by-provider/v1",
    "supersociedades_financial_statements": "/co/supersociedades/financial-statements/v1",
    "sicaac_insolvency_cases": "/co/sicaac/insolvency-cases/v1",
    "contaduria_state_delinquent_debtors": "/co/contaduria/state-delinquent-debtors/v1",
    "procuraduria_disciplinary_records": "/co/procuraduria/disciplinary-records/v1",
    "contraloria_fiscal_records": "/co/contraloria/fiscal-records/v1",
    "legalize_laws_search": "/co/legalize/laws/v1",
    "legalize_law": "/co/legalize/law/v1",
    "ancp_cce_conceptos_search": "/co/ancp-cce/conceptos-search/v1",
    "ancp_cce_concepto": "/co/ancp-cce/concepto/v1",
}


class CromaError(RuntimeError):
    """Croma respondio, pero con un error de negocio o de validacion."""


class CromaDeshabilitado(CromaError):
    """El interruptor `LUMEN_CROMA_HABILITADO` esta en false.

    No es un fallo: es una decision de ahorro. El token de Croma es UNO para
    las cuatro personas mas el monitor, y los creditos son finitos. Hereda de
    `CromaError` a proposito, para que todo el codigo que ya lo captura degrade
    igual que ante cualquier otro fallo de Croma en vez de reventar.
    """


class CromaSinRespuesta(RuntimeError):
    """La respuesta no era JSON utilizable. Suele ser token invalido."""


def _cuerpo_rues_por_nit(argumentos: dict[str, Any]) -> dict[str, Any]:
    """La guia REST pide `document_number`, no `nit`."""
    cuerpo = dict(argumentos)
    if "document_number" not in cuerpo and "nit" in cuerpo:
        cuerpo["document_number"] = cuerpo.pop("nit")
    return cuerpo


NORMALIZAR: dict[str, Any] = {
    "rues_entity_by_nit": _cuerpo_rues_por_nit,
}


class CromaClient:
    """Cliente asincrono de la API HTTP de Croma."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = TIMEOUT_SEGUNDOS,
    ) -> None:
        ajustes = get_settings()
        self.base_url = BASE_URL
        self.api_key = api_key if api_key is not None else ajustes.croma_api_key
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
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

    async def consultar(
        self,
        fuente: str,
        argumentos: dict[str, Any] | None = None,
        esperar_pendientes: bool = True,
    ) -> Any:
        """POST a la ruta de `fuente` y devuelve el `data` ya desempaquetado."""
        # Interruptor de ahorro. Va ANTES de mirar la ruta y antes de tocar la
        # red: si esta apagado, no sale ni una peticion.
        if not get_settings().lumen_croma_habilitado:
            raise CromaDeshabilitado(
                f"Croma está desactivado (LUMEN_CROMA_HABILITADO=false), no se consultó "
                f"'{fuente}'. Se apagó para no gastar créditos del token compartido. "
                f"Para volver a activarlo, ponlo en true en tu .env."
            )

        if fuente not in RUTAS:
            raise CromaError(
                f"Fuente '{fuente}' no esta en el corte. "
                "Revisa HERRAMIENTAS.md o agrega la ruta en RUTAS."
            )
        cuerpo = dict(argumentos or {})
        if fuente in NORMALIZAR:
            cuerpo = NORMALIZAR[fuente](cuerpo)

        ruta = RUTAS[fuente]
        log.info(
            "Croma HTTP POST %s%s cuerpo=%s",
            self.base_url,
            ruta,
            json.dumps(cuerpo, ensure_ascii=False, default=str),
        )
        respuesta = await self._http.post(ruta, json=cuerpo)
        log.info(
            "Croma HTTP %s %s%s (%s bytes)",
            respuesta.status_code,
            self.base_url,
            ruta,
            len(respuesta.content),
        )

        if respuesta.status_code == 202:
            datos = _leer_json(respuesta)
            if esperar_pendientes:
                return await self._esperar_trabajo(respuesta, datos)
            return datos.get("data", datos)

        if respuesta.status_code >= 400:
            raise CromaError(_mensaje_error(respuesta))

        datos = _leer_json(respuesta)
        if isinstance(datos, dict) and "error" in datos:
            raise CromaError(f"Croma reportó un error en '{fuente}': {datos['error']}")

        if isinstance(datos, dict) and "data" in datos:
            return datos["data"]
        return datos

    call_tool = consultar

    async def _esperar_trabajo(self, respuesta: httpx.Response, pendiente: dict[str, Any]) -> Any:
        """Polling de jobs async (SICAAC, Contaduria, etc.)."""
        job_url = (
            respuesta.headers.get("Location")
            or pendiente.get("status_url")
            or _url_job(pendiente)
        )
        if not job_url:
            return pendiente.get("data", pendiente)

        log.info("Croma devolvió un trabajo pendiente, esperando: %s", job_url)

        for _intento in range(MAX_INTENTOS_POLL):
            await asyncio.sleep(ESPERA_ENTRE_POLLS)
            try:
                poll = await self._http.get(job_url)
                poll.raise_for_status()
                actual = poll.json()
            except (httpx.HTTPError, json.JSONDecodeError) as err:
                log.warning("Falló el polling del trabajo de Croma: %s", err)
                return pendiente.get("data", pendiente)

            estado = str(actual.get("status", "")).lower()
            if estado in {"pending", "running", "queued", "in_progress"}:
                continue
            if isinstance(actual, dict) and "data" in actual:
                return actual["data"]
            return actual

        log.warning(
            "El trabajo de Croma seguía pendiente tras %s intentos.",
            MAX_INTENTOS_POLL,
        )
        return pendiente.get("data", pendiente)


def _url_job(pendiente: dict[str, Any]) -> str | None:
    job_id = pendiente.get("id") or pendiente.get("job_id")
    if job_id:
        return f"/jobs/{job_id}"
    return None


def _leer_json(respuesta: httpx.Response) -> dict[str, Any]:
    try:
        return respuesta.json()
    except json.JSONDecodeError as err:
        raise CromaSinRespuesta(
            "Croma no devolvió JSON. Revisa CROMA_API_KEY."
        ) from err


def _mensaje_error(respuesta: httpx.Response) -> str:
    try:
        carga = respuesta.json()
        error = carga.get("error", carga)
        return f"HTTP {respuesta.status_code}: {error}"
    except json.JSONDecodeError:
        return f"HTTP {respuesta.status_code}: {respuesta.text[:300]}"


async def probar_conexion() -> dict[str, Any]:
    """Comprueba que el token funciona con una llamada real a RUES."""
    ajustes = get_settings()
    if not ajustes.lumen_croma_habilitado:
        # Este endpoint hace una consulta REAL, asi que abrirlo desde /docs
        # gasta creditos. Con el interruptor apagado ni lo intenta.
        return {
            "estado": "desactivado",
            "detalle": (
                "LUMEN_CROMA_HABILITADO=false: no se consultó Croma para no gastar "
                "créditos del token compartido. El resto de la API sigue funcionando."
            ),
        }

    if not ajustes.croma_configurado:
        return {
            "estado": "sin_configurar",
            "detalle": "CROMA_API_KEY está vacía. Copia .env.example a .env y pega el valor del chat privado.",
        }

    try:
        async with CromaClient() as croma:
            datos = await croma.consultar("rues_entities_by_name", {"name": "exito", "page": 1})
    except Exception as err:  # noqa: BLE001
        return {"estado": "error", "detalle": f"{type(err).__name__}: {err}"}

    entidades = 0
    if isinstance(datos, dict):
        entidades = len(datos.get("entities") or [])

    return {
        "estado": "ok",
        "servidor": "api.croma.run",
        "herramientas_disponibles": len(RUTAS),
        "detalle": f"RUES respondió ({entidades} entidades en la página).",
    }
