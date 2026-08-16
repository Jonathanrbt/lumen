"""El interruptor de créditos de Croma.

`LUMEN_CROMA_HABILITADO=false` tiene que cortar **antes** de la red, no
después: si la petición sale y luego se descarta la respuesta, el crédito ya se
gastó. Por eso aquí no se comprueba "devuelve error", se comprueba que el
cliente HTTP no se llegó a usar.

El token de Croma es uno solo para las cuatro personas más el monitor.
"""

from __future__ import annotations

import pytest

from lumen.config import get_settings
from lumen.croma.client import CromaClient, CromaDeshabilitado, probar_conexion


@pytest.fixture(autouse=True)
def _limpiar_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.anyio
async def test_apagado_no_sale_ni_una_peticion(monkeypatch: pytest.MonkeyPatch):
    """Lo que se comprueba es que el POST nunca ocurre."""
    monkeypatch.setenv("LUMEN_CROMA_HABILITADO", "false")
    monkeypatch.setenv("CROMA_API_KEY", "loquesea")
    get_settings.cache_clear()

    llamadas = []

    async with CromaClient() as croma:
        async def _post_espia(*args, **kwargs):
            llamadas.append(args)
            raise AssertionError("salió una petición a Croma con el interruptor apagado")

        monkeypatch.setattr(croma._http, "post", _post_espia)

        with pytest.raises(CromaDeshabilitado):
            await croma.consultar("rues_entity_by_nit", {"document_number": "79372917"})

    assert llamadas == []


@pytest.mark.anyio
async def test_el_health_no_consulta_cuando_esta_apagado(monkeypatch: pytest.MonkeyPatch):
    """/health/croma hace una consulta real: abrirlo desde /docs gastaba créditos."""
    monkeypatch.setenv("LUMEN_CROMA_HABILITADO", "false")
    monkeypatch.setenv("CROMA_API_KEY", "loquesea")
    get_settings.cache_clear()

    resultado = await probar_conexion()

    assert resultado["estado"] == "desactivado"
    assert "créditos" in resultado["detalle"]


@pytest.mark.anyio
async def test_encendido_vuelve_a_intentar(monkeypatch: pytest.MonkeyPatch):
    """El interruptor no puede dejar el sistema roto para siempre.

    No se llama a Croma de verdad: se comprueba que ya no corta por
    configuración, sustituyendo el transporte.
    """
    monkeypatch.setenv("LUMEN_CROMA_HABILITADO", "true")
    monkeypatch.setenv("CROMA_API_KEY", "loquesea")
    get_settings.cache_clear()

    class _RespuestaFalsa:
        status_code = 200
        headers: dict[str, str] = {}
        content = b'{"data":{"found":true,"entities":[]}}'  # el cliente loguea su tamaño

        @staticmethod
        def json():
            return {"data": {"found": True, "entities": []}}

    async with CromaClient() as croma:
        async def _post(*args, **kwargs):
            return _RespuestaFalsa()

        monkeypatch.setattr(croma._http, "post", _post)
        datos = await croma.consultar("rues_entities_by_name", {"name": "x"})

    assert datos == {"found": True, "entities": []}


def test_por_defecto_viene_encendido():
    """Quien haga pull no debe encontrarse el backend mudo sin saber por qué.

    Se comprueba el valor por defecto del código, ignorando el `.env` local: en
    esta máquina está apagado a propósito, y eso no debe viajar al resto del
    equipo por el repo.
    """
    from lumen.config import Settings

    assert Settings(_env_file=None).lumen_croma_habilitado is True
