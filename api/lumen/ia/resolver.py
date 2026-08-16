"""Resolucion de entidades: `POST /resolver`. Dueno: Freddy (B2).

Traduce lenguaje natural a `Candidato[]` sin asumir cual es (§CONTRATO-API.md:
"nunca se asume cual es"). Dos caminos, en ese orden, para gastar el LLM solo
cuando hace falta:

1. **Camino barato.** El texto puede que YA sea un nombre (el caso mas comun:
   "Conalvías", "Odinsa"). Se manda tal cual a RUES (`rues_entities_by_name`).
   Cero llamadas al LLM.
2. **Camino con LLM.** Si el camino barato no encuentra nada -- porque Croma
   rechaza el texto o porque la busqueda literal no da resultados -- se usa
   `Modelo.RAPIDO` para extraer el nombre real de la pregunta libre
   ("¿la alcaldía de mi pueblo tiene algo raro?" no tiene nombre que buscar;
   "el metro de Bogotá" sí). Si el modelo tampoco encuentra un nombre
   concreto, se devuelve lista vacía: no se inventa.

**Hallazgo en vivo (16.ago, llamando a la API real, no asumido):** RUES
rechaza con HTTP 400 cualquier caracter fuera de letras, numeros, espacios y
`.,'&-()/+`. Una pregunta con "¿" o "?" nunca pasa el camino barato.

**Tipo de actor:** RUES es sobre todo un registro mercantil, asi que casi
todo lo que devuelve es empresa. No hay una ruta de Croma que diga "esto es
una entidad publica" de forma directa, asi que `_tipo_desde_rues` es una
heuristica sobre el texto de `legal_organization`/`category`, documentada
como tal -- no una certeza.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from ..contracts import Candidato, TipoActor
from ..croma.client import CromaClient, CromaError
from .llm_client import CursorAgentError, LLMEjecucionError, Modelo, preguntar

log = logging.getLogger(__name__)

MAX_CANDIDATOS = 5

# El mismo charset que RUES acepta (confirmado contra la API real): letras
# (incluidas tildes y ñ), numeros, espacios y . , ' & - ( ) / +
_CARACTERES_VALIDOS = re.compile(r"^[\w\sÁÉÍÓÚÑáéíóúñ.,'&\-()/+]{3,200}$", re.UNICODE)

_PROMPT_EXTRACCION = """Un ciudadano colombiano escribio este texto buscando informacion sobre una \
empresa, proveedor o entidad publica:

"{texto}"

Extrae SOLO el nombre propio que hay que buscar en el registro mercantil (RUES). Reglas estrictas:
- Responde con el nombre limpio, nada mas: sin signos de interrogacion, sin el resto de la pregunta.
- Usa solo letras, numeros, espacios y . , ' & - ( ) / +
- Si el texto NO menciona un nombre concreto de empresa, persona o entidad (por ejemplo "mi pueblo", \
"una empresa cualquiera", "el municipio" sin nombre propio), responde exactamente: NINGUNO
- Una sola linea, sin explicacion.
"""


def _texto_valido_para_rues(texto: str) -> bool:
    return bool(_CARACTERES_VALIDOS.match(texto.strip()))


async def _extraer_nombre(texto: str) -> str | None:
    """`/resolver` es de cara al ciudadano: si el LLM no arranca (config, red)
    o corre y falla, esto se degrada a "no hay nombre" en vez de tumbar el
    endpoint con un 500. El camino barato ya cubre el caso comun sin LLM."""
    try:
        respuesta = await preguntar(_PROMPT_EXTRACCION.format(texto=texto), Modelo.RAPIDO)
    except (CursorAgentError, LLMEjecucionError):
        log.exception("El extractor de nombres para /resolver falló con texto=%r", texto)
        return None

    nombre = respuesta.strip()
    if not nombre or nombre.upper() == "NINGUNO":
        return None
    if not _texto_valido_para_rues(nombre):
        log.warning("El modelo devolvió un nombre no válido para RUES: %r", nombre)
        return None
    return nombre


def _tipo_desde_rues(entidad: dict[str, Any]) -> TipoActor:
    organizacion = (entidad.get("legal_organization") or "").upper()
    categoria = (entidad.get("category") or "").upper()
    if "PERSONA NATURAL" in organizacion:
        return TipoActor.PERSONA
    if "ADMINISTRACION PUBLICA" in organizacion or "ADMINISTRACION PUBLICA" in categoria:
        return TipoActor.ENTIDAD
    return TipoActor.EMPRESA


def _actividad_legible(detalle: dict[str, Any]) -> str | None:
    actividad = detalle.get("primary_activity") or {}
    codigo, descripcion = actividad.get("code"), actividad.get("description")
    if codigo and descripcion:
        return f"{codigo} - {descripcion}"
    return descripcion or None


def _candidato_desde_rues(entidad: dict[str, Any]) -> Candidato | None:
    nombre = entidad.get("name")
    if not nombre:
        return None
    detalle = entidad.get("detail") or {}
    # commercial_municipality suele venir vacio en la practica; chamber_name
    # (la camara de comercio, ej. "CALI") es la mejor aproximacion que queda.
    ciudad = detalle.get("commercial_municipality") or entidad.get("chamber_name")
    return Candidato(
        nombre=nombre,
        nit=entidad.get("nit"),
        ciudad=ciudad,
        actividad=_actividad_legible(detalle),
        tipo=_tipo_desde_rues(entidad),
    )


def _candidatos_desde_respuesta(datos: Any) -> list[Candidato]:
    entidades = datos.get("entities") if isinstance(datos, dict) else None
    if not entidades:
        return []

    # Los que ya traen NIT sirven para seguir directo a /analizar: van primero.
    ordenados = sorted(entidades, key=lambda e: e.get("nit") is None)

    candidatos: list[Candidato] = []
    vistos: set[str] = set()
    for entidad in ordenados:
        candidato = _candidato_desde_rues(entidad)
        if candidato is None or candidato.nombre in vistos:
            continue
        vistos.add(candidato.nombre)
        candidatos.append(candidato)
        if len(candidatos) >= MAX_CANDIDATOS:
            break
    return candidatos


async def _buscar_en_rues(nombre: str) -> list[Candidato]:
    try:
        async with CromaClient() as croma:
            datos = await croma.consultar("rues_entities_by_name", {"name": nombre, "page": 1})
    except CromaError as err:
        log.info("RUES rechazó la búsqueda %r: %s", nombre, err)
        return []
    return _candidatos_desde_respuesta(datos)


async def resolver_candidatos(texto: str) -> list[Candidato]:
    """El texto que escribió la persona, tal cual. Nunca se asume cuál es."""
    texto = texto.strip()
    if not texto:
        return []

    if _texto_valido_para_rues(texto):
        candidatos = await _buscar_en_rues(texto)
        if candidatos:
            return candidatos

    nombre = await _extraer_nombre(texto)
    if not nombre:
        return []
    return await _buscar_en_rues(nombre)
