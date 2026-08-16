"""Integración real con Croma. Se salta si no hay CROMA_API_KEY."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from lumen.config import get_settings
from lumen.main import app

NIT_CON_CONTRATOS = "79372917"  # 6 contratos reales en SECOP (docs Croma)
ENTIDAD_BOGOTA = "899999061"

cliente = TestClient(app)


def _hay_croma() -> bool:
    get_settings.cache_clear()
    return get_settings().croma_configurado


pytestmark = pytest.mark.skipif(not _hay_croma(), reason="CROMA_API_KEY vacía")


def test_analizar_proveedor_real_devuelve_caso():
    r = cliente.post("/analizar", json={"nit": NIT_CON_CONTRATOS})
    assert r.status_code == 200, r.text
    caso = r.json()
    assert caso["id"]
    assert caso["nivel_atencion"] in {"bajo", "medio", "alto"}
    assert "no es prueba de irregularidad" in caso["disclaimer"]
    for senal in caso["senales"]:
        assert senal["fuente"]["url_oficial"]
        assert senal["fuente"]["consultado_en"]
        assert "RUES" not in senal["regla_legible"]
        assert "SECOP" not in senal["regla_legible"]
        assert "BDME" not in senal["regla_legible"]


def test_red_del_mismo_nit_esta_curada():
    r = cliente.get(f"/red/{NIT_CON_CONTRATOS}")
    assert r.status_code == 200, r.text
    grafo = r.json()
    assert 1 <= len(grafo["nodos"]) <= 12
    for arista in grafo["aristas"]:
        assert arista["fuente"]


def test_analizar_entidad_real_no_explota():
    r = cliente.post("/analizar", json={"entidad_id": ENTIDAD_BOGOTA})
    assert r.status_code == 200, r.text
    assert r.json()["entidad"]
