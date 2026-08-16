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
from .supabase_client import get_supabase

log = logging.getLogger(__name__)

TABLA = "cache_croma"


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
    """
    argumentos = argumentos or {}
    clave = _clave(herramienta, argumentos)
    supabase = get_supabase()

    existente = (
        supabase.table(TABLA)
        .select("respuesta, consultado_en")
        .eq("clave", clave)
        .limit(1)
        .execute()
    )
    if existente.data:
        fila = existente.data[0]
        log.debug("Cache hit para %s (clave %s...)", herramienta, clave[:8])
        return fila["respuesta"], datetime.fromisoformat(fila["consultado_en"])

    respuesta = await croma.call_tool(herramienta, argumentos)
    consultado_en = datetime.now(timezone.utc)

    supabase.table(TABLA).insert(
        {
            "clave": clave,
            "herramienta": herramienta,
            "argumentos": argumentos,
            "respuesta": respuesta,
            "consultado_en": consultado_en.isoformat(),
        }
    ).execute()

    return respuesta, consultado_en
