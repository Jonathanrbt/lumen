"""Lector de justificaciones de urgencia manifiesta: `POST /justificacion`.
Dueno: Freddy (B2). **El núcleo del producto** — la feature que gana los 25
puntos de "uso real de IA": análisis semántico de un documento no
estructurado, no una regla SQL.

La norma (Ley 1523 art. 65, Decreto 1082 de 2015) exige que la contratación
bajo urgencia manifiesta tenga: (1) relación directa y verificable con los
hechos de la emergencia, (2) que la necesidad haya surgido a raíz de esos
hechos y no que ya existiera, (3) diagnóstico o estudio técnico que la
respalde. Por eso el lector **no** le pide al modelo que invente preguntas:
siempre hace las mismas tres, formuladas como se las harías a una persona
(fuente de verdad: `fixtures/lectura.json`). Un rubric fijo es más confiable
y más fácil de auditar que "que el modelo decida qué preguntar".

**El guardarraíl que no se negocia va dos veces:** se lo pide el prompt, y
además el código verifica que cada `cita_textual` sea un fragmento real del
documento (no una alucinación) antes de aceptarla. Si no aparece en el
texto, se descarta y el punto pasa a `no_concluye_por`. Y el veredicto
`solida` es imposible en código si algún punto quedó sin cita — no depende
de que el modelo lo recuerde.
"""

from __future__ import annotations

import io
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from pypdf import PdfReader

from ..contracts import Lectura, PuntoLectura, Veredicto
from .llm_client import LLMEjecucionError, Modelo, preguntar

log = logging.getLogger(__name__)

PREGUNTAS = [
    "¿Lo que se está comprando tiene que ver con los daños o hechos que causaron la emergencia?",
    "¿Esta necesidad apareció después del hecho que originó la emergencia, o ya venía de antes?",
    "¿Hay estudios técnicos o diagnósticos que respalden que esto era urgente?",
]

# ~15k tokens. El lector hace pocas llamadas (es la feature "cara" a propósito
# solo en eso), pero no hace falta mandar un documento entero de 300 paginas.
MAX_CARACTERES_DOCUMENTO = 60_000


class DocumentoIlegible(RuntimeError):
    """El PDF no trajo texto extraíble (escaneo sin OCR, corrupto, vacío)."""


async def descargar_pdf(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as cliente:
        resp = await cliente.get(url)
        resp.raise_for_status()
        return resp.content


def _texto_por_pagina(contenido_pdf: bytes) -> list[str]:
    try:
        lector = PdfReader(io.BytesIO(contenido_pdf))
        paginas = [(pagina.extract_text() or "").strip() for pagina in lector.pages]
    except Exception as err:  # noqa: BLE001 - cualquier PDF corrupto cae aqui
        raise DocumentoIlegible(f"No se pudo leer el PDF: {type(err).__name__}: {err}") from err

    if not any(paginas):
        raise DocumentoIlegible("El PDF no trajo texto extraíble. Puede ser un escaneo sin OCR.")
    return paginas


def _documento_para_prompt(paginas: list[str]) -> str:
    bloques: list[str] = []
    total = 0
    for i, texto in enumerate(paginas, start=1):
        if not texto:
            continue
        bloque = f"--- Página {i} ---\n{texto}"
        if total + len(bloque) > MAX_CARACTERES_DOCUMENTO:
            break
        bloques.append(bloque)
        total += len(bloque)
    return "\n\n".join(bloques)


_PROMPT = """Eres un lector que evalúa si un documento de "urgencia manifiesta" de una entidad \
pública colombiana cumple con lo que exige la ley: que la contratación tenga relación directa y \
verificable con los hechos de la emergencia, que la necesidad haya surgido a raíz de esos hechos \
(no que ya existiera antes), y que haya un diagnóstico o estudio técnico que respalde la urgencia.

Documento (con números de página marcados):

{documento}

Contesta EXACTAMENTE estas tres preguntas, en este orden, sobre el documento de arriba:

1. {p1}
2. {p2}
3. {p3}

Reglas estrictas, no negociables:
- Cada respuesta necesita una CITA TEXTUAL literal del documento (copiada tal cual, sin \
parafrasear) que la respalde, y el número de página de donde salió.
- Si el documento NO tiene ningún fragmento que respalde la respuesta a una pregunta, NO \
inventes ni parafrasees una cita. En ese caso deja "cita_textual" en null, "pagina" en null, y \
llena "no_concluye_por" explicando en una frase por qué no se puede concluir.
- El "hallazgo" es una frase corta en lenguaje que cualquier persona entiende, no jerga legal.
- Al final, da un "veredicto" general: "solida" si las tres preguntas tienen citas claras y \
directas que conectan el gasto con la emergencia; "generica" si hay alguna relación pero es \
débil, boilerplate, o falta alguno de los tres elementos; "sin_relacion" si el objeto de la \
compra no tiene relación aparente con el hecho que originó la emergencia.

Responde SOLO con un JSON válido, sin texto antes ni después ni bloques de código, con esta \
forma exacta:

{{
  "veredicto": "solida" | "generica" | "sin_relacion",
  "puntos": [
    {{"hallazgo": "...", "cita_textual": "..." o null, "pagina": N o null, "no_concluye_por": \
"..." o null}},
    {{"hallazgo": "...", "cita_textual": "..." o null, "pagina": N o null, "no_concluye_por": \
"..." o null}},
    {{"hallazgo": "...", "cita_textual": "..." o null, "pagina": N o null, "no_concluye_por": \
"..." o null}}
  ]
}}
"""


def _extraer_json(texto: str) -> dict[str, Any]:
    texto = texto.strip()
    # El modelo a veces envuelve el JSON en ```json ... ``` pese a la instrucción.
    coincidencia = re.search(r"\{.*\}", texto, re.DOTALL)
    if not coincidencia:
        raise LLMEjecucionError(f"El lector no devolvió JSON: {texto[:200]!r}")
    try:
        return json.loads(coincidencia.group(0))
    except json.JSONDecodeError as err:
        raise LLMEjecucionError(f"El lector devolvió JSON inválido: {err}") from err


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip().lower()


def _cita_es_real(cita: str, texto_documento: str) -> bool:
    """Anti-alucinación: la cita tiene que ser un fragmento real del
    documento, no algo que el modelo se inventó parecido al texto."""
    return _normalizar(cita) in _normalizar(texto_documento)


def _construir_puntos(crudo: list[dict[str, Any]], texto_documento: str) -> list[PuntoLectura]:
    """Siempre exactamente 3 puntos, con el texto canónico de PREGUNTAS —
    nunca lo que el modelo haya (o no) devuelto en `pregunta`. Si el modelo
    devolvió menos de 3 items o algo raro, los que faltan quedan como
    'no se pudo concluir', no se inventa una respuesta."""
    puntos = []
    for i, pregunta in enumerate(PREGUNTAS):
        item = crudo[i] if i < len(crudo) and isinstance(crudo[i], dict) else {}
        cita = item.get("cita_textual")
        no_concluye = item.get("no_concluye_por")

        if cita and not _cita_es_real(str(cita), texto_documento):
            log.warning("Cita descartada por no aparecer en el documento: %r", str(cita)[:120])
            cita = None
            no_concluye = (
                "La cita que propuso el modelo no coincide con el texto del documento; "
                "se descarta por no poder verificarse."
            )
        if not cita and not no_concluye:
            no_concluye = "El modelo no respondió esta pregunta."

        puntos.append(
            PuntoLectura(
                pregunta=pregunta,
                hallazgo=item.get("hallazgo") or "No fue posible determinarlo.",
                cita_textual=cita if cita else None,
                pagina=item.get("pagina") if cita else None,
                no_concluye_por=no_concluye if not cita else None,
            )
        )
    return puntos


def _veredicto_final(propuesto: Any, puntos: list[PuntoLectura]) -> Veredicto:
    """Guardarraíl en el código, no solo en el prompt: 'solida' es imposible
    si algún punto quedó sin cita — 'solida' significa que las tres
    preguntas tienen respaldo verificable, por definición."""
    try:
        veredicto = Veredicto(propuesto)
    except ValueError:
        veredicto = Veredicto.GENERICA

    algun_punto_sin_cita = any(p.cita_textual is None for p in puntos)
    if veredicto == Veredicto.SOLIDA and algun_punto_sin_cita:
        return Veredicto.GENERICA
    return veredicto


async def leer_justificacion(contenido_pdf: bytes, documento_url: str | None = None) -> Lectura:
    paginas = _texto_por_pagina(contenido_pdf)
    texto_documento = "\n".join(paginas)

    prompt = _PROMPT.format(
        documento=_documento_para_prompt(paginas),
        p1=PREGUNTAS[0],
        p2=PREGUNTAS[1],
        p3=PREGUNTAS[2],
    )

    respuesta = await preguntar(prompt, Modelo.FUERTE)
    crudo = _extraer_json(respuesta)

    puntos = _construir_puntos(crudo.get("puntos", []), texto_documento)
    veredicto = _veredicto_final(crudo.get("veredicto"), puntos)

    return Lectura(
        veredicto=veredicto,
        puntos=puntos,
        documento_url=documento_url,
        analizado_en=datetime.now(timezone.utc),
    )


async def leer_justificacion_desde_url(url: str) -> Lectura:
    contenido = await descargar_pdf(url)
    return await leer_justificacion(contenido, documento_url=url)
