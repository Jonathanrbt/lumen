"""Monitor de Modo Emergencia. Dueno: Cristian (B3).

Camina los pasos 1-2 y 7-9 del Flujo A (docs/brief-final-claude.md §4.6):
encuentra actividad contractual nueva en las entidades afectadas, descarta lo
que ya esta en base, arma el Caso llamando al motor de Jonatin (B1) y dispara
alertas si el nivel de atencion lo amerita.

Los pasos 3-6 (enriquecimiento, las 8 señales, el lector de IA, el nivel de
atencion) son `POST /analizar`, de Jonatin — este modulo lo invoca, no lo
reimplementa.

## Por que se recorren entidades y no "contratos de urgencia"

Croma **no** barre por departamento ni por causal de desastre: no existe esa
ruta. Jonatin lo verifico en vivo y dejo la lista de entidades afectadas en
`senales/entidades_emergencia.py` (commit c894509). Aqui se recorre esa lista.

## Por que se analiza por entidad y no por proceso

`secop_processes_by_entity` devuelve **procesos** (pre-adjudicacion): traen
`notice_uid` (`CO1.NTC.*`), `base_price` y `published_date`, y muchas veces
todavia no tienen proveedor. El `contrato_id` que acepta `/analizar` es otra
cosa: un `CO1.PCCNTR.*` que se consulta con `secop_contract`. Pasar un
`notice_uid` por ahi devuelve `found: false` y produce un caso vacio.

Asi que el proceso sirve para **detectar novedad** (su `notice_uid` es la
llave) y la entidad es la **unidad de analisis**. Un barrido produce como mucho
un caso por entidad, no uno por proceso: son 4 analisis en vez de 427, que es
lo unico que cabe en la cuota compartida de Croma.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from fastapi import HTTPException

from ..config import get_settings
from ..contracts import AnalizarRequest, Caso, NivelAtencion
from ..croma.client import CromaClient, CromaSinRespuesta
from ..routers.analisis import analizar
from ..senales.entidades_emergencia import ENTIDADES_EMERGENCIA, FECHA_APERTURA
from ..alertas import enviar_alerta  # despachador Telegram/WhatsApp, dueno Freddy (B2)
from .cache_croma import llamar_con_cache
from .casos import contrato_ya_conocido, guardar_caso
from .suscripciones import listar_suscriptores
from .tiempo import inicio_de_dia_bogota_en_utc

log = logging.getLogger(__name__)

# La fecha de apertura de la ventana la fija B1 junto con los NITs, para que no
# haya dos versiones de "desde cuando" en el repo.
FECHA_APERTURA_VENTANA = FECHA_APERTURA

HERRAMIENTA_PROCESOS = "secop_processes_by_entity"


def _procesos_de(datos: Any) -> list[dict[str, Any]]:
    """Saca `processes[]` de la respuesta, tolerando que Croma no encuentre nada.

    `found: false` es un dato legitimo (la entidad no tiene procesos), no un
    error: se traduce a lista vacia.
    """
    if isinstance(datos, dict):
        procesos = datos.get("processes")
        if isinstance(procesos, list):
            return [p for p in procesos if isinstance(p, dict)]
        return []
    if isinstance(datos, list):
        return [p for p in datos if isinstance(p, dict)]
    return []


def _llave_de_novedad(proceso: dict[str, Any]) -> str | None:
    """El identificador real que devuelve Croma, no uno inventado.

    Procesos traen `notice_uid`; si alguna vez llega un contrato por este
    camino, trae `contract_id`. Cualquier otra cosa se descarta con registro en
    vez de fabricar una llave.
    """
    for campo in ("notice_uid", "contract_id"):
        valor = proceso.get(campo)
        if valor:
            return str(valor).strip()
    return None


def _mas_reciente(procesos: list[dict[str, Any]]) -> dict[str, Any] | None:
    """El proceso publicado mas tarde. Es el que representa la actividad nueva."""
    con_fecha = [p for p in procesos if p.get("published_date")]
    if con_fecha:
        return max(con_fecha, key=lambda p: str(p.get("published_date")))
    return procesos[0] if procesos else None


async def _procesos_de_entidad(
    croma: CromaClient, nit_entidad: str, desde: date
) -> list[dict[str, Any]]:
    """Procesos de una entidad publicados desde `desde`.

    La fecha se ancla al inicio del dia en hora de Bogota antes de convertirla,
    para que "desde el 11 de agosto" signifique el mismo instante corra donde
    corra el proceso (Render va en UTC).
    """
    desde_utc = inicio_de_dia_bogota_en_utc(desde)

    datos, _consultado_en = await llamar_con_cache(
        croma,
        HERRAMIENTA_PROCESOS,
        {
            "document_number": nit_entidad,
            "from_date": desde_utc.date().isoformat(),
            "page": 1,
        },
    )
    return _procesos_de(datos)


async def _avisar_si_corresponde(caso: Caso) -> None:
    if caso.nivel_atencion not in (NivelAtencion.MEDIO, NivelAtencion.ALTO):
        return

    for telefono in listar_suscriptores(caso.municipio, caso.departamento):
        try:
            await enviar_alerta(caso, telefono)
        except Exception:  # noqa: BLE001 - una alerta fallida no debe tumbar el barrido completo
            log.exception(
                "No se pudo enviar la alerta a %s para el caso %s", telefono, caso.id
            )


async def monitor_nuevos(desde: date | None = None) -> list[Caso]:
    """Barrido completo: entidades afectadas -> filtro de novedad -> Caso armado.

    Devuelve solo los casos NUEVOS de esta corrida, no el historico.
    """
    if not get_settings().croma_configurado:
        raise CromaSinRespuesta(
            "CROMA_API_KEY está vacía. Copia .env.example a .env y pega el valor "
            "del chat privado antes de correr el monitor."
        )

    fecha_min = desde or FECHA_APERTURA_VENTANA
    tope = get_settings().lumen_monitor_max_casos
    casos: list[Caso] = []

    async with CromaClient() as croma:
        for entidad in ENTIDADES_EMERGENCIA:
            if len(casos) >= tope:
                log.info("Tope de %s casos alcanzado; se corta el barrido.", tope)
                break

            nit = entidad["nit"]
            nombre = entidad["nombre"]

            procesos = await _procesos_de_entidad(croma, nit, fecha_min)
            if not procesos:
                log.info("%s (%s): sin procesos desde %s", nombre, nit, fecha_min)
                continue

            reciente = _mas_reciente(procesos)
            llave = _llave_de_novedad(reciente) if reciente else None
            if not llave:
                log.warning(
                    "%s (%s): %s procesos pero ninguno trae notice_uid ni "
                    "contract_id; no se puede seguir la novedad, se omite.",
                    nombre,
                    nit,
                    len(procesos),
                )
                continue

            if contrato_ya_conocido(llave):
                log.info("%s (%s): sin actividad nueva (%s ya visto)", nombre, nit, llave)
                continue

            try:
                caso = await analizar(AnalizarRequest(entidad_id=nit))
            except HTTPException as err:
                log.warning(
                    "El motor no pudo analizar %s (%s): %s %s",
                    nombre,
                    nit,
                    err.status_code,
                    err.detail,
                )
                continue

            guardar_caso(caso, contrato_id=llave)
            casos.append(caso)
            log.info(
                "%s (%s): caso %s con %s señales, nivel %s",
                nombre,
                nit,
                caso.id,
                len(caso.senales),
                caso.nivel_atencion.value,
            )
            await _avisar_si_corresponde(caso)

    return casos
