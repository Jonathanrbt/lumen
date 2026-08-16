"""Endpoints de IA. Dueno: Freddy (B2).

Nadie mas edita este archivo. Si necesitas algo de aqui, pidelo por el chat.

Aqui vive lo que gana los 25 puntos de "uso real de IA": `/justificacion` es el
lector que evalua una justificacion de urgencia manifiesta contra el estandar que
la ley exige. Es analisis semantico de documento no estructurado; no hay regla SQL
que lo haga.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..contracts import (
    AccionRequest,
    Artefacto,
    Candidato,
    ChatRequest,
    ChatResponse,
    Lectura,
    ResolverRequest,
)
from ..ia.artefactos import generar_artefacto
from ..ia.lector import (
    DocumentoIlegible,
    leer_justificacion,
    leer_justificacion_desde_url,
)
from ..ia.llm_client import CursorAgentError, LLMEjecucionError
from ..ia.resolver import resolver_candidatos
from ..plataforma.casos import obtener_caso
from ..plataforma.supabase_client import SupabaseNoConfigurado

router = APIRouter(tags=["IA · B2 Freddy"])


@router.post("/resolver", response_model=list[Candidato])
async def resolver(peticion: ResolverRequest) -> list[Candidato]:
    """Traduce lenguaje natural a entidades concretas. Sin pedir un NIT.

    Devuelve candidatos para que la persona desambigüe. **Nunca se asume cuál es.**
    Camino barato primero (el texto ya es un nombre, va directo a RUES); si no
    encuentra nada, `Modelo.RAPIDO` extrae el nombre de la pregunta libre.
    """
    return await resolver_candidatos(peticion.texto)


@router.post("/justificacion", response_model=Lectura)
async def justificacion(
    archivo: UploadFile | None = File(default=None),
    url: str | None = Form(default=None),
) -> Lectura:
    """Lee la justificación de urgencia manifiesta y emite un veredicto.

    La norma exige que la contratación bajo urgencia tenga relación directa y
    verificable con los hechos de la emergencia, precedida de diagnósticos
    técnicos. Esto evalúa si la tiene.

    Cada punto del veredicto va con su cita textual. **Si no puede citar, no
    afirma:** llena `no_concluye_por` y deja la cita vacía.
    """
    if archivo is None and not url:
        raise HTTPException(status_code=422, detail="Manda 'archivo' (PDF) o 'url'.")

    try:
        if archivo is not None:
            contenido = await archivo.read()
            return await leer_justificacion(contenido, documento_url=None)
        return await leer_justificacion_desde_url(url)  # type: ignore[arg-type]
    except DocumentoIlegible as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    except httpx.HTTPError as err:
        raise HTTPException(status_code=502, detail=f"No se pudo descargar el PDF: {err}") from err
    except (CursorAgentError, LLMEjecucionError) as err:
        raise HTTPException(
            status_code=503, detail=f"El lector no pudo completarse: {err}"
        ) from err


@router.post("/accion", response_model=Artefacto)
async def accion(peticion: AccionRequest) -> Artefacto:
    """Convierte un hallazgo en algo que se puede enviar.

    Prioridad: el derecho de petición primero, que es el que sale en el video.
    Redactado a partir del hallazgo específico, con hechos numerados y norma
    citada. No es una plantilla con huecos.
    """
    try:
        caso = obtener_caso(peticion.caso_id)
    except SupabaseNoConfigurado as err:
        raise HTTPException(status_code=503, detail=str(err)) from err

    if caso is None:
        raise HTTPException(
            status_code=404, detail=f"No existe un caso con id '{peticion.caso_id}'."
        )

    try:
        return await generar_artefacto(caso, peticion.tipo)
    except (CursorAgentError, LLMEjecucionError) as err:
        raise HTTPException(
            status_code=503, detail=f"El generador de artefactos no pudo completarse: {err}"
        ) from err


@router.post("/chat", response_model=ChatResponse)
async def chat(peticion: ChatRequest) -> ChatResponse:
    """La única ruta exclusiva del Modo Vigilancia.

    Por dentro orquesta `/resolver` y `/analizar`. **No es un motor aparte.**

    Reglas del agente, no negociables: desambiguar antes de analizar, narrar en
    lenguaje ciudadano, cada afirmación con su fuente, siempre ofrecer el
    siguiente paso, jamás decir "corrupto" o "ilegal", y saber decir "no sé".
    """
    raise HTTPException(status_code=501, detail="Pendiente: B2 (Freddy). Agente conversacional.")
