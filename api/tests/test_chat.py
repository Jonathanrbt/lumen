"""Pruebas del agente conversacional (POST /chat). Dueno: Freddy (B2).

Mockea `resolver_candidatos`, `analizar` y `preguntar` — no pega contra
Croma ni Cursor de verdad. Fija las reglas no negociables del agente: nunca
se asume cuál es (ni con un solo candidato), siempre hay un siguiente paso,
y si la narración por LLM falla, se degrada a las señales tal cual en vez de
tumbar la respuesta.
"""

from __future__ import annotations

import asyncio

import pytest

from lumen.contracts import Candidato, Caso, Fuente, ModoCaso, NivelAtencion, Senal, TipoActor
from lumen.ia import chat

FUENTE = Fuente(
    herramienta_croma="rues_entity_by_nit",
    url_oficial="https://www.rues.org.co/",
    consultado_en="2026-08-15T17:20:00-05:00",
)


def _caso(nivel: NivelAtencion = NivelAtencion.ALTO) -> Caso:
    return Caso(
        id="caso-test-chat",
        modo=ModoCaso.VIGILANCIA,
        entidad="Alcaldía Municipal de prueba",
        proveedor="Constructora de prueba S.A.S.",
        valor=4_200_000_000.0,
        nivel_atencion=nivel,
        senales=[
            Senal(
                codigo="S1",
                nombre="Empresa recién creada",
                nivel=nivel,
                regla_legible="Esta empresa se creó hace 2 meses y ya ganó un contrato de $4.200 millones.",
                datos_usados={},
                fuente=FUENTE,
            )
        ],
    )


def _candidato(nombre: str = "CONSTRUCTORA DE PRUEBA S.A.S.") -> Candidato:
    return Candidato(nombre=nombre, nit="900000000", tipo=TipoActor.EMPRESA)


def _run(coro):
    return asyncio.run(coro)


async def _preguntar_falso(prompt: str, modelo) -> str:
    return "Narración de prueba en lenguaje ciudadano."


def test_sin_candidatos_dice_no_se_con_alternativa(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _resolver_falso(texto: str):
        return []

    monkeypatch.setattr(chat, "resolver_candidatos", _resolver_falso)

    resultado = _run(chat.responder_chat("una empresa que no existe"))

    assert resultado.caso is None
    assert resultado.candidatos is None
    assert resultado.siguientes_pasos  # nunca se deja sin salida
    assert "No encontré" in resultado.narracion


def test_un_solo_candidato_no_se_asume_se_confirma(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _resolver_falso(texto: str):
        return [_candidato()]

    monkeypatch.setattr(chat, "resolver_candidatos", _resolver_falso)

    resultado = _run(chat.responder_chat("Conalvias"))

    assert resultado.caso is None  # no se analiza a ciegas con un solo match
    assert resultado.candidatos is not None
    assert len(resultado.candidatos) == 1
    assert "¿Es este?" in resultado.narracion


def test_varios_candidatos_se_muestran_todos(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _resolver_falso(texto: str):
        return [_candidato("A"), _candidato("B"), _candidato("C")]

    monkeypatch.setattr(chat, "resolver_candidatos", _resolver_falso)

    resultado = _run(chat.responder_chat("Conalvias"))

    assert resultado.candidatos is not None
    assert len(resultado.candidatos) == 3


def test_contexto_con_nit_analiza_directo_sin_volver_a_preguntar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llamadas = {}

    async def _analizar_falso(peticion):
        llamadas["nit"] = peticion.nit
        return _caso()

    monkeypatch.setattr(chat, "analizar", _analizar_falso)
    monkeypatch.setattr(chat, "preguntar", _preguntar_falso)

    resultado = _run(chat.responder_chat("sí, esa", contexto={"nit": "900000000"}))

    assert llamadas["nit"] == "900000000"
    assert resultado.caso is not None
    assert resultado.candidatos is None
    assert resultado.narracion == "Narración de prueba en lenguaje ciudadano."
    assert "Redactar un derecho de petición" in resultado.siguientes_pasos  # nivel alto


def test_nivel_bajo_no_sugiere_derecho_de_peticion(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _analizar_falso(peticion):
        return _caso(NivelAtencion.BAJO)

    monkeypatch.setattr(chat, "analizar", _analizar_falso)
    monkeypatch.setattr(chat, "preguntar", _preguntar_falso)

    resultado = _run(chat.responder_chat("x", contexto={"nit": "900000000"}))

    assert "Redactar un derecho de petición" not in resultado.siguientes_pasos


def test_narracion_se_degrada_si_el_llm_falla_no_tumba_la_respuesta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from lumen.ia.llm_client import LLMEjecucionError

    async def _analizar_falso(peticion):
        return _caso()

    async def _preguntar_roto(prompt: str, modelo):
        raise LLMEjecucionError("el modelo no respondio")

    monkeypatch.setattr(chat, "analizar", _analizar_falso)
    monkeypatch.setattr(chat, "preguntar", _preguntar_roto)

    resultado = _run(chat.responder_chat("x", contexto={"nit": "900000000"}))

    assert resultado.caso is not None
    assert "creó hace 2 meses" in resultado.narracion  # cae a la señal tal cual
    assert "corrupto" not in resultado.narracion.lower()
    assert "ilegal" not in resultado.narracion.lower()
