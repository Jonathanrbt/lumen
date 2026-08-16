"""Plantillas literales de docs/COPY-SENALES.md. No se reescriben en otra capa."""

from __future__ import annotations

from .pesos import pesos_redondeados


def s1(meses: int, valor: float) -> str:
    tiempo = "un mes" if meses <= 1 else f"{meses} meses"
    return f"Esta empresa se creó hace {tiempo} y ya ganó un contrato de {pesos_redondeados(valor)}."


def s2() -> str:
    return "Estas dos empresas tienen el mismo representante. Se presentaron al mismo proceso."


def s3() -> str:
    return "Esta empresa tiene una sanción vigente y le siguieron adjudicando contratos."


def s4() -> str:
    return (
        "Esta empresa nunca ha reportado ingresos de este tamaño. "
        "El contrato es más grande que toda su facturación de un año."
    )


def s5() -> str:
    return "Esta empresa está en proceso de insolvencia. Si quiebra, la obra queda a medias."


def s6(cantidad: int) -> str:
    return (
        f"Se firmaron {cantidad} contratos parecidos, casi el mismo día, "
        "cada uno justo por debajo del monto que obliga a hacer concurso."
    )


def s7(porcentaje: int, cuantas: int) -> str:
    sujeto = "Una empresa se llevó" if cuantas == 1 else f"{cuantas} empresas se llevaron"
    return f"{sujeto} el {porcentaje} % de toda la plata de esta entidad."


def s8(porcentaje: int, cuantas: int) -> str:
    return s7(porcentaje, cuantas)


def s10() -> str:
    return "Esta empresa le debe plata al Estado, y el Estado le sigue adjudicando contratos."
