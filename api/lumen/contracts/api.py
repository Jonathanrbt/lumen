"""Entradas y salidas de los nueve endpoints.

Los objetos del dominio viven en `modelos.py`. Aqui solo estan los sobres: lo que
recibe y lo que devuelve cada ruta. Es lo que Andrew necesita para construir el
frontend sin esperar al backend.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .modelos import Candidato, Caso, TipoArtefacto


class ResolverRequest(BaseModel):
    """POST /resolver — el usuario escribe en lenguaje natural, sin saber que es un NIT."""

    texto: str = Field(
        description="Lo que la persona escribio tal cual",
        examples=["¿la alcaldía de mi pueblo tiene algo raro?", "Conalvías", "el metro de Bogotá"],
    )


class AnalizarRequest(BaseModel):
    """POST /analizar — corre el motor. Hay que dar al menos una de las tres llaves."""

    nit: str | None = None
    entidad_id: str | None = None
    contrato_id: str | None = None

    @model_validator(mode="after")
    def al_menos_una_llave(self) -> "AnalizarRequest":
        if not any([self.nit, self.entidad_id, self.contrato_id]):
            raise ValueError(
                "Hay que enviar al menos uno de: nit, entidad_id o contrato_id"
            )
        return self


class JustificacionRequest(BaseModel):
    """POST /justificacion — por URL.

    El PDF tambien se puede subir como multipart; en ese caso no se manda este
    cuerpo. Es la ruta que sirve donde todavia no hay datos abiertos: alguien
    fotografia o descarga el documento que vio en su municipio.
    """

    url: str = Field(description="Enlace al PDF de la justificación de urgencia manifiesta")


class AccionRequest(BaseModel):
    """POST /accion — convierte un hallazgo en algo que se puede enviar."""

    caso_id: str
    tipo: TipoArtefacto


class AlertaRequest(BaseModel):
    """POST /alerta — dispara el aviso al suscriptor."""

    caso_id: str
    destinatario: str = Field(description="Teléfono en formato E.164, ej. +573001112233")


class AlertaResponse(BaseModel):
    estado: str = Field(description="'enviado', 'omitido' o 'error'")
    detalle: str | None = None


class ChatRequest(BaseModel):
    """POST /chat — la unica ruta exclusiva del Modo Vigilancia.

    Por dentro orquesta /resolver y /analizar. No es un motor aparte.
    """

    mensaje: str
    contexto: dict | None = Field(
        default=None,
        description="Estado de la conversacion: candidato ya elegido, caso en curso, etc.",
    )


class ChatResponse(BaseModel):
    """La respuesta siempre ofrece el siguiente paso. Nunca deja al usuario sin salida."""

    narracion: str
    caso: Caso | None = None
    candidatos: list[Candidato] | None = Field(
        default=None,
        description="Si vienen candidatos, el frontend los muestra como tarjetas y la persona elige. Nunca se asume",
    )
    siguientes_pasos: list[str] = Field(
        default_factory=list,
        examples=[["Ver la red de actores", "Generar el derecho de petición"]],
    )


class HealthResponse(BaseModel):
    estado: str
    servicio: str = "lumen-api"
    entorno: str
    version: str


class HealthCromaResponse(BaseModel):
    """Comprueba que el token de Croma de QUIEN corre esto funciona de verdad.

    Hace una llamada real al servidor, no un ping. Es el primer verde que tienen
    que ver los cuatro en el bloque de arranque.
    """

    estado: str
    servidor: str | None = None
    herramientas_disponibles: int | None = None
    detalle: str | None = None
