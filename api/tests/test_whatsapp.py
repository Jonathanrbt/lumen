"""Pruebas del canal de WhatsApp. Dueno: Freddy (B2).

No pegan contra Twilio ni Evolution API de verdad: comprueban el guardarrail
que no se negocia (nunca se fabrica un 'enviado') y que el proveedor se
selecciona con `LUMEN_WHATSAPP_PROVIDER` sin tocar el router de Cristian.
"""

from __future__ import annotations

import asyncio

import pytest

from lumen.config import get_settings
from lumen.contracts import Caso, Fuente, ModoCaso, NivelAtencion, Senal
from lumen.whatsapp import enviar_alerta
from lumen.whatsapp.copy import MAX_LINEAS, armar_mensaje

FUENTE = Fuente(
    herramienta_croma="rues_entity_by_nit",
    url_oficial="https://www.rues.org.co/",
    consultado_en="2026-08-15T17:20:00-05:00",
)


def _caso(nivel: NivelAtencion, valor: float | None = 4_200_000_000.0) -> Caso:
    return Caso(
        id="caso-test-0001",
        modo=ModoCaso.EMERGENCIA,
        entidad="Alcaldía Municipal de prueba",
        municipio="Municipio de prueba",
        valor=valor,
        nivel_atencion=nivel,
        senales=[
            Senal(
                codigo="S1",
                nombre="Empresa recién creada",
                nivel=nivel,
                regla_legible="Esta empresa se creó hace 2 meses y ya ganó un contrato de $4.200 millones.",
                datos_usados={},
                fuente=FUENTE,
            )
        ],
    )


@pytest.fixture(autouse=True)
def _limpiar_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_nivel_bajo_se_omite_sin_llamar_a_ningun_proveedor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "no-deberia-usarse")
    caso = _caso(NivelAtencion.BAJO)

    estado, detalle = _run_async(enviar_alerta(caso, "+573001112233"))

    assert estado == "omitido"
    assert detalle


def test_twilio_sin_configurar_nunca_dice_enviado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_WHATSAPP_PROVIDER", "twilio")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "")
    monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "")
    caso = _caso(NivelAtencion.ALTO)

    estado, detalle = _run_async(enviar_alerta(caso, "+573001112233"))

    assert estado == "error"
    assert estado != "enviado"
    assert "Twilio" in detalle


def test_evolution_sin_configurar_nunca_dice_enviado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_WHATSAPP_PROVIDER", "evolution")
    monkeypatch.setenv("EVOLUTION_API_URL", "")
    monkeypatch.setenv("EVOLUTION_API_KEY", "")
    monkeypatch.setenv("EVOLUTION_INSTANCE", "")
    caso = _caso(NivelAtencion.ALTO)

    estado, detalle = _run_async(enviar_alerta(caso, "+573001112233"))

    assert estado == "error"
    assert estado != "enviado"
    assert "Evolution" in detalle


def test_mensaje_respeta_las_cinco_lineas_y_lleva_el_disclaimer() -> None:
    caso = _caso(NivelAtencion.ALTO)

    mensaje = armar_mensaje(caso)
    lineas = mensaje.splitlines()

    assert len(lineas) <= MAX_LINEAS
    assert "no es prueba de irregularidad" in mensaje
    assert caso.senales[0].regla_legible in mensaje


def _run_async(coro):
    import asyncio

    return asyncio.run(coro)
