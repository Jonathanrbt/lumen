"""Pruebas del despachador de canal (api/lumen/alertas.py). Dueno: Freddy (B2).

Fija que LUMEN_CANAL_ALERTA elige el proveedor correcto y que la regla de
nivel_atencion se aplica una sola vez, antes de tocar cualquier canal.
"""

from __future__ import annotations

import asyncio

import pytest

from lumen.alertas import enviar_alerta
from lumen.config import get_settings
from lumen.contracts import Caso, Fuente, ModoCaso, NivelAtencion, Senal

FUENTE = Fuente(
    herramienta_croma="rues_entity_by_nit",
    url_oficial="https://www.rues.org.co/",
    consultado_en="2026-08-15T17:20:00-05:00",
)


def _caso(nivel: NivelAtencion) -> Caso:
    return Caso(
        id="caso-test-alertas",
        modo=ModoCaso.EMERGENCIA,
        entidad="Alcaldía Municipal de prueba",
        nivel_atencion=nivel,
        senales=[
            Senal(
                codigo="S1",
                nombre="Empresa recién creada",
                nivel=nivel,
                regla_legible="Esta empresa se creó hace 2 meses y ya ganó un contrato.",
                datos_usados={},
                fuente=FUENTE,
            )
        ],
    )


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def _limpiar_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_nivel_bajo_no_llega_a_ningun_canal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "no-deberia-usarse")

    estado, _ = _run(enviar_alerta(_caso(NivelAtencion.BAJO), "123"))

    assert estado == "omitido"


def test_canal_telegram_por_defecto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LUMEN_CANAL_ALERTA", raising=False)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")  # forzamos error, no exito, para no gastar red

    estado, detalle = _run(enviar_alerta(_caso(NivelAtencion.ALTO), "123"))

    assert estado == "error"
    assert "TELEGRAM_BOT_TOKEN" in detalle


def test_canal_whatsapp_si_se_configura(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_CANAL_ALERTA", "whatsapp")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "")

    estado, detalle = _run(enviar_alerta(_caso(NivelAtencion.ALTO), "+573001112233"))

    assert estado == "error"
    assert "Twilio" in detalle
