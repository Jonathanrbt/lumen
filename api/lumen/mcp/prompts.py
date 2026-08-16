"""Aperturas de conversacion del servidor MCP. Dueno: Cristian (B3).

Tercera capa del comportamiento (§design.md, decision 4). Las dos primeras son
`instrucciones.py` y las descripciones de las herramientas; estas son los tres
puntos de entrada tipicos, listos para que un cliente MCP los ofrezca como
comandos.

Cada prompt devuelve el arranque completo de la conversacion, con la regla que
mas se rompe en ese camino repetida donde toca. Son texto, no ejecutan nada.
"""

from __future__ import annotations

__all__ = ["registrar_prompts"]


def _buscar_empresa(nombre: str) -> str:
    return f"""\
Busca "{nombre}" y cuéntame qué aparece.

Empieza por `resolver_entidad` con ese texto tal cual. Cuando devuelva candidatos, \
muéstramelos todos con su NIT, ciudad y actividad, y pregúntame cuál es — también si \
solo encuentras uno. No elijas por mí.

Cuando yo confirme, corre `analizar_entidad` con el NIT (avísame antes: tarda entre \
80 y 100 segundos) y cuéntame el resultado en lenguaje sencillo, reusando el texto \
`regla_legible` de cada señal y diciendo de qué fuente oficial sale cada cosa. \
Muéstrame el descargo junto al resultado.

Al final ofréceme ver la red de actores y generar el paquete de evidencia; el derecho \
de petición solo si el nivel de atención es medio o alto.
"""


def _revisar_entidad_publica(entidad: str) -> str:
    return f"""\
Quiero revisar cómo está contratando "{entidad}".

Resuelve primero el nombre con `resolver_entidad` y confírmame cuál de los candidatos \
es la entidad que busco antes de seguir. Después corre `analizar_entidad` usando el \
NIT como `entidad_id`, que es la llave para mirar a la entidad como contratante y no \
como proveedora.

Cuéntame qué señales aparecen, cada una con su fuente. Si no aparece ninguna, dímelo \
tal cual: que no haya señales es un resultado, no un fallo. Nunca digas que la entidad \
es corrupta ni que algo es ilegal — son patrones que merecen revisión.
"""


def _revisar_justificacion(url: str) -> str:
    return f"""\
Revisa esta justificación de urgencia manifiesta: {url}

Usa `leer_justificacion_urgencia`. La norma exige que una contratación por urgencia \
tenga relación directa y verificable con los hechos de la emergencia, precedida de \
diagnósticos técnicos.

Cuando me des el veredicto, muéstrame cada punto con su cita textual del documento. \
Si un punto no tiene cita, dime por qué no se pudo concluir en vez de afirmarlo igual: \
sin cita no hay afirmación. Y explícame qué significa el veredicto en palabras \
normales, sin que suene a sentencia.
"""


def registrar_prompts(servidor) -> None:  # noqa: ANN001 - MCPServer, sin importarlo aqui
    """Registra las tres aperturas en el servidor MCP.

    Va como funcion y no como decoradores sueltos para que `servidor.py` sea el
    unico sitio donde se arma el servidor, igual que con las herramientas.
    """

    @servidor.prompt(
        name="buscar_empresa",
        title="Buscar una empresa por nombre",
        description=(
            "Arranca la búsqueda de una empresa o proveedor por su nombre, con la "
            "desambiguación obligatoria antes de analizar."
        ),
    )
    def buscar_empresa(nombre: str) -> str:
        """Nombre de la empresa tal como lo diría una persona, sin NIT."""
        return _buscar_empresa(nombre)

    @servidor.prompt(
        name="revisar_entidad_publica",
        title="Revisar la contratación de una entidad pública",
        description=(
            "Arranca la revisión de una alcaldía, gobernación o entidad pública como "
            "contratante, usando su NIT como entidad_id."
        ),
    )
    def revisar_entidad_publica(entidad: str) -> str:
        """Nombre de la alcaldía, gobernación o entidad pública."""
        return _revisar_entidad_publica(entidad)

    @servidor.prompt(
        name="revisar_justificacion",
        title="Revisar una justificación de urgencia manifiesta",
        description=(
            "Arranca la lectura del PDF de una justificación de urgencia manifiesta, "
            "con la regla de que sin cita textual no hay afirmación."
        ),
    )
    def revisar_justificacion(url: str) -> str:
        """Enlace al PDF de la justificación."""
        return _revisar_justificacion(url)
