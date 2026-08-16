"""Arma el texto del mensaje. Fuente unica del copy: docs/COPY-SENALES.md.

No redacta señales nuevas: reusa `Senal.regla_legible`, que Jonatin (B1) ya
escribe en lenguaje ciudadano, y el `Caso.disclaimer` que trae el texto fijo
del parche v3.1. Este modulo solo decide el orden y el limite de 5 lineas —
nunca inventa una frase que no este ya en el contrato.

Portado 1:1 desde el respaldo de Cristian (`api/lumen/plataforma/whatsapp.py`,
escrito antes de la reasignacion de las 22:14): la logica ya estaba bien, no
hacia falta reinventarla.
"""

from __future__ import annotations

from ..config import get_settings
from ..contracts import Caso

MAX_LINEAS = 5


def formatear_pesos(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def url_ficha(caso: Caso) -> str:
    ajustes = get_settings()
    if ajustes.lumen_frontend_url:
        # El prefijo /app no es decorativo: la ficha vive en la ruta
        # /app/caso/:id del router del frontend y el catch-all redirige todo
        # lo demas al landing. Sin /app el enlace del WhatsApp abre la portada
        # y el veedor nunca ve el caso, sin ningun error visible.
        return f"{ajustes.lumen_frontend_url.rstrip('/')}/app/caso/{caso.id}"
    # Sin dominio declarado se enlaza al recurso de la API.
    return f"Ver evidencia: pide el caso {caso.id} en la API (dominio del frontend pendiente)"


def armar_mensaje(caso: Caso) -> str:
    """Maximo 5 lineas, con el copy exacto que ya trae cada Senal."""
    encabezado = f"Nuevo contrato en {caso.municipio or caso.entidad}"
    if caso.valor:
        encabezado += f" por {formatear_pesos(caso.valor)}"
    lineas = [encabezado + "."]

    for senal in caso.senales[:2]:  # deja espacio para disclaimer + enlace en 5 lineas
        lineas.append(senal.regla_legible)

    lineas.append(caso.disclaimer)
    lineas.append(url_ficha(caso))

    return "\n".join(lineas[:MAX_LINEAS])
