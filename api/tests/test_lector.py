"""Pruebas del lector de justificaciones. Dueno: Freddy (B2).

No pegan contra Cursor de verdad (mockean `preguntar`) ni dependen de
extraer texto de un PDF real (mockean `_texto_por_pagina`): lo que fijan es
la lógica propia — el guardarraíl anti-alucinación de citas, que 'solida'
sea imposible en código si algún punto quedó sin cita, y que un JSON roto
del modelo no tumbe el endpoint con un 500.

La prueba de extracción real de PDF (con un PDF de verdad, sin mocks) vive
en test_lector_pdf_real.py.
"""

from __future__ import annotations

import asyncio

import pytest

from lumen.contracts import Veredicto
from lumen.ia import lector

DOCUMENTO = (
    "--- Página 1 ---\n"
    "Objeto: suministro de mobiliario de oficina para la sede administrativa.\n"
    "--- Página 2 ---\n"
    "Conforme a la necesidad identificada en el Plan Anual de Adquisiciones de junio de 2026."
)


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def _mockear_extraccion(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(lector, "_texto_por_pagina", lambda contenido: DOCUMENTO.split("\n\n"))
    yield


def test_veredicto_solida_es_imposible_si_falta_una_cita(monkeypatch: pytest.MonkeyPatch) -> None:
    """Guardarraíl en código: el modelo dice 'solida' pero un punto no tiene
    cita real -- el resultado tiene que bajar a 'generica', no confiar en lo
    que diga el modelo."""

    async def _preguntar_falso(prompt: str, modelo) -> str:
        return """{
            "veredicto": "solida",
            "puntos": [
                {"hallazgo": "Es mobiliario, no tiene que ver con el terremoto.",
                 "cita_textual": "suministro de mobiliario de oficina para la sede administrativa",
                 "pagina": 1, "no_concluye_por": null},
                {"hallazgo": "Ya existía antes.",
                 "cita_textual": "Plan Anual de Adquisiciones de junio de 2026",
                 "pagina": 2, "no_concluye_por": null},
                {"hallazgo": "No hay estudios.",
                 "cita_textual": null, "pagina": null,
                 "no_concluye_por": "El documento no contiene ningun anexo tecnico."}
            ]
        }"""

    monkeypatch.setattr(lector, "preguntar", _preguntar_falso)

    resultado = _run(lector.leer_justificacion(b"pdf-falso"))

    assert resultado.veredicto == Veredicto.GENERICA  # no 'solida', pese a lo que dijo el modelo
    assert len(resultado.puntos) == 3
    assert resultado.puntos[2].cita_textual is None
    assert resultado.puntos[2].no_concluye_por


def test_cita_inventada_se_descarta_aunque_el_modelo_la_de_por_buena(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Anti-alucinación: una cita que no aparece en el documento real se
    descarta, no se confía ciegamente en el modelo."""

    async def _preguntar_falso(prompt: str, modelo) -> str:
        return """{
            "veredicto": "solida",
            "puntos": [
                {"hallazgo": "Sí tiene relación con el terremoto.",
                 "cita_textual": "esta frase no existe en el documento para nada",
                 "pagina": 1, "no_concluye_por": null},
                {"hallazgo": "x", "cita_textual": null, "pagina": null, "no_concluye_por": "x"},
                {"hallazgo": "x", "cita_textual": null, "pagina": null, "no_concluye_por": "x"}
            ]
        }"""

    monkeypatch.setattr(lector, "preguntar", _preguntar_falso)

    resultado = _run(lector.leer_justificacion(b"pdf-falso"))

    assert resultado.puntos[0].cita_textual is None
    assert "no coincide" in resultado.puntos[0].no_concluye_por
    assert resultado.veredicto == Veredicto.GENERICA


def test_json_roto_no_tumba_el_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    from lumen.ia.llm_client import LLMEjecucionError

    async def _preguntar_falso(prompt: str, modelo) -> str:
        return "esto no es JSON para nada"

    monkeypatch.setattr(lector, "preguntar", _preguntar_falso)

    with pytest.raises(LLMEjecucionError):
        _run(lector.leer_justificacion(b"pdf-falso"))


def test_json_envuelto_en_markdown_se_parsea_igual(monkeypatch: pytest.MonkeyPatch) -> None:
    """El prompt pide JSON puro, pero el modelo a veces lo envuelve en
    ```json de todos modos -- el parser tiene que tolerarlo."""

    async def _preguntar_falso(prompt: str, modelo) -> str:
        return """```json
        {"veredicto": "sin_relacion", "puntos": [
            {"hallazgo": "a", "cita_textual": null, "pagina": null, "no_concluye_por": "a"},
            {"hallazgo": "b", "cita_textual": null, "pagina": null, "no_concluye_por": "b"},
            {"hallazgo": "c", "cita_textual": null, "pagina": null, "no_concluye_por": "c"}
        ]}
        ```"""

    monkeypatch.setattr(lector, "preguntar", _preguntar_falso)

    resultado = _run(lector.leer_justificacion(b"pdf-falso"))

    assert resultado.veredicto == Veredicto.SIN_RELACION


def test_menos_de_tres_puntos_se_completa_sin_inventar(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _preguntar_falso(prompt: str, modelo) -> str:
        return '{"veredicto": "generica", "puntos": []}'

    monkeypatch.setattr(lector, "preguntar", _preguntar_falso)

    resultado = _run(lector.leer_justificacion(b"pdf-falso"))

    assert len(resultado.puntos) == 3
    assert all(p.no_concluye_por == "El modelo no respondió esta pregunta." for p in resultado.puntos)
    assert [p.pregunta for p in resultado.puntos] == lector.PREGUNTAS


# La prueba de "PDF real en blanco -> DocumentoIlegible" vive en
# test_lector_pdf_real.py: necesita la función real `_texto_por_pagina` sin
# el mock autouse de este archivo.
