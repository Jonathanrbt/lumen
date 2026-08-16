"""Barrido del Modo Emergencia. Dueno: Cristian (B3).

Sin red y sin credenciales: se sustituyen las piezas que salen al mundo
(Croma, Supabase, WhatsApp) y se comprueba la lógica que de verdad es de
plataforma — qué campo identifica un proceso, qué se descarta y qué tope
aplica.

El bug que estas pruebas existen para que no vuelva: el monitor buscaba
`id`/`contrato_id`/`numero_contrato`, campos que Croma no devuelve nunca, así
que descartaba todo en silencio y `/monitor/nuevos` respondía `[]` pareciendo
sano.
"""

from __future__ import annotations

import pytest

from lumen.plataforma import monitor


def test_la_llave_de_novedad_es_notice_uid():
    """Los procesos de entidad se identifican por `notice_uid`."""
    assert monitor._llave_de_novedad({"notice_uid": "CO1.NTC.123"}) == "CO1.NTC.123"


def test_la_llave_de_novedad_acepta_contract_id():
    """Si por este camino llega un contrato, su llave es `contract_id`."""
    assert monitor._llave_de_novedad({"contract_id": "CO1.PCCNTR.9"}) == "CO1.PCCNTR.9"


def test_un_proceso_sin_identificador_no_inventa_llave():
    """Antes se caía en `id`/`contrato_id`, que no existen en Croma."""
    assert monitor._llave_de_novedad({"base_price": 1000, "modality": "directa"}) is None


def test_se_elige_el_proceso_publicado_mas_tarde():
    procesos = [
        {"notice_uid": "a", "published_date": "2026-08-11"},
        {"notice_uid": "c", "published_date": "2026-08-15"},
        {"notice_uid": "b", "published_date": "2026-08-13"},
    ]
    assert monitor._mas_reciente(procesos)["notice_uid"] == "c"


def test_sin_fechas_no_revienta():
    procesos = [{"notice_uid": "a"}, {"notice_uid": "b"}]
    assert monitor._mas_reciente(procesos) is not None
    assert monitor._mas_reciente([]) is None


def test_found_false_es_lista_vacia_no_error():
    """`found: false` significa 'esta entidad no tiene procesos', no un fallo."""
    assert monitor._procesos_de({"found": False}) == []


def test_se_extraen_los_procesos_de_la_envoltura():
    datos = {"processes": [{"notice_uid": "a"}, {"notice_uid": "b"}], "found": True}
    assert len(monitor._procesos_de(datos)) == 2


@pytest.mark.anyio
async def test_sin_croma_configurado_falla_explicito(monkeypatch: pytest.MonkeyPatch):
    """Falta de credencial no se puede confundir con 'no encontré nada'."""
    from lumen.config import get_settings

    monkeypatch.setenv("CROMA_API_KEY", "")
    get_settings.cache_clear()
    try:
        with pytest.raises(Exception, match="CROMA_API_KEY"):
            await monitor.monitor_nuevos()
    finally:
        get_settings.cache_clear()
