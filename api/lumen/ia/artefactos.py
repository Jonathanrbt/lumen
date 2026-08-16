"""Generador de artefactos: `POST /accion`. Dueno: Freddy (B2).

"La brecha que nadie más cubre. Sin esto, una alerta es solo una alerta."

**Prioridad: `derecho_peticion`**, el que sale en el video, redactado por el
LLM a partir del hallazgo específico de cada caso — no es una plantilla con
huecos. Pero el disclaimer legal y la firma van **fijos en el código**, no
dependen de que el modelo se acuerde de escribirlos, mismo principio que el
`DISCLAIMER` de `contracts/modelos.py`.

Los otros tres tipos (`paquete_evidencia`, `informe_veeduria`,
`guia_denuncia`) son estructurales, no narrativos: listan lo que el caso ya
trae (señales, fuentes, lectura). Se arman con plantillas en Python, sin
LLM — cero riesgo de alucinación para algo que es, en el fondo, un formateo
de datos que ya existen.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from ..contracts import Artefacto, Caso, TipoArtefacto
from .llm_client import LLMEjecucionError, Modelo, preguntar

log = logging.getLogger(__name__)

# El disclaimer legal de la carta. Fijo en código, igual que DISCLAIMER en
# contracts/modelos.py: la seguridad juridica de la carta no puede depender
# de que el modelo se acuerde de escribirla en cada corrida.
DISCLAIMER_CARTA = (
    "Esta solicitud no imputa irregularidad alguna. Su propósito es ejercer el "
    "control social sobre el uso de recursos públicos."
)

FIRMA = (
    "Atentamente,\n\n_________________________\n"
    "[Nombre y documento del peticionario]\n[Dirección de notificación]\n"
)

NORMAS_BASE_DERECHO_PETICION = [
    "Constitución Política, artículo 23",
    "Ley 1755 de 2015",
    "Ley 80 de 1993, artículos 42 y 43",
]


def _formatear_pesos(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def _hechos_del_caso(caso: Caso) -> list[str]:
    """Los hechos numerados salen del `Caso`, no se le pide al LLM que los
    invente: fecha, valor, proveedor y cada señal con su regla_legible."""
    hechos: list[str] = []
    if caso.fecha and caso.objeto:
        hechos.append(
            f"El {caso.fecha.isoformat()} esa entidad adjudicó un contrato "
            f"cuyo objeto es: {caso.objeto}"
            + (f", por valor de {_formatear_pesos(caso.valor)}." if caso.valor else ".")
        )
    elif caso.objeto:
        hechos.append(f"El objeto del contrato es: {caso.objeto}.")

    if caso.proveedor:
        hechos.append(f"El proveedor adjudicatario fue: {caso.proveedor}.")

    for senal in caso.senales:
        hechos.append(senal.regla_legible)

    if caso.lectura and caso.lectura.veredicto.value == "sin_relacion":
        hechos.append(
            "El documento que explica por qué era urgente no muestra relación con los "
            "hechos de la emergencia."
        )

    return hechos or ["No hay hechos adicionales verificados para este caso."]


def _normas_del_caso(caso: Caso) -> list[str]:
    normas = list(NORMAS_BASE_DERECHO_PETICION)
    if caso.modo.value == "emergencia" or (caso.lectura is not None):
        normas.insert(2, "Ley 1523 de 2012, artículo 46")
    return normas


_PROMPT_DERECHO_PETICION = """Redacta un derecho de petición formal, en español de Colombia, para \
que un ciudadano se lo envíe a una entidad pública. Sigue EXACTAMENTE esta estructura y registro \
(este es el modelo, no lo copies literal, pero imita su formato y tono):

---EJEMPLO---
Señor(a)
**Alcalde(sa) Municipal de ejemplo**
E. S. D.

**Asunto:** Derecho de petición en interés general — solicitud de información sobre \
contratación por urgencia manifiesta.

Respetuosamente, en ejercicio del derecho fundamental de petición consagrado en el artículo 23 \
de la Constitución Política y regulado por la Ley 1755 de 2015, solicito la siguiente \
información:

**Hechos**

1. [hecho numerado]
2. [hecho numerado]

**Peticiones**

1. Copia íntegra del acto administrativo que declaró la urgencia manifiesta y de los estudios \
previos que lo sustentan.
2. [peticiones adicionales según el caso]

**Fundamento**

[Un párrafo corto conectando los hechos con las normas citadas]
---FIN EJEMPLO---

Datos reales de este caso — usa SOLO estos datos, no inventes fechas, cifras ni nombres que no \
estén aquí:

Entidad: {entidad}
Municipio: {municipio}

Hechos verificados (numéralos tal cual, no los cambies ni los completes con datos que no están):
{hechos}

Normas que debes citar en el fundamento: {normas}

Devuelve SOLO un JSON válido, sin texto antes ni después, con esta forma exacta:

{{
  "titulo": "título corto del derecho de petición",
  "salutacion_y_asunto": "el bloque 'Señor(a)... Asunto:...' hasta antes de 'Respetuosamente'",
  "cuerpo": "desde 'Respetuosamente' hasta el final del párrafo de Fundamento, INCLUSIVE, en \
markdown con **Hechos**, **Peticiones** y **Fundamento** como headers. NO incluyas firma ni \
disclaimer, esos van aparte."
}}
"""


async def _generar_derecho_peticion(caso: Caso) -> Artefacto:
    hechos = _hechos_del_caso(caso)
    normas = _normas_del_caso(caso)
    hechos_numerados = "\n".join(f"{i}. {h}" for i, h in enumerate(hechos, start=1))

    prompt = _PROMPT_DERECHO_PETICION.format(
        entidad=caso.entidad,
        municipio=caso.municipio or "(no especificado)",
        hechos=hechos_numerados,
        normas=", ".join(normas),
    )

    respuesta = await preguntar(prompt, Modelo.RAPIDO)
    crudo = _extraer_json(respuesta)

    cuerpo = (
        f"{crudo.get('salutacion_y_asunto', '').strip()}\n\n"
        f"{crudo.get('cuerpo', '').strip()}\n\n"
        f"{DISCLAIMER_CARTA}\n\n"
        f"{FIRMA}"
    )

    return Artefacto(
        tipo=TipoArtefacto.DERECHO_PETICION,
        titulo=crudo.get("titulo") or f"Derecho de petición — {caso.entidad}",
        cuerpo_markdown=cuerpo,
        normas_citadas=normas,
        destinatario=caso.entidad,
        caso_id=caso.id,
    )


def _extraer_json(texto: str) -> dict[str, Any]:
    texto = texto.strip()
    coincidencia = re.search(r"\{.*\}", texto, re.DOTALL)
    if not coincidencia:
        raise LLMEjecucionError(f"El generador de artefactos no devolvió JSON: {texto[:200]!r}")
    try:
        return json.loads(coincidencia.group(0))
    except json.JSONDecodeError as err:
        raise LLMEjecucionError(f"El generador de artefactos devolvió JSON inválido: {err}") from err


def _generar_paquete_evidencia(caso: Caso) -> Artefacto:
    lineas = [f"# Paquete de evidencia — {caso.entidad}", ""]
    if caso.proveedor:
        lineas.append(f"**Proveedor:** {caso.proveedor}  ")
    if caso.valor:
        lineas.append(f"**Valor del contrato:** {_formatear_pesos(caso.valor)}  ")
    if caso.objeto:
        lineas.append(f"**Objeto:** {caso.objeto}  ")
    lineas.append(f"**Nivel de atención:** {caso.nivel_atencion.value}")
    lineas.append("")
    lineas.append("## Señales")
    if not caso.senales:
        lineas.append("Sin señales registradas para este caso.")
    for s in caso.senales:
        lineas.append(f"- **[{s.codigo.value}] {s.nombre}** ({s.nivel.value}): {s.regla_legible}")
        lineas.append(
            f"  Fuente: {s.fuente.herramienta_croma} — {s.fuente.url_oficial} "
            f"(consultado {s.fuente.consultado_en.isoformat()})"
        )
    if caso.lectura:
        lineas.append("")
        lineas.append(f"## Lectura de la justificación — veredicto: {caso.lectura.veredicto.value}")
        for p in caso.lectura.puntos:
            lineas.append(f"- **{p.pregunta}** {p.hallazgo}")
            if p.cita_textual:
                lineas.append(f'  > "{p.cita_textual}"' + (f" (pág. {p.pagina})" if p.pagina else ""))
            elif p.no_concluye_por:
                lineas.append(f"  _No se pudo concluir: {p.no_concluye_por}_")
    lineas.append("")
    lineas.append(f"_{caso.disclaimer}_")

    return Artefacto(
        tipo=TipoArtefacto.PAQUETE_EVIDENCIA,
        titulo=f"Paquete de evidencia — {caso.entidad}",
        cuerpo_markdown="\n".join(lineas),
        normas_citadas=[],
        destinatario=None,
        caso_id=caso.id,
    )


def _generar_informe_veeduria(caso: Caso) -> Artefacto:
    lineas = [f"# Informe de veeduría — {caso.entidad}", ""]
    lineas.append(
        caso.narracion
        or f"Un contrato de {caso.entidad} quedó marcado con nivel de atención "
        f"'{caso.nivel_atencion.value}' por {len(caso.senales)} señal(es) detectadas."
    )
    lineas.append("")
    lineas.append("## Qué se encontró")
    for s in caso.senales:
        lineas.append(f"- {s.regla_legible}")
    lineas.append("")
    lineas.append("## Qué se puede hacer")
    lineas.append(
        "Usar el derecho de petición generado para este caso para pedirle explicaciones "
        "formales a la entidad, y hacer seguimiento a la respuesta dentro de los términos "
        "legales."
    )
    lineas.append("")
    lineas.append(f"_{caso.disclaimer}_")

    return Artefacto(
        tipo=TipoArtefacto.INFORME_VEEDURIA,
        titulo=f"Informe de veeduría — {caso.entidad}",
        cuerpo_markdown="\n".join(lineas),
        normas_citadas=[],
        destinatario=None,
        caso_id=caso.id,
    )


def _generar_guia_denuncia(caso: Caso) -> Artefacto:
    cuerpo = f"""# Guía para denunciar — {caso.entidad}

Si después de mandar el derecho de petición no hay respuesta, o la respuesta no aclara lo que
se preguntó, estos son los canales oficiales para llevar el caso más allá:

## Procuraduría General de la Nación
Investiga a los funcionarios públicos que participaron en la contratación. Denuncia en línea:
https://www.procuraduria.gov.co/

## Contraloría General de la República
Es quien ejerce el control fiscal posterior sobre estos contratos, por norma. Denuncia:
https://www.contraloria.gov.co/

## Fiscalía General de la Nación
Si hay indicios de un delito (no una simple irregularidad administrativa), ahí se denuncia.
Línea gratuita: 122.

**Qué llevar:** el derecho de petición ya enviado, la respuesta de la entidad (o la constancia
de que no respondió dentro del término legal), y el paquete de evidencia de este caso.

_{caso.disclaimer}_
"""
    return Artefacto(
        tipo=TipoArtefacto.GUIA_DENUNCIA,
        titulo=f"Guía para denunciar — {caso.entidad}",
        cuerpo_markdown=cuerpo,
        normas_citadas=[],
        destinatario=None,
        caso_id=caso.id,
    )


async def generar_artefacto(caso: Caso, tipo: TipoArtefacto) -> Artefacto:
    if tipo == TipoArtefacto.DERECHO_PETICION:
        return await _generar_derecho_peticion(caso)
    if tipo == TipoArtefacto.PAQUETE_EVIDENCIA:
        return _generar_paquete_evidencia(caso)
    if tipo == TipoArtefacto.INFORME_VEEDURIA:
        return _generar_informe_veeduria(caso)
    return _generar_guia_denuncia(caso)
