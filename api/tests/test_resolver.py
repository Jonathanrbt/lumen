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
    """Camino barato: el texto ya es un nombre, va directo a RUES."""
    r = cliente.post("/resolver", json={"texto": "Conalvias"})

    assert llm_falso.llamadas == 0
    assert r.status_code == 200
    candidatos = r.json()
    assert len(candidatos) == 2  # el duplicado de nombre se filtra
    # El que trae NIT va primero: es el que sirve para seguir a /analizar.
    assert candidatos[0]["nit"] == "890318278"
    assert candidatos[0]["nombre"] == "CONALVIAS CONSTRUCCIONES S.A.S. EN LIQUIDACION JUDICIAL"
    assert candidatos[0]["tipo"] == "empresa"
    assert candidatos[0]["actividad"].startswith("4210 - ")
    assert candidatos[1]["nit"] is None
    assert candidatos[1]["ciudad"] == "MEDELLIN PARA ANTIOQUIA"  # fallback a chamber_name


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
