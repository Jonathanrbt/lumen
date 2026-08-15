"""Prueba de humo de la API.

Comprueba que la app levanta, que los nueve endpoints estan registrados y que
cada uno sigue perteneciendo a quien dice `docs/PLAN.md`. Si alguien renombra una
ruta sin avisar, esto falla y lo vemos antes de la integracion.

No toca Croma ni Supabase: corre sin `.env` y sin red.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from lumen.main import app

cliente = TestClient(app)

RUTAS_ESPERADAS = {
    # ruta: dueno
    "/analizar": "Jonatin (B1)",
    "/red/{nit}": "Jonatin (B1)",
    "/resolver": "Freddy (B2)",
    "/justificacion": "Freddy (B2)",
    "/accion": "Freddy (B2)",
    "/chat": "Freddy (B2)",
    "/caso/{caso_id}": "Cristian (B3)",
    "/monitor/nuevos": "Cristian (B3)",
    "/alerta": "Cristian (B3)",
}


def test_health_responde():
    r = cliente.get("/health")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"


def test_estan_los_nueve_endpoints_del_contrato():
    registradas = set(app.openapi()["paths"])
    faltan = set(RUTAS_ESPERADAS) - registradas
    assert not faltan, f"faltan rutas del contrato §5.5: {sorted(faltan)}"


def test_los_endpoints_sin_implementar_dicen_de_quien_son():
    """Un 501 con el nombre del dueño ahorra una pregunta en el chat."""
    r = cliente.post("/analizar", json={"nit": "901000000"})
    assert r.status_code == 501
    assert "Jonatin" in r.json()["detail"]


def test_analizar_exige_al_menos_una_llave():
    r = cliente.post("/analizar", json={})
    assert r.status_code == 422
