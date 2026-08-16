"""Respaldo de grabacion: lee casos desde el dump JSON versionado. Dueno: Cristian (B3).

Con `LUMEN_USAR_DUMP_LOCAL=true`, la API responde desde aqui sin tocar Supabase
ni Croma (§5.3 del brief). No es la arquitectura: es lo que evita que un corte
de red a las 07:00 cueste el hackathon.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from ..config import get_settings
from ..contracts import Caso


@lru_cache
def _cargar_dump() -> dict[str, Caso]:
    ajustes = get_settings()
    ruta = Path(ajustes.lumen_dump_path)
    if not ruta.exists():
        return {}

    crudo = json.loads(ruta.read_text(encoding="utf-8"))
    casos_crudos = crudo if isinstance(crudo, list) else crudo.get("casos", [])
    return {c["id"]: Caso.model_validate(c) for c in casos_crudos}


def limpiar_cache_de_dump() -> None:
    """Solo para pruebas: fuerza a releer el archivo en la siguiente llamada."""
    _cargar_dump.cache_clear()


def obtener_caso_local(caso_id: str) -> Caso | None:
    return _cargar_dump().get(caso_id)


def listar_casos_local() -> list[Caso]:
    return list(_cargar_dump().values())
