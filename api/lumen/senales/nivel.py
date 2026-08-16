"""Nivel de atención solo a partir de señales. La lectura de Freddy se suma después."""

from ..contracts import NivelAtencion, Senal


def desde_senales(senales: list[Senal]) -> NivelAtencion:
    if len(senales) >= 2:
        return NivelAtencion.ALTO
    if len(senales) == 1:
        return NivelAtencion.MEDIO
    return NivelAtencion.BAJO
