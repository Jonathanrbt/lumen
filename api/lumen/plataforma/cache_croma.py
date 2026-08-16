"""Cache de respuestas de Croma en Supabase. Dueno: Cristian (B3).

El token de Croma es compartido entre las 4 personas y el monitor, y tiene
cuota (docs/PLAN.md §4). Esto evita repetir una llamada identica: misma
herramienta, mismos parametros, misma respuesta servida sin salir a la red.

Ver spec `plataforma/cache-croma`: una `Fuente` construida desde una respuesta
cacheada debe conservar la fecha de la llamada ORIGINAL, no la del acierto de
cache. Por eso `llamar_con_cache` siempre devuelve ese `consultado_en` junto
con el dato.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from ..croma.client import CromaClient
from .supabase_client import SupabaseNoConfigurado, get_supabase

log = logging.getLogger(__name__)

TABLA = "cache_croma"

_AVISO_SIN_CACHE_DADO = False


def _aviso_sin_cache(motivo: str) -> None:
    """Avisa una sola vez por proceso, no una vez por consulta.

    Sin cache seguimos funcionando, pero cada llamada sale a Croma de verdad y
    el token es compartido entre las cuatro personas. Que se vea en el log una
    vez es util; que se vea 400 veces es ruido que tapa lo importante.
    """
    global _AVISO_SIN_CACHE_DADO
    if not _AVISO_SIN_CACHE_DADO:
        log.warning(
            "Cache de Croma DESACTIVADA (%s). Cada consulta sale a la red y "
            "consume cuota compartida.",
            motivo,
        )
        _AVISO_SIN_CACHE_DADO = True


def _clave(herramienta: str, argumentos: dict[str, Any]) -> str:
    crudo = json.dumps({"herramienta": herramienta, "argumentos": argumentos}, sort_keys=True)
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()


async def llamar_con_cache(
    croma: CromaClient,
    herramienta: str,
    argumentos: dict[str, Any] | None = None,
) -> tuple[Any, datetime]:
    """Devuelve `(respuesta, consultado_en)`.

    Si la entrada ya esta en `cache_croma`, no se llama a Croma. Si no, se llama,
    se guarda, y se devuelve el momento de esa llamada original.

    El cache es una optimizacion de cuota, no un requisito de correccion: si
    Supabase no esta configurado o falla, la consulta sale igual a Croma y solo
    se pierde el ahorro. Tumbar el barrido porque el cache no esta disponible
    seria cambiar un problema de cuota por uno de disponibilidad.
    """
    argumentos = argumentos or {}
    clave = _clave(herramienta, argumentos)

    try:
        supabase = get_supabase()
    except SupabaseNoConfigurado as err:
        _aviso_sin_cache(str(err).split(".")[0])
        return await croma.call_tool(herramienta, argumentos), datetime.now(timezone.utc)

    try:
        existente = (
            supabase.table(TABLA)
            .select("respuesta, consultado_en")
            .eq("clave", clave)
            .limit(1)
            .execute()
        )
    except Exception as err:  # noqa: BLE001 - un cache caido no puede tumbar el barrido
        _aviso_sin_cache(f"error leyendo {TABLA}: {type(err).__name__}")
        return await croma.call_tool(herramienta, argumentos), datetime.now(timezone.utc)

    if existente.data:
        fila = existente.data[0]
        log.debug("Cache hit para %s (clave %s...)", herramienta, clave[:8])
        return fila["respuesta"], datetime.fromisoformat(fila["consultado_en"])

    respuesta = await croma.call_tool(herramienta, argumentos)
    consultado_en = datetime.now(timezone.utc)

    try:
        supabase.table(TABLA).insert(
            {
                "clave": clave,
                "herramienta": herramienta,
                "argumentos": argumentos,
                "respuesta": respuesta,
                "consultado_en": consultado_en.isoformat(),
            }
        ).execute()
    except Exception as err:  # noqa: BLE001 - ya tenemos el dato; no guardarlo solo cuesta cuota
        log.warning("No se pudo guardar en %s: %s", TABLA, err)

    return respuesta, consultado_en
