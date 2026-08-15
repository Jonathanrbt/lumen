"""Endpoints de IA. Dueno: Freddy (B2).

Nadie mas edita este archivo. Si necesitas algo de aqui, pidelo por el chat.

Aqui vive lo que gana los 25 puntos de "uso real de IA": `/justificacion` es el
lector que evalua una justificacion de urgencia manifiesta contra el estandar que
la ley exige. Es analisis semantico de documento no estructurado; no hay regla SQL
que lo haga.
"""

from __future__ import annotations

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

router = APIRouter(tags=["IA · B2 Freddy"])


@router.post("/resolver", response_model=list[Candidato])
async def resolver(peticion: ResolverRequest) -> list[Candidato]:
    """Traduce lenguaje natural a entidades concretas. Sin pedir un NIT.

    Devuelve candidatos para que la persona desambigüe. **Nunca se asume cuál es.**
    Si el texto cae en el catálogo curado, resuelve directo.
    """
    raise HTTPException(status_code=501, detail="Pendiente: B2 (Freddy). Resolución de entidades.")


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
    raise HTTPException(
        status_code=501, detail="Pendiente: B2 (Freddy). Lector de justificaciones."
    )


@router.post("/accion", response_model=Artefacto)
async def accion(peticion: AccionRequest) -> Artefacto:
    """Convierte un hallazgo en algo que se puede enviar.

    Prioridad: el derecho de petición primero, que es el que sale en el video.
    Redactado a partir del hallazgo específico, con hechos numerados y norma
    citada. No es una plantilla con huecos.
    """
    raise HTTPException(status_code=501, detail="Pendiente: B2 (Freddy). Generador de artefactos.")


@router.post("/chat", response_model=ChatResponse)
async def chat(peticion: ChatRequest) -> ChatResponse:
    """La única ruta exclusiva del Modo Vigilancia.

    Por dentro orquesta `/resolver` y `/analizar`. **No es un motor aparte.**

    Reglas del agente, no negociables: desambiguar antes de analizar, narrar en
    lenguaje ciudadano, cada afirmación con su fuente, siempre ofrecer el
    siguiente paso, jamás decir "corrupto" o "ilegal", y saber decir "no sé".
    """
    raise HTTPException(status_code=501, detail="Pendiente: B2 (Freddy). Agente conversacional.")
