"""El contrato tiene que ser verdad, no una promesa.

Andrew construye el frontend contra los fixtures sin esperar al backend. Si un
fixture no cuadra con el modelo que la API devuelve de verdad, esa apuesta se
rompe y lo descubrimos a las dos de la manana, en plena integracion.

Estas pruebas son baratas y corren en segundos:

    .\\.venv\\Scripts\\python.exe -m pytest api/tests -q

Correlas antes de pushear un cambio en `contracts/` o en `fixtures/`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lumen.contracts import (
    AlertaResponse,
    Artefacto,
    Candidato,
    Caso,
    ChatResponse,
    Lectura,
    NivelAtencion,
    Senal,
)

RAIZ = Path(__file__).resolve().parents[2]
FIXTURES = RAIZ / "fixtures"


def cargar(nombre: str):
    return json.loads((FIXTURES / nombre).read_text(encoding="utf-8"))


def test_caso_cuadra_con_el_modelo():
    caso = Caso.model_validate(cargar("caso.json"))
    assert caso.senales, "un caso sin señales no le sirve a nadie"
    assert caso.disclaimer, "el disclaimer va en cada resultado, no en un footer"


def test_candidatos_cuadran_con_el_modelo():
    datos = cargar("candidatos.json")
    candidatos = [Candidato.model_validate(c) for c in datos]
    assert len(candidatos) > 1, "el fixture existe para probar la desambiguación"


def test_lectura_cuadra_con_el_modelo():
    lectura = Lectura.model_validate(cargar("lectura.json"))
    assert lectura.puntos


def test_artefacto_cuadra_con_el_modelo():
    artefacto = Artefacto.model_validate(cargar("artefacto.json"))
    assert artefacto.cuerpo_markdown.strip()
    assert artefacto.normas_citadas, "un derecho de petición sin norma citada no sirve"


def test_respuestas_de_chat_cuadran_con_el_modelo():
    ChatResponse.model_validate(cargar("chat_desambiguacion.json"))
    ChatResponse.model_validate(cargar("chat_respuesta.json"))


def test_alerta_cuadra_con_el_modelo():
    AlertaResponse.model_validate(cargar("alerta.json"))


# ---------------------------------------------------------------------------
# Guardarrailes del producto. Estos no son pruebas de tipos: son pruebas de que
# las promesas eticas del proyecto estan escritas en el codigo y no solo en el
# README. Si alguna falla, alguien rompio el producto, no la libreria.
# ---------------------------------------------------------------------------


def test_una_senal_no_se_puede_construir_sin_fuente():
    """Sin fuente oficial con fecha, no hay señal. Punto."""
    with pytest.raises(Exception):
        Senal(
            codigo="S1",
            nombre="Empresa recién creada",
            nivel="alto",
            regla_legible="La empresa se registró 41 días antes de ganar.",
            datos_usados={},
            # falta `fuente` a proposito
        )


def test_el_nivel_de_atencion_nunca_es_un_numero():
    """Tres estados con color. Si aparece un score, rompimos el producto."""
    assert {n.value for n in NivelAtencion} == {"bajo", "medio", "alto"}

    with pytest.raises(Exception):
        Caso.model_validate({**cargar("caso.json"), "nivel_atencion": 0.78})


def test_el_disclaimer_viene_por_defecto():
    """Que no dependa de que alguien se acuerde de ponerlo."""
    caso = Caso(id="x", modo="vigilancia", entidad="Entidad", nivel_atencion="bajo")
    assert "no es prueba de irregularidad" in caso.disclaimer


def test_el_lector_puede_no_concluir():
    """Si la IA no puede citar el fragmento, dice que no concluye. Nunca inventa."""
    lectura = Lectura.model_validate(cargar("lectura.json"))
    sin_cita = [p for p in lectura.puntos if p.cita_textual is None]
    assert sin_cita, "el fixture debe mostrar el caso de 'no puedo concluir'"
    assert all(p.no_concluye_por for p in sin_cita), (
        "un punto sin cita tiene que explicar por qué no concluye"
    )
