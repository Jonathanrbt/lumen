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

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from lumen.contracts import Caso
from lumen.plataforma import monitor

RAIZ = Path(__file__).resolve().parents[2]
DUMP = RAIZ / "fixtures" / "casos_demo.json"


def _un_caso() -> Caso:
    crudo = json.loads(DUMP.read_text(encoding="utf-8"))
    casos = crudo if isinstance(crudo, list) else crudo.get("casos", [])
    if not casos:
        pytest.skip("El dump no tiene casos")
    return Caso.model_validate(casos[0])


class _CromaFalso:
    """El barrido abre un `CromaClient`; aquí nadie sale a la red."""

    async def __aenter__(self) -> "_CromaFalso":
        return self

    async def __aexit__(self, *_: Any) -> bool:
        return False


@pytest.fixture
def barrido_de_una_entidad(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    """Un barrido sin red: una entidad, un proceso, y registro de lo que pasó."""
    from lumen.config import get_settings

    registro: dict[str, Any] = {"analizados": [], "guardados": [], "avisados": []}

    monkeypatch.setenv("CROMA_API_KEY", "llave-de-prueba")
    get_settings.cache_clear()

    monkeypatch.setattr(
        monitor, "ENTIDADES_EMERGENCIA", [{"nombre": "Gobernación del Chocó", "nit": "891680010"}]
    )
    monkeypatch.setattr(monitor, "CromaClient", _CromaFalso)

    async def _procesos(*_: Any, **__: Any) -> list[dict[str, Any]]:
        return [{"notice_uid": "CO1.NTC.10708619", "published_date": "2026-08-14"}]

    monkeypatch.setattr(monitor, "_procesos_de_entidad", _procesos)

    async def _analizar(peticion: Any) -> Caso:
        registro["analizados"].append(peticion.entidad_id)
        return _un_caso()

    monkeypatch.setattr(monitor, "analizar", _analizar)
    monkeypatch.setattr(
        monitor,
        "guardar_caso",
        lambda caso, **kwargs: registro["guardados"].append((caso.id, kwargs.get("contrato_id"))),
    )

    async def _avisar(caso: Caso) -> None:
        registro["avisados"].append(caso.id)

    monkeypatch.setattr(monitor, "_avisar_si_corresponde", _avisar)
    yield registro
    get_settings.cache_clear()


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
async def test_un_contrato_ya_visto_devuelve_el_caso_guardado(
    monkeypatch: pytest.MonkeyPatch, barrido_de_una_entidad: dict[str, Any]
):
    """El bug del que nace `forzar`: la segunda consulta se quedaba en `[]`.

    "Gobernación del Chocó (891680010): sin actividad nueva (CO1.NTC.10708619
    ya visto)" — la entidad tiene un caso perfectamente consultable y el
    monitor lo escondía. Ahora lo devuelve, sin re-analizar ni volver a avisar.
    """
    guardado = _un_caso()
    monkeypatch.setattr(monitor, "caso_de_contrato", lambda _: guardado)

    casos = await monitor.monitor_nuevos()

    assert [c.id for c in casos] == [guardado.id]
    assert barrido_de_una_entidad["analizados"] == []  # no se gastó cuota de Croma
    assert barrido_de_una_entidad["avisados"] == []  # ni se repitió la alerta


@pytest.mark.anyio
async def test_forzar_reanaliza_aunque_el_contrato_ya_este_en_base(
    monkeypatch: pytest.MonkeyPatch, barrido_de_una_entidad: dict[str, Any]
):
    monkeypatch.setattr(monitor, "caso_de_contrato", lambda _: _un_caso())

    casos = await monitor.monitor_nuevos(forzar=True)

    assert len(casos) == 1
    assert barrido_de_una_entidad["analizados"] == ["891680010"]
    assert barrido_de_una_entidad["guardados"] == [(casos[0].id, "CO1.NTC.10708619")]
    assert barrido_de_una_entidad["avisados"] == [casos[0].id]


@pytest.mark.anyio
async def test_un_contrato_nuevo_se_analiza_y_se_avisa(
    monkeypatch: pytest.MonkeyPatch, barrido_de_una_entidad: dict[str, Any]
):
    """El camino de siempre no cambia: sin caso en base, se analiza y se guarda."""
    monkeypatch.setattr(monitor, "caso_de_contrato", lambda _: None)

    casos = await monitor.monitor_nuevos()

    assert len(casos) == 1
    assert barrido_de_una_entidad["analizados"] == ["891680010"]
    assert barrido_de_una_entidad["guardados"] == [(casos[0].id, "CO1.NTC.10708619")]
    assert barrido_de_una_entidad["avisados"] == [casos[0].id]


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
