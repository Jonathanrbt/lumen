"""Pruebas del cliente de Telegram. Dueno: Freddy (B2).

No pegan contra Telegram de verdad: fijan el guardarraíl de siempre (nunca
'enviado' fabricado) usando un transport falso de httpx en vez de mockear la
librería completa.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from lumen.config import get_settings
from lumen.telegram import cliente as telegram_cliente


@pytest.fixture(autouse=True)
def _limpiar_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _run(coro):
    return asyncio.run(coro)


def test_sin_token_nunca_dice_enviado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")

    estado, detalle = _run(telegram_cliente.enviar("123456", "hola"))

    assert estado == "error"
    assert estado != "enviado"
    assert "TELEGRAM_BOT_TOKEN" in detalle


def test_telegram_ok_dice_enviado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:falso")

    def _handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/sendMessage")
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})

    _ClienteReal = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: _ClienteReal(transport=httpx.MockTransport(_handler), **kw)
    )

    estado, detalle = _run(telegram_cliente.enviar("123456", "hola"))

    assert estado == "enviado"


def test_telegram_rechaza_nunca_dice_enviado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:falso")

    def _handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"ok": False, "error_code": 400, "description": "chat not found"})

    _ClienteReal = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: _ClienteReal(transport=httpx.MockTransport(_handler), **kw)
    )

    estado, detalle = _run(telegram_cliente.enviar("000", "hola"))

    assert estado == "error"
    assert "chat not found" in detalle


def test_parse_mode_es_opcional_y_por_defecto_no_se_manda(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin parse_mode explícito, el comportamiento no cambia -- /alerta y el
    monitor no se enteran de este parámetro nuevo."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:falso")
    import json

    capturado = {}

    def _handler(request: httpx.Request) -> httpx.Response:
        capturado["json"] = json.loads(request.content)
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})

    _ClienteReal = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: _ClienteReal(transport=httpx.MockTransport(_handler), **kw)
    )

    _run(telegram_cliente.enviar("123456", "hola"))
    assert "parse_mode" not in capturado["json"]

    _run(telegram_cliente.enviar("123456", "<b>hola</b>", parse_mode="HTML"))
    assert capturado["json"]["parse_mode"] == "HTML"
