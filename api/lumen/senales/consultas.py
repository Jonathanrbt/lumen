"""Una llamada Croma por (fuente, args) por corrida. No cuatro señales pegándole a RUES."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from ..croma.client import CromaClient, CromaError, CromaSinRespuesta

log = logging.getLogger(__name__)


class Consultas:
    def __init__(self, croma: CromaClient) -> None:
        self._croma = croma
        self._memoria: dict[str, Any] = {}
        self.consultado_en: datetime = datetime.now(timezone.utc)

    async def get(self, fuente: str, argumentos: dict[str, Any] | None = None) -> Any:
        argumentos = argumentos or {}
        clave = json.dumps({"f": fuente, "a": argumentos}, sort_keys=True)
        if clave in self._memoria:
            log.info("Croma cache local hit: %s", fuente)
            return self._memoria[clave]
        log.info("Croma consulta real: %s %s", fuente, argumentos)
        try:
            datos = await self._croma.consultar(fuente, argumentos)
        except (CromaError, CromaSinRespuesta) as err:
            log.warning("Croma no respondió %s: %s", fuente, err)
            datos = {"found": False, "error": str(err)}
        self._memoria[clave] = datos
        return datos
