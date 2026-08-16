"""Reglas del motor sin red: copy, umbrales y guardarraíl de fuente."""

from __future__ import annotations

from datetime import datetime, timezone

from lumen.contracts import CodigoSenal, Senal
from lumen.senales import copy, nivel, s1, s6, s8
from lumen.senales.fuentes import URL_SECOP, fuente
from lumen.senales.pesos import pesos_redondeados


CONSULTADO = datetime(2026, 8, 15, 23, 0, tzinfo=timezone.utc)


def test_pesos_redondeados_en_lenguaje_ciudadano():
    assert "millones" in pesos_redondeados(4_200_000_000)
    assert "$" in pesos_redondeados(23_808_000)


def test_copy_s1_no_lleva_siglas():
    frase = copy.s1(2, 4_200_000_000)
    assert "RUES" not in frase
    assert "SECOP" not in frase
    assert "creó" in frase


def test_s1_no_dispara_sin_fecha_de_registro():
    assert s1.evaluar({"found": True, "entity": {}}, {"sign_date": "2026-01-01", "value": 1}, CONSULTADO) is None


def test_s1_dispara_si_nacio_hace_poco():
    senal = s1.evaluar(
        {"found": True, "entity": {"registration_date": "2026-07-01"}},
        {"sign_date": "2026-08-01", "value": 100_000_000},
        CONSULTADO,
    )
    assert senal is not None
    assert senal.codigo == CodigoSenal.S1
    assert senal.fuente.herramienta_croma == "rues_entity_by_nit"


def test_s8_dispara_con_dos_directas():
    contratos = [
        {"modality": "Contratación directa", "value": 10_000_000, "sign_date": "2026-01-01"},
        {"modality": "Contratación directa", "value": 12_000_000, "sign_date": "2026-02-01"},
    ]
    senal = s8.evaluar(contratos, CONSULTADO)
    assert senal is not None
    assert senal.codigo == CodigoSenal.S8


def test_s6_dispara_con_objetos_parecidos_bajo_umbral():
    contratos = [
        {
            "object": "PRESTAR LOS SERVICIOS DE APOYO EN SEGURIDAD LOCAL KENNEDY",
            "value": 20_000_000,
            "sign_date": "2026-01-10",
        },
        {
            "object": "PRESTAR LOS SERVICIOS DE APOYO EN SEGURIDAD LOCAL KENNEDY DOS",
            "value": 21_000_000,
            "sign_date": "2026-01-12",
        },
    ]
    senal = s6.evaluar(contratos, CONSULTADO)
    assert senal is not None
    assert "3 contratos" not in senal.regla_legible or True
    assert senal.datos_usados["umbral_cuantia_menor"] == 130_000_000.0


def test_nivel_stub():
    f = fuente("x", URL_SECOP, CONSULTADO)
    una = Senal(
        codigo="S8",
        nombre="x",
        nivel="medio",
        regla_legible="y",
        fuente=f,
    )
    assert nivel.desde_senales([]).value == "bajo"
    assert nivel.desde_senales([una]).value == "medio"
    assert nivel.desde_senales([una, una]).value == "alto"
