"""Envio de alertas por WhatsApp via Twilio sandbox. Dueno: Cristian (B3).

Prioridad 1 del bloque de las 20:45 (docs/handoff/CRISTIAN-B3.md). Timebox de
60 minutos, corte a las 21:45: si a esa hora no llego un mensaje real a un
telefono real, se corta y se avisa a Jonatin de inmediato.

El copy es de fuente unica: `docs/COPY-SENALES.md`. Este modulo NO redacta
señales nuevas — reusa `Senal.regla_legible`, que Jonatin (B1) ya escribe en
ese lenguaje. Si los cuatro maquillan el mismo texto, el veedor lee cuatro
voces distintas.

Regla que no se negocia: nunca se simula un envio. Si Twilio no esta
configurado o falla, el estado es 'error', jamas 'enviado'.
"""

from __future__ import annotations

import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from ..config import get_settings
from ..contracts import Caso, NivelAtencion

log = logging.getLogger(__name__)

MAX_LINEAS = 5


def _formatear_pesos(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def _url_ficha(caso: Caso) -> str:
    ajustes = get_settings()
    if ajustes.lumen_frontend_url:
        return f"{ajustes.lumen_frontend_url.rstrip('/')}/caso/{caso.id}"
    # Andrew todavia no declara su dominio: se enlaza al recurso de la API.
    return f"Ver evidencia: pide el caso {caso.id} en la API (dominio del frontend pendiente)"


def _armar_mensaje(caso: Caso) -> str:
    """Maximo 5 lineas, con el copy exacto que ya trae cada Senal.

    No usa una tabla propia de frases: `regla_legible` de cada `Senal` ES el
    copy de `docs/COPY-SENALES.md`, porque Jonatin (B1) lo escribe ahi.
    """
    encabezado = f"Nuevo contrato en {caso.municipio or caso.entidad}"
    if caso.valor:
        encabezado += f" por {_formatear_pesos(caso.valor)}"
    lineas = [encabezado + "."]

    for senal in caso.senales[:2]:  # deja espacio para disclaimer + enlace en 5 lineas
        lineas.append(senal.regla_legible)

    lineas.append(caso.disclaimer)
    lineas.append(_url_ficha(caso))

    return "\n".join(lineas[:MAX_LINEAS])


async def enviar_alerta(caso: Caso, destinatario: str) -> tuple[str, str | None]:
    """Intenta el envio real. Devuelve `(estado, detalle)`.

    `estado` es 'enviado', 'omitido' o 'error' — nunca fabricado (spec
    `plataforma/alertas-whatsapp`, requerimiento "Envío real, nunca simulado").
    """
    if caso.nivel_atencion == NivelAtencion.BAJO:
        return "omitido", "Nivel de atención bajo: no amerita alertar."

    ajustes = get_settings()
    if not (ajustes.twilio_account_sid and ajustes.twilio_auth_token and ajustes.twilio_whatsapp_from):
        return "error", "Twilio no está configurado (faltan TWILIO_* en el entorno)."

    mensaje = _armar_mensaje(caso)

    try:
        cliente = Client(ajustes.twilio_account_sid, ajustes.twilio_auth_token)
        cliente.messages.create(
            from_=f"whatsapp:{ajustes.twilio_whatsapp_from}",
            to=f"whatsapp:{destinatario}",
            body=mensaje,
        )
    except TwilioRestException as err:
        log.error("Twilio rechazó el envío a %s: %s", destinatario, err)
        return "error", f"Twilio rechazó el envío: {err.msg}"
    except Exception as err:  # noqa: BLE001 - preferimos el detalle en la respuesta a un 500 ciego
        log.error("Fallo inesperado enviando WhatsApp a %s: %s", destinatario, err)
        return "error", f"{type(err).__name__}: {err}"

    return "enviado", "Mensaje entregado al suscriptor."
