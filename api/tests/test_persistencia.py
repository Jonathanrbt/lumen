"""La capa de persistencia de Caso. Dueno: Cristian (B3).

Estas pruebas existen porque `guardar_caso` no se habia ejecutado **ni una vez**
hasta que hubo proyecto de Supabase: un desajuste entre lo que `_a_fila`
produce y lo que la migracion define no se habria visto hasta las 3 de la
manana, en plena integracion.

El viaje completo (serializar -> jsonb -> reconstruir) se comprobo a mano
contra el proyecto real. Aqui se fija como regresion, con un cliente falso, para
que corra sin red y sin credenciales.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from lumen.contracts import Caso, NivelAtencion
from lumen.plataforma import casos as modulo_casos

RAIZ = Path(__file__).resolve().parents[2]
DUMP = RAIZ / "fixtures" / "casos_demo.json"

COLUMNAS_DE_LA_MIGRACION = {
    "id",
    "contrato_id",
    "modo",
    "nivel_atencion",
    "municipio",
    "departamento",
    "cuerpo",
}


def _un_caso() -> Caso:
    crudo = json.loads(DUMP.read_text(encoding="utf-8"))
    casos = crudo if isinstance(crudo, list) else crudo.get("casos", [])
    if not casos:
        pytest.skip("El dump no tiene casos")
    return Caso.model_validate(casos[0])


class _TablaFalsa:
    """Imita lo justo del cliente de Supabase: recuerda lo que le mandaron."""

    def __init__(self, registro: dict[str, Any], respuesta: list[dict[str, Any]]) -> None:
        self._registro = registro
        self._respuesta = respuesta

    def upsert(self, fila: dict[str, Any], **kwargs: Any) -> "_TablaFalsa":
        self._registro["upsert"] = fila
        self._registro["kwargs"] = kwargs
        return self

    def select(self, *_: Any) -> "_TablaFalsa":
        return self

    def eq(self, *_: Any) -> "_TablaFalsa":
        return self

    def limit(self, *_: Any) -> "_TablaFalsa":
        return self

    def execute(self) -> Any:
        return type("Respuesta", (), {"data": self._respuesta})()


class _SupabaseFalso:
    def __init__(self, registro: dict[str, Any], respuesta: list[dict[str, Any]]) -> None:
        self._registro = registro
        self._respuesta = respuesta

    def table(self, nombre: str) -> _TablaFalsa:
        self._registro["tabla"] = nombre
        return _TablaFalsa(self._registro, self._respuesta)


def test_la_fila_solo_usa_columnas_que_existen_en_la_migracion():
    """Si alguien añade un campo a `_a_fila` sin migrar, esto falla aquí y no en produccion."""
    fila = modulo_casos._a_fila(_un_caso())
    sobran = set(fila) - COLUMNAS_DE_LA_MIGRACION
    assert not sobran, f"columnas que no existen en la tabla `casos`: {sobran}"


def test_el_cuerpo_serializado_es_json_puro():
    """Va a una columna jsonb: no puede llevar datetime ni Enum de Python."""
    fila = modulo_casos._a_fila(_un_caso())
    json.dumps(fila["cuerpo"])  # revienta si quedó un objeto no serializable

    assert isinstance(fila["nivel_atencion"], str)
    assert isinstance(fila["modo"], str)


def test_guardar_caso_hace_upsert_por_id(monkeypatch: pytest.MonkeyPatch):
    registro: dict[str, Any] = {}
    monkeypatch.setattr(modulo_casos, "get_supabase", lambda: _SupabaseFalso(registro, []))

    caso = _un_caso()
    modulo_casos.guardar_caso(caso, contrato_id="CO1.NTC.123")

    assert registro["tabla"] == "casos"
    assert registro["upsert"]["id"] == caso.id
    assert registro["upsert"]["contrato_id"] == "CO1.NTC.123"
    # Sin on_conflict, un segundo barrido sobre la misma entidad reventaria por
    # clave duplicada en vez de actualizar el caso.
    assert registro["kwargs"].get("on_conflict") == "id"


def test_el_viaje_de_ida_y_vuelta_conserva_los_guardarrailes(monkeypatch: pytest.MonkeyPatch):
    """Serializar y reconstruir no puede perder la fuente ni convertir el nivel en numero.

    Se reordenan las claves a proposito: Postgres devuelve el jsonb en su
    propio orden, no en el que se escribio.
    """
    caso = _un_caso()
    cuerpo = modulo_casos._a_fila(caso)["cuerpo"]
    barajado = dict(reversed(list(cuerpo.items())))

    registro: dict[str, Any] = {}
    monkeypatch.setattr(
        modulo_casos,
        "get_supabase",
        lambda: _SupabaseFalso(registro, [{"cuerpo": barajado}]),
    )
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "false")
    from lumen.config import get_settings

    get_settings.cache_clear()
    try:
        recuperado = modulo_casos.obtener_caso(caso.id)
    finally:
        get_settings.cache_clear()

    assert recuperado is not None
    assert recuperado.id == caso.id
    assert isinstance(recuperado.nivel_atencion, NivelAtencion)
    assert all(s.fuente and s.fuente.consultado_en for s in recuperado.senales)
    assert "no es prueba de irregularidad" in recuperado.disclaimer
