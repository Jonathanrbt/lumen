"""Pruebas de llm_client. Dueno: Freddy (B2).

No pegan contra Cursor de verdad (costaria presupuesto real en cada corrida
de CI): mockean `AsyncClient` y `AsyncAgent` para fijar el guardarrail que
importa, la higiene de errores del handoff: `CursorAgentError` es "nunca
arranco", `LLMEjecucionError` es "arranco y no termino bien". Confundirlos
cuesta una hora, segun el propio handoff.

El smoke test real (con la key de verdad, gastando unos tokens) se corrio a
mano el 16.ago ~01:15 y esta documentado en docs/handoff/FREDDY-B2.md.
"""

from __future__ import annotations

import asyncio

import pytest

from lumen.config import get_settings
from lumen.ia import llm_client
from lumen.ia.llm_client import CursorAgentError, LLMEjecucionError, Modelo, preguntar


class _ClienteFalso:
    async def aclose(self) -> None:
        pass


class _AsyncClientFalso:
    @staticmethod
    async def launch_bridge(*, workspace: str) -> _ClienteFalso:
        return _ClienteFalso()


class _ResultadoFalso:
    def __init__(self, status: str, result: str) -> None:
        self.status = status
        self.result = result


def _agente_falso(status: str, result: str = "") -> type:
    class _AsyncAgentFalso:
        @staticmethod
        async def prompt(mensaje: str, opciones, *, client) -> _ResultadoFalso:
            return _ResultadoFalso(status, result)

    return _AsyncAgentFalso


@pytest.fixture(autouse=True)
def _limpiar_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_falta_modelo_lanza_cursor_agent_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_MODELO_RAPIDO", "")

    with pytest.raises(CursorAgentError):
        asyncio.run(preguntar("hola", Modelo.RAPIDO))


def test_status_finished_devuelve_el_texto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_MODELO_RAPIDO", "composer-2.5")
    monkeypatch.setattr(llm_client, "AsyncClient", _AsyncClientFalso)
    monkeypatch.setattr(llm_client, "AsyncAgent", _agente_falso("finished", "hola"))

    resultado = asyncio.run(preguntar("hola", Modelo.RAPIDO))

    assert resultado == "hola"


@pytest.mark.parametrize("status", ["error", "cancelled", "expired"])
def test_status_no_finished_lanza_llm_ejecucion_error(
    monkeypatch: pytest.MonkeyPatch, status: str
) -> None:
    monkeypatch.setenv("LUMEN_MODELO_FUERTE", "claude-opus-5")
    monkeypatch.setattr(llm_client, "AsyncClient", _AsyncClientFalso)
    monkeypatch.setattr(llm_client, "AsyncAgent", _agente_falso(status))

    with pytest.raises(LLMEjecucionError):
        asyncio.run(preguntar("hola", Modelo.FUERTE))
