"""Pruebas del generador de artefactos (POST /accion). Dueno: Freddy (B2).

`paquete_evidencia`, `informe_veeduria` y `guia_denuncia` son plantillas en
Python (sin LLM, sin red): se prueban directo. `derecho_peticion` mockea
`preguntar` y fija el guardarraíl del disclaimer y la firma, que van fijos
en el código y no dependen de que el modelo los escriba.
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from lumen.config import get_settings
from lumen.contracts import Caso, Fuente, ModoCaso, NivelAtencion, Senal, TipoArtefacto
from lumen.ia import artefactos
from lumen.main import app
from lumen.plataforma.dump_local import limpiar_cache_de_dump

cliente = TestClient(app)
CASO_DUMP_ID = "caso-38d879c8695f"  # ver fixtures/casos_demo.json

FUENTE = Fuente(
    herramienta_croma="rues_entity_by_nit",
    url_oficial="https://www.rues.org.co/",
    consultado_en="2026-08-15T17:20:00-05:00",
)


def _caso() -> Caso:
    return Caso(
        id="caso-test-accion",
        modo=ModoCaso.EMERGENCIA,
        entidad="Alcaldía Municipal de prueba",
        municipio="Municipio de prueba",
        proveedor="Constructora de prueba S.A.S.",
        valor=4_200_000_000.0,
        objeto="Retiro de escombros",
        nivel_atencion=NivelAtencion.ALTO,
        senales=[
            Senal(
                codigo="S1",
                nombre="Empresa recién creada",
                nivel=NivelAtencion.ALTO,
                regla_legible="Esta empresa se creó hace 2 meses y ya ganó un contrato de $4.200 millones.",
                datos_usados={},
                fuente=FUENTE,
            )
        ],
    )


def _run(coro):
    return asyncio.run(coro)


def test_paquete_evidencia_lista_las_senales_con_fuente():
    artefacto = _run(artefactos.generar_artefacto(_caso(), TipoArtefacto.PAQUETE_EVIDENCIA))

    assert artefacto.tipo == TipoArtefacto.PAQUETE_EVIDENCIA
    assert "Esta empresa se creó hace 2 meses" in artefacto.cuerpo_markdown
    assert "rues_entity_by_nit" in artefacto.cuerpo_markdown
    assert "una señal no es prueba" in artefacto.cuerpo_markdown.lower()


def test_informe_veeduria_incluye_las_senales():
    artefacto = _run(artefactos.generar_artefacto(_caso(), TipoArtefacto.INFORME_VEEDURIA))

    assert artefacto.tipo == TipoArtefacto.INFORME_VEEDURIA
    assert "Esta empresa se creó hace 2 meses" in artefacto.cuerpo_markdown


def test_guia_denuncia_incluye_los_tres_canales():
    artefacto = _run(artefactos.generar_artefacto(_caso(), TipoArtefacto.GUIA_DENUNCIA))

    assert artefacto.tipo == TipoArtefacto.GUIA_DENUNCIA
    for canal in ["Procuraduría", "Contraloría", "Fiscalía"]:
        assert canal in artefacto.cuerpo_markdown


def test_derecho_peticion_siempre_lleva_disclaimer_y_firma_aunque_el_modelo_no_los_escriba(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _preguntar_falso(prompt: str, modelo) -> str:
        return """{
            "titulo": "Derecho de petición sobre el contrato",
            "salutacion_y_asunto": "Señor(a)\\n**Alcalde(sa)**\\nE. S. D.\\n\\n**Asunto:** prueba",
            "cuerpo": "Respetuosamente solicito informacion.\\n\\n**Hechos**\\n\\n1. Un hecho.\\n\\n**Peticiones**\\n\\n1. Una peticion.\\n\\n**Fundamento**\\n\\nUn parrafo."
        }"""

    monkeypatch.setattr(artefactos, "preguntar", _preguntar_falso)

    artefacto = _run(artefactos.generar_artefacto(_caso(), TipoArtefacto.DERECHO_PETICION))

    assert artefacto.tipo == TipoArtefacto.DERECHO_PETICION
    assert artefactos.DISCLAIMER_CARTA in artefacto.cuerpo_markdown
    assert "[Nombre y documento del peticionario]" in artefacto.cuerpo_markdown
    assert "Constitución Política, artículo 23" in artefacto.normas_citadas
    assert "Ley 1523 de 2012, artículo 46" in artefacto.normas_citadas  # caso es de emergencia
    assert artefacto.destinatario == "Alcaldía Municipal de prueba"
    assert artefacto.caso_id == "caso-test-accion"


def test_derecho_peticion_json_roto_no_tumba_silenciosamente(monkeypatch: pytest.MonkeyPatch) -> None:
    from lumen.ia.llm_client import LLMEjecucionError

    async def _preguntar_falso(prompt: str, modelo) -> str:
        return "esto no es JSON"

    monkeypatch.setattr(artefactos, "preguntar", _preguntar_falso)

    with pytest.raises(LLMEjecucionError):
        _run(artefactos.generar_artefacto(_caso(), TipoArtefacto.DERECHO_PETICION))


# --- Pruebas del endpoint completo, contra el dump local (sin red, sin Supabase) ---


@pytest.fixture(autouse=True)
def _limpiar_cachés_de_settings():
    get_settings.cache_clear()
    limpiar_cache_de_dump()
    yield
    get_settings.cache_clear()
    limpiar_cache_de_dump()


def test_accion_paquete_evidencia_contra_el_dump_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "true")

    r = cliente.post("/accion", json={"caso_id": CASO_DUMP_ID, "tipo": "paquete_evidencia"})

    assert r.status_code == 200, r.text
    assert r.json()["tipo"] == "paquete_evidencia"


def test_accion_caso_inexistente_da_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUMEN_USAR_DUMP_LOCAL", "true")

    r = cliente.post("/accion", json={"caso_id": "no-existe", "tipo": "paquete_evidencia"})

    assert r.status_code == 404
