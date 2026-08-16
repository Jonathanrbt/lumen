"""Catalogo curado del Modo Vigilancia (brief SS4.5.1 y SS4.5.4). Dueno: Freddy (B2).

La fila "Obra o proyecto famoso" de SS4.5.1 dice que la resolucion de entidades
tiene que pasar por un **catalogo propio** antes de ir a RUES. Estaba planeado
desde la 01:15 ("qué sigue: /resolver contra el catálogo curado") y nunca se
escribio: `resolver.py` iba directo a RUES siempre. El precio se vio en vivo el
16.ago — "el metro de Bogotá" devolvia METRO BIKES, un hotel y una firma de
arquitectura de Barcelona, y las tarjetas de arranque del chat morian en "no
encontré nada".

**Ni un identificador inventado.** Cada entrada de aqui sale de algo que ya
estaba verificado contra Croma y anotado por su dueno:

- Los cuatro NIT de entidad del sismo, de `docs/entidades-emergencia.json`
  (Jonatin, consultado en Croma el 15.ago 23:50). Freddy confirmo despues que
  Choco, Valle y Buenaventura disparan una S6 real.
- Bogota (`899999061`), Odinsa (`800169499`) y Conalvias (`890318278`), de la
  tabla de `docs/handoff/JONATIN-B1.md` y de `CATALOGO_CURADO` en
  `scripts/precomputar_casos_demo.py`.

Los que Jonatin dejo marcados como **no resueltos** — Metro de Bogota, UNGRD
2024, Mocoa 2017, Providencia — **no estan aqui**, porque su instruccion fue
literal: *"Metro de Bogota no aparece como Empresa Metro en RUES. No inventar."*
Cuando alguien verifique uno, se agrega una entrada y ya.

No se expone el proveedor de prueba `79372917`: es una persona natural y el
guardarrail #4 del brief mantiene a las personas fuera del producto salvo en su
rol publico. Sirve de smoke tecnico por CLI, no de puerta de entrada.

**Esto no rompe la regla de desambiguar** (SS4.5.2 #1): el catalogo devuelve un
`Candidato`, no un `Caso`. La persona sigue confirmando en una tarjeta antes de
que se analice nada. Lo unico que cambia es que el candidato viene curado y con
el NIT correcto, en vez de salir de una busqueda por texto en el registro
mercantil.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from ..contracts import Candidato, TipoActor

#: Zona del sismo del 10 de agosto de 2026. El texto que ve la persona sale de
#: `docs/entidades-emergencia.json`, no se redacta aqui.
_SISMO = "Zona del sismo del 10 de agosto"


@dataclass(frozen=True)
class Entrada:
    """Un caso curado: como se dice, y a que identificador verificado apunta.

    `alias` son las formas en que una persona lo escribiria. Se comparan sobre
    el texto normalizado (sin tildes, en minusculas) y **por palabra completa**,
    para que "cali" no se dispare dentro de "calidad".
    """

    candidato: Candidato
    alias: tuple[str, ...]


CATALOGO: tuple[Entrada, ...] = (
    Entrada(
        candidato=Candidato(
            nombre="Gobernación del Chocó",
            nit="891680010",
            ciudad="Chocó",
            actividad=_SISMO,
            tipo=TipoActor.ENTIDAD,
        ),
        alias=("choco", "gobernacion del choco", "quibdo"),
    ),
    Entrada(
        candidato=Candidato(
            nombre="Gobernación del Valle del Cauca",
            nit="890399029",
            ciudad="Valle del Cauca",
            actividad=_SISMO,
            tipo=TipoActor.ENTIDAD,
        ),
        alias=("valle", "valle del cauca", "gobernacion del valle"),
    ),
    Entrada(
        candidato=Candidato(
            nombre="Alcaldía Distrital de Buenaventura",
            nit="890399045",
            ciudad="Buenaventura",
            actividad=_SISMO,
            tipo=TipoActor.ENTIDAD,
        ),
        alias=("buenaventura", "alcaldia de buenaventura"),
    ),
    Entrada(
        candidato=Candidato(
            nombre="Santiago de Cali Distrito Especial",
            nit="890399011",
            ciudad="Cali",
            actividad=_SISMO,
            tipo=TipoActor.ENTIDAD,
        ),
        alias=("cali", "santiago de cali", "alcaldia de cali"),
    ),
    Entrada(
        candidato=Candidato(
            nombre="Alcaldía Mayor de Bogotá y alcaldías locales",
            nit="899999061",
            ciudad="Bogotá",
            actividad="Incluye la Alcaldía Local de Kennedy",
            tipo=TipoActor.ENTIDAD,
        ),
        alias=("bogota", "alcaldia de bogota", "kennedy", "alcaldia local de kennedy"),
    ),
    Entrada(
        candidato=Candidato(
            nombre="ODINSA S.A.",
            nit="800169499",
            ciudad="Bogotá",
            actividad="Concesiones viales · Ruta del Sol",
            tipo=TipoActor.EMPRESA,
        ),
        alias=("odinsa", "ruta del sol"),
    ),
    Entrada(
        candidato=Candidato(
            nombre="CONALVIAS CONSTRUCCIONES S.A.S. EN LIQUIDACION JUDICIAL",
            nit="890318278",
            ciudad="Cali",
            actividad="Construcción de carreteras y vías",
            tipo=TipoActor.EMPRESA,
        ),
        alias=("conalvias",),
    ),
)


def _normalizar(texto: str) -> str:
    """Sin tildes, en minusculas y sin signos: "¿el Chocó?" -> "el choco".

    Los signos se cambian por espacio y no se borran, para que "choco,valle"
    siga siendo dos palabras y el emparejamiento por palabra completa funcione.
    """
    sin_tildes = "".join(
        c
        for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9ñ]+", " ", sin_tildes).strip()


def _menciona(texto_normalizado: str, alias: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", texto_normalizado) is not None


def buscar(texto: str) -> list[Candidato]:
    """Los candidatos curados que menciona el texto. Cero red, cero LLM.

    Se devuelven en el orden del catalogo y sin repetir, para que dos alias de
    la misma entrada ("kennedy" y "bogota" en la misma frase) no la muestren
    dos veces.
    """
    normalizado = _normalizar(texto)
    if not normalizado:
        return []

    encontrados: list[Candidato] = []
    for entrada in CATALOGO:
        if any(_menciona(normalizado, alias) for alias in entrada.alias):
            encontrados.append(entrada.candidato)
    return encontrados
