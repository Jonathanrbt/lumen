"""Persistencia y lectura de Caso. Dueno: Cristian (B3).

Sirve `GET /caso/{caso_id}` (spec `plataforma/casos`): lee de Supabase, o del
dump local si `LUMEN_USAR_DUMP_LOCAL` esta activo. Guarda el `Caso` que arma el
motor de Jonatin (B1) cuando el monitor o el precomputo lo llaman.

Los dos guardarraíles del contrato — `Senal` exige `Fuente`, `nivel_atencion`
es un enum de tres valores — ya estan garantizados por el tipo `Caso` en si
(ver `contracts/modelos.py`): si esta funcion recibe un `Caso`, ya los cumple.
Esto no los repite, los hereda.
"""

from __future__ import annotations

import json
from typing import Any

from ..config import get_settings
from ..contracts import Caso
from .dump_local import obtener_caso_local
from .supabase_client import get_supabase

TABLA = "casos"


def _a_fila(caso: Caso) -> dict[str, Any]:
    return {
        "id": caso.id,
        "modo": caso.modo.value,
        "nivel_atencion": caso.nivel_atencion.value,
        "municipio": caso.municipio,
        "departamento": caso.departamento,
        "cuerpo": json.loads(caso.model_dump_json()),
    }


def guardar_caso(caso: Caso, *, contrato_id: str | None = None) -> None:
    """Guarda (o reemplaza) un Caso en Supabase.

    `contrato_id` es el identificador crudo de Croma que originó el caso desde
    el monitor — se guarda aparte del `Caso.id` para que el filtro de novedad
    (`plataforma/monitor-emergencia`) pueda reconocer un contrato ya procesado
    aunque el motor le haya asignado otro `id` al caso.
    """
    fila = _a_fila(caso)
    if contrato_id:
        fila["contrato_id"] = contrato_id

    supabase = get_supabase()
    supabase.table(TABLA).upsert(fila, on_conflict="id").execute()


def obtener_caso(caso_id: str) -> Caso | None:
    ajustes = get_settings()
    if ajustes.lumen_usar_dump_local:
        return obtener_caso_local(caso_id)

    supabase = get_supabase()
    resultado = supabase.table(TABLA).select("cuerpo").eq("id", caso_id).limit(1).execute()
    if not resultado.data:
        return None
    return Caso.model_validate(resultado.data[0]["cuerpo"])


def contrato_ya_conocido(contrato_id: str) -> bool:
    """Filtro de novedad: True si ese contrato ya tiene un Caso guardado."""
    supabase = get_supabase()
    resultado = (
        supabase.table(TABLA).select("id").eq("contrato_id", contrato_id).limit(1).execute()
    )
    return bool(resultado.data)
