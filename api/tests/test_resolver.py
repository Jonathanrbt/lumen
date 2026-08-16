"""Pruebas de /resolver. Dueno: Freddy (B2).

Mockean `CromaClient.consultar` (sin red, sin cuota) para fijar la logica de
mapeo RUES -> Candidato: el heuristico de tipo, el orden por NIT, el
deduplicado, y que un texto invalido para RUES (signos que la API real
rechaza, confirmado en vivo) no explota el endpoint.

La integracion real contra RUES vive en test_resolver_croma.py, marcada
`croma` igual que el resto de las pruebas de Jonatin contra Croma real.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from lumen.croma.client import CromaError
from lumen.main import app

cliente = TestClient(app)

RESPUESTA_CONALVIAS: dict[str, Any] = {
    "query": "Conalvias",
    "capped": False,
    "entities": [
        {
            "name": "CONALVIAS",
            "nit": None,
            "chamber_name": "MEDELLIN PARA ANTIOQUIA",
            "legal_organization": "SOCIEDAD ANONIMA",
            "category": "AGENCIA",
            "detail": {
                "commercial_municipality": None,
                "primary_activity": {
                    "code": "F453001",
                    "description": "CONSTRUCCION, REFORMAS Y REPARACIONES COMPLETAS DE CARRETERAS Y CALLES",
                },
            },
        },
        {
            "name": "CONALVIAS CONSTRUCCIONES S.A.S. EN LIQUIDACION JUDICIAL",
            "nit": "890318278",
            "chamber_name": "CALI",
            "legal_organization": "SOCIEDADES POR ACCIONES SIMPLIFICADAS SAS",
            "category": "SOCIEDAD ó PERSONA JURIDICA PRINCIPAL ó ESAL",
            "detail": {
                "commercial_municipality": None,
                "primary_activity": {
                    "code": "4210",
                    "description": "Construcción de carreteras y vías de ferrocarril",
                },
            },
        },
        # Duplicado de nombre a proposito: el segundo debe filtrarse.
        {
            "name": "CONALVIAS CONSTRUCCIONES S.A.S. EN LIQUIDACION JUDICIAL",
            "nit": "999999999",
            "chamber_name": "CALI",
            "legal_organization": "SOCIEDADES POR ACCIONES SIMPLIFICADAS SAS",
            "category": "SOCIEDAD",
            "detail": {},
        },
    ],
}


async def _consultar_falso(self, fuente: str, argumentos: dict[str, Any] | None = None):
    assert fuente == "rues_entities_by_name"
    if argumentos["name"] == "sin-resultados":
        return {"query": "sin-resultados", "capped": False, "entities": []}
    if argumentos["name"] == "explota":
        raise CromaError("HTTP 400: nombre invalido")
    return RESPUESTA_CONALVIAS


class _LLMFalso:
    """Cuenta llamadas para poder afirmar que el camino barato no lo toca, y
    nunca pega contra Cursor de verdad (cuesta presupuesto real y no es
    determinista en CI)."""

    def __init__(self) -> None:
        self.llamadas = 0

    async def preguntar(self, prompt: str, modelo) -> str:
        self.llamadas += 1
        return "NINGUNO"


@pytest.fixture(autouse=True)
def _mockear_croma(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("lumen.croma.client.CromaClient.consultar", _consultar_falso)
    yield


@pytest.fixture()
def llm_falso(monkeypatch: pytest.MonkeyPatch) -> _LLMFalso:
    falso = _LLMFalso()
    monkeypatch.setattr("lumen.ia.resolver.preguntar", falso.preguntar)
    return falso


def test_resolver_con_nombre_directo_no_llama_al_llm(llm_falso: _LLMFalso):
    """Camino barato: el texto ya es un nombre, va directo a RUES.

    El texto es "Constructora Ejemplo" y no "Conalvias" a propósito: desde el
    16.ago "conalvias" es un alias del catálogo curado y ni siquiera llegaría a
    RUES. Aquí se prueba el camino de RUES, así que el nombre tiene que ser uno
    que el catálogo no conozca."""
    r = cliente.post("/resolver", json={"texto": "Constructora Ejemplo"})

    assert llm_falso.llamadas == 0
    assert r.status_code == 200
    candidatos = r.json()
    # De los 3 que devuelve RUES: uno se cae por nombre duplicado y otro por no
    # traer NIT (sin NIT no hay nada que analizar después).
    assert len(candidatos) == 1
    assert candidatos[0]["nit"] == "890318278"
    assert candidatos[0]["nombre"] == "CONALVIAS CONSTRUCCIONES S.A.S. EN LIQUIDACION JUDICIAL"
    assert candidatos[0]["tipo"] == "empresa"
    assert candidatos[0]["actividad"].startswith("4210 - ")


def test_resolver_descarta_candidatos_sin_nit(llm_falso: _LLMFalso):
    """El bug del bucle, fijado: RUES devuelve registros de cámara de comercio
    sin NIT y el chat no puede hacer nada con ellos — al elegirlos volvía a
    resolver el mismo texto y mostraba las mismas tarjetas, para siempre."""
    r = cliente.post("/resolver", json={"texto": "Constructora Ejemplo"})

    assert all(c["nit"] for c in r.json())


def test_catalogo_curado_resuelve_sin_tocar_croma_ni_el_llm(
    llm_falso: _LLMFalso, monkeypatch: pytest.MonkeyPatch
):
    """Brief §4.5.1: lo que el equipo ya verificó a mano no pasa por RUES.

    Croma se rompe a propósito aquí: si el catálogo lo tocara, el test falla."""

    async def _croma_prohibida(self, fuente: str, argumentos=None):
        raise AssertionError("el catálogo curado no debe consultar Croma")

    monkeypatch.setattr("lumen.croma.client.CromaClient.consultar", _croma_prohibida)

    r = cliente.post("/resolver", json={"texto": "¿la Gobernación del Chocó tiene algo raro?"})

    assert llm_falso.llamadas == 0
    assert r.status_code == 200
    candidatos = r.json()
    assert len(candidatos) == 1
    assert candidatos[0]["nit"] == "891680010"
    assert candidatos[0]["tipo"] == "entidad"


def test_catalogo_no_se_dispara_por_una_palabra_dentro_de_otra(llm_falso: _LLMFalso):
    """"cali" es alias, pero "calidad" no puede despertarlo: el emparejamiento
    es por palabra completa, no por subcadena."""
    from lumen.ia import catalogo

    assert catalogo.buscar("un contrato de calidad") == []
    assert catalogo.buscar("la alcaldía de Cali") != []


def test_resolver_sin_resultados_devuelve_lista_vacia(llm_falso: _LLMFalso):
    """Nombre válido para RUES pero sin resultados: el camino barato falla y
    cae al LLM (mockeado, dice NINGUNO), termina en lista vacía."""
    r = cliente.post("/resolver", json={"texto": "sin-resultados"})

    assert llm_falso.llamadas == 1
    assert r.status_code == 200
    assert r.json() == []


def test_resolver_texto_vacio_no_llama_a_croma():
    r = cliente.post("/resolver", json={"texto": "   "})

    assert r.status_code == 200
    assert r.json() == []


def test_resolver_texto_con_signos_usa_el_llm_y_no_revienta(llm_falso: _LLMFalso):
    """El texto tiene "¿" y "?", que RUES rechaza (confirmado en vivo contra
    la API real): el camino barato se salta y entra el LLM. Aquí el LLM
    mockeado dice NINGUNO, así que el resultado es lista vacía, no un 500."""
    r = cliente.post("/resolver", json={"texto": "¿explota esto?"})

    assert llm_falso.llamadas == 1
    assert r.status_code == 200
    assert r.json() == []


def test_resolver_si_el_llm_no_arranca_no_revienta(monkeypatch: pytest.MonkeyPatch):
    """Config rota (auth, red) en el paso del LLM: se degrada a lista vacía,
    nunca un 500 — /resolver es de cara al ciudadano."""
    from lumen.ia.llm_client import CursorAgentError

    async def _preguntar_roto(prompt: str, modelo):
        raise CursorAgentError("CURSOR_API_KEY inválida")

    monkeypatch.setattr("lumen.ia.resolver.preguntar", _preguntar_roto)

    r = cliente.post("/resolver", json={"texto": "¿explota esto?"})

    assert r.status_code == 200
    assert r.json() == []
