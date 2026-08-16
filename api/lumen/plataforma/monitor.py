"""Monitor de Modo Emergencia. Dueno: Cristian (B3).

Camina los pasos 1-2 y 7-9 del Flujo A (docs/brief-final-claude.md §4.6):
encuentra contratos nuevos con causal de urgencia, descarta lo que ya esta en
base, arma el Caso llamando al motor de Jonatin (B1) y dispara alertas si el
nivel de atencion lo amerita.

Los pasos 3-6 (enriquecimiento, las 8 señales, el lector de IA, el nivel de
atencion) son `POST /analizar`, de Jonatin — este modulo lo invoca, no lo
reimplementa. Si `/analizar` todavia responde 501 (no implementado), el
contrato se salta con una advertencia: el monitor no se cae por eso, y no hace
falta coordinar el orden exacto en que B1 y B3 terminan su parte.
"""

from __future__ import annotations

import logging
from datetime import date

from fastapi import HTTPException

from ..config import get_settings
from ..contracts import AnalizarRequest, Caso, NivelAtencion
from ..croma.client import CromaClient, CromaSinRespuesta
from ..routers.analisis import analizar
from .cache_croma import llamar_con_cache
from .casos import contrato_ya_conocido, guardar_caso
from .suscripciones import listar_suscriptores
from .tiempo import inicio_de_dia_bogota_en_utc
from ..whatsapp import enviar_alerta  # cliente real: api/lumen/whatsapp/, dueno Freddy (B2)

log = logging.getLogger(__name__)

FECHA_APERTURA_VENTANA = date(2026, 8, 11)

# TODO(Jonatin/B1): esto NO es una ruta real. Confirmado tras el cliente HTTP
# de Croma (api/lumen/croma/client.py, 22:30): su diccionario RUTAS solo
# expone consultas puntuales por entidad/proveedor/NIT (rues_entity_by_nit,
# secop_processes_by_entity, secop_contracts_by_provider, secop_process,
# secop_contract...), ninguna que liste "todos los contratos nuevos por
# departamento y causal de urgencia desde una fecha". Ese barrido amplio
# puede no existir en Croma en absoluto — es la verificacion de las 3 capas
# de datos de §6 del brief, que le toca a B1. Si no existe, el monitor
# probablemente tiene que recorrer una lista de entidades conocidas con
# `secop_processes_by_entity` en vez de un barrido global; eso lo decide
# quien tenga el mapa de entidades afectadas.
HERRAMIENTA_CONTRATOS_URGENCIA = "secop_contracts_by_urgency"  # placeholder, ver arriba

# TODO(Jonatin/B1): completar con los departamentos afectados que B1 valida en
# su bloque de las 17:30-18:15 (§6 del brief). Vacio a proposito: no
# inventamos una lista de departamentos sin fuente.
DEPARTAMENTOS_AFECTADOS: list[str] = []


async def _buscar_contratos_nuevos(desde: date) -> list[dict]:
    """Pide a Croma los contratos con causal de urgencia desde `desde`.

    La fecha se ancla al inicio del dia en hora de Bogota (UTC-5) antes de
    convertirla a UTC, para que "desde el 11 de agosto" signifique el mismo
    instante sin importar que el proceso corra en Render (UTC) o en una
    maquina del equipo.
    """
    if not get_settings().croma_configurado:
        raise CromaSinRespuesta(
            "CROMA_API_KEY está vacía. Copia .env.example a .env y pega el valor "
            "del chat privado antes de correr el monitor."
        )

    desde_utc = inicio_de_dia_bogota_en_utc(desde)

    async with CromaClient() as croma:
        contratos, _consultado_en = await llamar_con_cache(
            croma,
            HERRAMIENTA_CONTRATOS_URGENCIA,
            {
                "departamentos": DEPARTAMENTOS_AFECTADOS,
                "desde": desde_utc.date().isoformat(),
            },
        )
    return contratos if isinstance(contratos, list) else []


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
    """Barrido completo: contratos nuevos -> filtro de novedad -> Caso armado.

    Devuelve solo los casos NUEVOS de esta corrida (spec
    `plataforma/monitor-emergencia`), no el historico completo.
    """
    fecha_min = desde or FECHA_APERTURA_VENTANA
    contratos = await _buscar_contratos_nuevos(fecha_min)

    casos: list[Caso] = []
    for contrato in contratos:
        contrato_id = contrato.get("id") or contrato.get("contrato_id") or contrato.get("numero_contrato")
        if not contrato_id or contrato_ya_conocido(contrato_id):
            continue

        try:
            caso = await analizar(AnalizarRequest(contrato_id=contrato_id))
        except HTTPException as err:
            if err.status_code == 501:
                log.warning(
                    "El motor de señales (Jonatin/B1) aún no está implementado; "
                    "se salta el contrato %s hasta que /analizar exista.",
                    contrato_id,
                )
                continue
            raise

        guardar_caso(caso, contrato_id=contrato_id)
        casos.append(caso)
        await _avisar_si_corresponde(caso)

    return casos
