"""Pruebas de la capa de plataforma. Dueno: Cristian (B3).

Corren sin red y sin credenciales: usan el respaldo de dump local
(`LUMEN_USAR_DUMP_LOCAL=true`) para `/caso` y `/alerta`, y comprueban que
`/monitor/nuevos` falla de forma explícita (503) en vez de un 500 ciego
cuando Croma no está configurado. Nada de esto sustituye probar contra los
servicios reales, pero prueba las dos promesas que sí puede probar sin ellos:
los guardarraíles del contrato se conservan, y nunca se fabrica un éxito.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from lumen.config import get_settings
from lumen.main import app
from lumen.plataforma.dump_local import limpiar_cache_de_dump

cliente = TestClient(app)

RAIZ = Path(__file__).resolve().parents[2]
DUMP = RAIZ / "fixtures" / "casos_demo.json"


def _casos_del_dump() -> list[dict]:
    crudo = json.loads(DUMP.read_text(encoding="utf-8"))
    return crudo if isinstance(crudo, list) else crudo.get("casos", [])


def _un_caso_con_senales() -> dict:
    """Un caso del dump que tenga al menos una señal.

    No se fija un id a mano: el dump se regenera con
    `scripts/precomputar_casos_demo.py` y los ids cambian con los datos reales,
    así que hardcodearlos hace que estas pruebas fallen cada vez que alguien
    actualiza el respaldo de grabación.
    """
    casos = _casos_del_dump()
    con_senales = [c for c in casos if c.get("senales")]
    if not con_senales:
        pytest.skip("El dump no trae ningún caso con señales todavía")
    return con_senales[0]


CASO_DUMP_ID = (_casos_del_dump() or [{}])[0].get("id", "sin-casos-en-el-dump")


@pytest.fixture(autouse=True)
def _limpiar_cachés_de_settings():
    """`get_settings` y el dump local usan `lru_cache`: sin esto, un test que
    cambia el entorno con `monkeypatch.setenv` seguiría viendo los valores del
    test anterior."""
    get_settings.cache_clear()
    limpiar_cache_de_dump()
    yield
    get_settings.cache_clear()
    limpiar_cache_de_dump()


def test_caso_local_respeta_los_guardarrailes_del_contrato(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "true")
    esperado = _un_caso_con_senales()

    r = cliente.get(f"/caso/{esperado['id']}")

    assert r.status_code == 200
    caso = r.json()
    assert caso["senales"], "un caso sin señales no le sirve a nadie"
    assert all(s["fuente"] for s in caso["senales"]), "Senal no se puede construir sin fuente"
    assert caso["nivel_atencion"] in {"bajo", "medio", "alto"}
    assert "no es prueba de irregularidad" in caso["disclaimer"]


def test_caso_local_desconocido_da_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "true")

    r = cliente.get("/caso/no-existe")

    assert r.status_code == 404


def test_caso_sin_supabase_ni_dump_da_503_explicito(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin Supabase configurado y sin el flag de dump, el endpoint no puede
    responder — pero tiene que decirlo con un 503 claro, no reventar con un 500."""
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "false")
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "")

    r = cliente.get(f"/caso/{CASO_DUMP_ID}")

    assert r.status_code == 503
    assert "SUPABASE" in r.json()["detail"]


def test_alerta_nunca_dice_enviado_sin_twilio_configurado(monkeypatch: pytest.MonkeyPatch) -> None:
    """Guardarraíl de `plataforma/alertas-whatsapp`: sin Twilio configurado, el
    estado tiene que ser 'error', jamás 'enviado' fabricado."""
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "true")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "")
    monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "")

    r = cliente.post(
        "/alerta", json={"caso_id": CASO_DUMP_ID, "destinatario": "+573001112233"}
    )

    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["estado"] == "error"
    assert cuerpo["estado"] != "enviado"


def test_alerta_para_caso_inexistente_da_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "true")

    r = cliente.post("/alerta", json={"caso_id": "no-existe", "destinatario": "+573001112233"})

    assert r.status_code == 404


def test_monitor_sin_croma_configurado_da_503_explicito(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CROMA_API_KEY", "")

    r = cliente.get("/monitor/nuevos")

    assert r.status_code == 503
    assert "Croma" in r.json()["detail"]
