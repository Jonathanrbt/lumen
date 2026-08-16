"""Coherencia de zona horaria. Dueno: Cristian (B3).

Render corre en UTC; el equipo razona en hora de Bogota (America/Bogota, UTC-5,
sin horario de verano). "Desde el 11 de agosto" tiene que significar el mismo
instante sin importar en que maquina se calcule (docs/handoff/CRISTIAN-B3.md).
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

BOGOTA = ZoneInfo("America/Bogota")


def inicio_de_dia_bogota_en_utc(dia: date) -> datetime:
    """El instante en que empieza `dia` en Bogota, expresado en UTC.

    Es lo que se manda a Croma como `from_date` y lo que se guarda en Supabase:
    un timestamp con zona horaria explicita, nunca una fecha ingenua.
    """
    inicio_local = datetime.combine(dia, time.min, tzinfo=BOGOTA)
    return inicio_local.astimezone(timezone.utc)
