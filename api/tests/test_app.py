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


def test_los_endpoints_de_ia_sin_implementar_dicen_de_quien_son():
    """Un 501 con el nombre del dueño ahorra una pregunta en el chat.

    `/resolver`, `/justificacion` y `/accion` ya no están en 501 (ver
    docs/handoff/FREDDY-B2.md) — tienen sus propias pruebas en
    test_resolver.py, test_lector.py y test_artefactos.py. `/chat` es lo
    único que sigue pendiente.
    """
    r = cliente.post("/chat", json={"mensaje": "hola"})
    assert r.status_code == 501
    assert "Freddy" in r.json()["detail"]


def test_analizar_exige_al_menos_una_llave():
    r = cliente.post("/analizar", json={})
    assert r.status_code == 422
