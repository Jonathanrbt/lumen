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


@pytest.fixture(autouse=True)
def _no_tocar_supabase_de_verdad(monkeypatch: pytest.MonkeyPatch):
    """`guardar_caso` no está mockeada por defecto en la mayoría de estos
    tests. Sin este fixture, cualquier test que llegue a `caso is not None`
    dispara un `get_supabase()` real -- y como esa función tiene su propio
    `@lru_cache` que nadie limpia entre tests, un `.env` local con
    credenciales de Supabase (aunque sean inválidas) queda cacheado y
    contamina tests de OTROS archivos que corran después en la misma
    sesión de pytest. Confirmado en vivo (16.ago ~03:15): rompía
    test_plataforma.py::test_caso_sin_supabase_ni_dump_da_503_explicito.
    Los dos tests que sí quieren probar el guardado real de otra forma
    sobreescriben este mock localmente.

    Desde el 16.ago la lista es de dos: `obtener_caso` entró por la misma
    puerta cuando `_caso_cacheado` empezó a preguntarle a Supabase si el caso
    ya existía antes de re-analizarlo. Devuelve None por defecto — "no hay
    nada cacheado" — que es el camino que estos tests quieren probar."""
    monkeypatch.setattr(chat, "guardar_caso", lambda caso: None)
    monkeypatch.setattr(chat, "obtener_caso", lambda caso_id: None)


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


def test_la_narracion_queda_dentro_del_caso_que_se_guarda(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si la narración vive solo en la respuesta del chat, al reabrir la ficha
    por `/caso/{id}` el párrafo desaparece: `FichaCaso` solo lo pinta cuando
    `caso.narracion` existe, y el motor siempre lo deja en None."""
    guardados = []

    async def _analizar_falso(peticion):
        return _caso()

    monkeypatch.setattr(chat, "analizar", _analizar_falso)
    monkeypatch.setattr(chat, "preguntar", _preguntar_falso)
    monkeypatch.setattr(chat, "guardar_caso", guardados.append)

    resultado = _run(chat.responder_chat("sí, esa", contexto={"nit": "900000000"}))

    assert resultado.caso is not None
    assert resultado.caso.narracion == "Narración de prueba en lenguaje ciudadano."
    assert guardados and guardados[0].narracion == resultado.caso.narracion


def test_un_caso_ya_cacheado_no_re_analiza_ni_vuelve_a_narrar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Brief §4.6, Flujo B paso 4: "si el caso ya está cacheado en Supabase,
    responde al instante". Un análisis por NIT tarda 80-100 s contra Croma y
    una narración cuesta presupuesto de Cursor: con el caso en la base, ni lo
    uno ni lo otro debe pasar."""

    async def _analizar_prohibido(peticion):
        raise AssertionError("no se debe re-analizar un caso que ya está en Supabase")

    async def _preguntar_prohibido(prompt, modelo):
        raise AssertionError("no se debe volver a narrar un caso que ya trae narración")

    cacheado = _caso().model_copy(update={"narracion": "Lo que ya se había narrado."})

    monkeypatch.setattr(chat, "analizar", _analizar_prohibido)
    monkeypatch.setattr(chat, "preguntar", _preguntar_prohibido)
    monkeypatch.setattr(chat, "obtener_caso", lambda caso_id: cacheado)

    resultado = _run(chat.responder_chat("sí, esa", contexto={"nit": "900000000"}))

    assert resultado.narracion == "Lo que ya se había narrado."
    assert resultado.caso is not None and resultado.caso.id == cacheado.id


def test_si_supabase_falla_el_cache_no_tumba_el_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    """El caché es un atajo, no un requisito: si la consulta revienta, se sigue
    por el camino largo."""

    def _obtener_roto(caso_id: str):
        raise RuntimeError("Supabase caída")

    async def _analizar_falso(peticion):
        return _caso()

    monkeypatch.setattr(chat, "obtener_caso", _obtener_roto)
    monkeypatch.setattr(chat, "analizar", _analizar_falso)
    monkeypatch.setattr(chat, "preguntar", _preguntar_falso)

    resultado = _run(chat.responder_chat("sí, esa", contexto={"nit": "900000000"}))

    assert resultado.caso is not None


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


def test_caso_analizado_se_guarda_para_que_accion_lo_pueda_encontrar_despues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Confirmado en vivo (16.ago ~03:00): sin esto, /accion sobre un caso
    que /chat acaba de descubrir siempre daba 404 -- el caso nunca quedaba
    en ningún lado. Este test fija que responder_chat SIEMPRE intenta
    guardarlo cuando analiza uno nuevo."""
    guardados = []

    async def _analizar_falso(peticion):
        return _caso()

    monkeypatch.setattr(chat, "analizar", _analizar_falso)
    monkeypatch.setattr(chat, "preguntar", _preguntar_falso)
    monkeypatch.setattr(chat, "guardar_caso", guardados.append)

    resultado = _run(chat.responder_chat("x", contexto={"nit": "900000000"}))

    assert len(guardados) == 1
    assert guardados[0].id == resultado.caso.id


def test_si_guardar_el_caso_falla_la_respuesta_del_chat_no_se_cae(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """guardar_caso no respeta LUMEN_USAR_DUMP_LOCAL (a diferencia de
    obtener_caso): en modo respaldo de grabación, sin Supabase real, esto
    va a fallar siempre. Tiene que ser best-effort, nunca tumbar /chat."""

    async def _analizar_falso(peticion):
        return _caso()

    def _guardar_roto(caso):
        raise RuntimeError("Supabase no configurado")

    monkeypatch.setattr(chat, "analizar", _analizar_falso)
    monkeypatch.setattr(chat, "preguntar", _preguntar_falso)
    monkeypatch.setattr(chat, "guardar_caso", _guardar_roto)

    resultado = _run(chat.responder_chat("x", contexto={"nit": "900000000"}))

    assert resultado.caso is not None
    assert resultado.narracion
