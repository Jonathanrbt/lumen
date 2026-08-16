"""Pruebas del servidor MCP. Dueno: Cristian (B3).

Corren sin `.env` util y sin red: las variables que importan se fijan con
`monkeypatch` y `get_settings.cache_clear()`, igual que en
`test_croma_interruptor.py`.

Dos cosas del SDK condicionan como estan escritas, y conviene saberlas antes de
tocar nada:

1. **El gestor de sesiones solo se puede arrancar una vez por instancia**
   (`StreamableHTTPSessionManager.run()` lo dice y lo comprueba). `servidor_mcp`
   es un singleton de modulo, asi que en toda la suite puede haber **un solo**
   `with TestClient(app)`. De ahi el fixture de modulo `cliente_mcp`.

2. **Los rechazos del guardia no necesitan lifespan.** Un `TestClient` sin
   `with` no arranca el transporte, asi que los tests de auth de abajo prueban
   ademas, gratis, que el guardia corta ANTES de tocar el transporte.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from lumen.config import get_settings
from lumen.croma.client import CromaDeshabilitado, CromaError
from lumen.ia.llm_client import CursorAgentError, LLMEjecucionError
from lumen.main import app
from lumen.mcp import servidor_mcp
from lumen.mcp.auth import MENSAJE_APAGADO, MENSAJE_SIN_TOKEN
from lumen.mcp.herramientas import traducir_error
from lumen.mcp.instrucciones import INSTRUCCIONES_SERVIDOR
from lumen.plataforma.supabase_client import SupabaseNoConfigurado

TOKEN = "token-de-prueba-no-es-un-secreto"

CABECERAS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}
AUTORIZADAS = {**CABECERAS, "Authorization": f"Bearer {TOKEN}"}

HERRAMIENTAS_ESPERADAS = {
    "resolver_entidad",
    "analizar_entidad",
    "ver_red_de_actores",
    "obtener_caso",
    "leer_justificacion_urgencia",
    "generar_artefacto",
    "contratos_nuevos_del_monitor",
    "enviar_alerta",
    "estado_del_sistema",
}

PROMPTS_ESPERADOS = {"buscar_empresa", "revisar_entidad_publica", "revisar_justificacion"}

# Las mismas nueve de `test_app.py`. Se repiten aqui a proposito: este archivo
# tiene que fallar si montar el MCP se lleva por delante el contrato.
RUTAS_DEL_CONTRATO = {
    "/analizar",
    "/red/{nit}",
    "/resolver",
    "/justificacion",
    "/accion",
    "/chat",
    "/caso/{caso_id}",
    "/monitor/nuevos",
    "/alerta",
}


@pytest.fixture
def con_token(monkeypatch: pytest.MonkeyPatch):
    """Servidor encendido y con credencial."""
    monkeypatch.setenv("LUMEN_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("LUMEN_MCP_HABILITADO", "true")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# --- El montaje no rompe nada ----------------------------------------------


def test_health_sigue_respondiendo_con_el_mcp_montado():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"


def test_los_nueve_endpoints_del_contrato_siguen_registrados():
    registradas = set(app.openapi()["paths"])
    faltan = RUTAS_DEL_CONTRATO - registradas
    assert not faltan, f"montar el MCP se llevó rutas del contrato: {sorted(faltan)}"


def test_mcp_no_aparece_en_el_openapi_del_contrato():
    """El MCP es otro protocolo, no un endpoint REST. Que no ensucie el
    contrato que Andrew lee para construir el frontend."""
    assert not [r for r in app.openapi()["paths"] if r.startswith("/mcp")]


def test_las_dos_formas_de_la_url_estan_registradas_sin_redireccion():
    """`/mcp` y `/mcp/` tienen que ser rutas exactas. Si alguien lo cambia por
    un `app.mount`, `/mcp` vuelve a responder 307 y hay clientes que sueltan la
    cabecera Authorization al redirigir."""
    rutas = {getattr(r, "path", None) for r in app.router.routes}
    assert {"/mcp", "/mcp/"} <= rutas


# --- El guardia -------------------------------------------------------------


def test_sin_cabecera_de_autorizacion_responde_401(con_token):
    r = TestClient(app).post("/mcp", headers=CABECERAS, json={})
    assert r.status_code == 401
    assert "Bearer" in r.headers.get("www-authenticate", "")


def test_con_token_equivocado_responde_401(con_token):
    cabeceras = {**CABECERAS, "Authorization": "Bearer otro-token"}
    r = TestClient(app).post("/mcp", headers=cabeceras, json={})
    assert r.status_code == 401


def test_sin_token_configurado_responde_503_y_no_queda_abierto(monkeypatch: pytest.MonkeyPatch):
    """El fallo mas facil de provocar: olvidar la variable en Render. Un /mcp
    abierto es la cuota de Croma de los cuatro expuesta a internet."""
    monkeypatch.setenv("LUMEN_MCP_TOKEN", "")
    monkeypatch.setenv("LUMEN_MCP_HABILITADO", "true")
    get_settings.cache_clear()
    try:
        r = TestClient(app).post("/mcp", headers=AUTORIZADAS, json={})
        assert r.status_code == 503
        assert r.json()["detail"] == MENSAJE_SIN_TOKEN
    finally:
        get_settings.cache_clear()


def test_con_el_interruptor_apagado_responde_503_aunque_el_token_sea_correcto(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("LUMEN_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("LUMEN_MCP_HABILITADO", "false")
    get_settings.cache_clear()
    try:
        r = TestClient(app).post("/mcp", headers=AUTORIZADAS, json={})
        assert r.status_code == 503
        assert r.json()["detail"] == MENSAJE_APAGADO
    finally:
        get_settings.cache_clear()


def test_el_interruptor_apagado_no_afecta_al_resto_del_servicio(monkeypatch: pytest.MonkeyPatch):
    """Es el rollback sin redesplegar: /mcp cae, la API sigue."""
    monkeypatch.setenv("LUMEN_MCP_HABILITADO", "false")
    get_settings.cache_clear()
    try:
        cliente = TestClient(app)
        assert cliente.post("/mcp", headers=AUTORIZADAS, json={}).status_code == 503
        assert cliente.get("/health").status_code == 200
    finally:
        get_settings.cache_clear()


def test_un_rechazo_no_dispara_ni_croma_ni_el_llm(con_token, monkeypatch: pytest.MonkeyPatch):
    """El guardia corta antes del transporte, así que una petición sin
    credencial no puede gastar cuota compartida."""
    llamadas: list[str] = []

    from lumen.mcp import herramientas

    async def _espia_resolver(texto):  # noqa: ANN001, ANN202
        llamadas.append("resolver")
        return []

    async def _espia_analizar(peticion):  # noqa: ANN001, ANN202
        llamadas.append("analizar")

    monkeypatch.setattr(herramientas, "resolver_candidatos", _espia_resolver)
    monkeypatch.setattr(herramientas, "_analizar", _espia_analizar)

    peticion = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "resolver_entidad", "arguments": {"texto": "Conalvías"}},
    }
    r = TestClient(app).post("/mcp", headers=CABECERAS, json=peticion)

    assert r.status_code == 401
    assert llamadas == []


# --- El inventario y las instrucciones --------------------------------------


@pytest.mark.anyio
async def test_estan_las_nueve_herramientas_con_su_nombre():
    nombres = {h.name for h in await servidor_mcp.list_tools()}
    assert nombres == HERRAMIENTAS_ESPERADAS


@pytest.mark.anyio
async def test_no_hay_ninguna_herramienta_que_envuelva_el_chat():
    """El agente conectado es el conversador. Envolver /chat sería un LLM
    dentro de otro, narrando dos veces y pagando el modelo dos veces."""
    herramientas = await servidor_mcp.list_tools()
    assert not [h for h in herramientas if "chat" in h.name.lower()]
    for herramienta in herramientas:
        propiedades = (herramienta.input_schema or {}).get("properties", {})
        assert "mensaje" not in propiedades, (
            f"'{herramienta.name}' recibe un mensaje conversacional libre: "
            "eso es el chat entrando por la puerta de atrás"
        )


@pytest.mark.anyio
async def test_estan_los_tres_prompts_de_apertura():
    assert {p.name for p in await servidor_mcp.list_prompts()} == PROMPTS_ESPERADOS


@pytest.mark.anyio
@pytest.mark.parametrize(
    "frase",
    [
        "ni siquiera cuando hay un solo candidato",  # 1. desambiguar
        "regla_legible",  # 2. lenguaje ciudadano
        "fuente",  # 3. cada afirmación con su fuente
        "sin salida",  # 4. siempre el siguiente paso
        '"corrupto" ni "ilegal"',  # 5. el vocabulario prohibido
        'decir "no sé"',  # 6. saber decir que no sabe
        "80 y 100 segundos",  # la advertencia de duración
        "nivel_atencion",  # el guardarraíl del enum
    ],
)
async def test_las_instrucciones_llevan_las_reglas(frase: str):
    assert frase in INSTRUCCIONES_SERVIDOR


def test_las_instrucciones_llevan_el_descargo_literal():
    """Una sola versión del descargo en todo el producto: la de
    `contracts/modelos.py`."""
    from lumen.contracts.modelos import DISCLAIMER

    assert DISCLAIMER in INSTRUCCIONES_SERVIDOR


@pytest.mark.anyio
async def test_las_descripciones_repiten_la_regla_que_les_toca():
    """Segunda capa de defensa: hay clientes MCP que truncan o ignoran las
    instrucciones del servidor, pero la descripción de una herramienta la leen
    siempre que puedan llamarla."""
    por_nombre = {h.name: (h.description or "") for h in await servidor_mcp.list_tools()}

    assert "NI SIQUIERA CUANDO SOLO HAY UNO" in por_nombre["resolver_entidad"]
    assert "80 Y 100 SEGUNDOS" in por_nombre["analizar_entidad"]
    assert "cuota" in por_nombre["analizar_entidad"]
    assert "MANDA UN MENSAJE REAL A UNA PERSONA" in por_nombre["enviar_alerta"]
    assert "confirma" in por_nombre["enviar_alerta"].lower()


# --- El mapa de errores -----------------------------------------------------


@pytest.mark.parametrize(
    ("error", "esperado"),
    [
        (CromaDeshabilitado("apagado"), "apagada a propósito"),
        (CromaError("500"), "no respondió"),
        (SupabaseNoConfigurado("sin llaves"), "almacenamiento de casos no está disponible"),
        (CursorAgentError("sin credencial"), "no llegó a arrancar"),
        (LLMEjecucionError("murió"), "arrancó y falló"),
    ],
)
def test_cada_error_conocido_se_traduce_a_algo_accionable(error: Exception, esperado: str):
    assert esperado in str(traducir_error(error))


def test_el_error_de_croma_apagado_gana_al_generico():
    """`CromaDeshabilitado` hereda de `CromaError`. Si alguien reordena el mapa,
    su mensaje deja de verse y 'apagado a propósito' pasa a parecer una caída."""
    mensaje = str(traducir_error(CromaDeshabilitado("apagado")))
    assert "apagada a propósito" in mensaje
    assert "no respondió" not in mensaje


def test_un_error_no_previsto_tampoco_devuelve_una_traza():
    mensaje = str(traducir_error(ZeroDivisionError("division by zero")))
    assert "ZeroDivisionError" in mensaje
    assert "Traceback" not in mensaje


# --- El protocolo, de punta a punta -----------------------------------------
#
# Un solo `with TestClient(app)` en toda la suite: el gestor de sesiones del
# SDK no se puede arrancar dos veces sobre la misma instancia.


def _datos_del_evento(respuesta) -> dict:  # noqa: ANN001
    """La respuesta viene como SSE; saca el último `data:`."""
    for linea in respuesta.text.splitlines():
        if linea.startswith("data: "):
            return json.loads(linea[6:])
    raise AssertionError(f"sin evento en la respuesta: {respuesta.text[:200]}")


@pytest.fixture(scope="module")
def cliente_mcp():
    import os

    previo = {
        "LUMEN_MCP_TOKEN": os.environ.get("LUMEN_MCP_TOKEN"),
        "LUMEN_MCP_HABILITADO": os.environ.get("LUMEN_MCP_HABILITADO"),
        "LUMEN_CROMA_HABILITADO": os.environ.get("LUMEN_CROMA_HABILITADO"),
    }
    os.environ["LUMEN_MCP_TOKEN"] = TOKEN
    os.environ["LUMEN_MCP_HABILITADO"] = "true"
    # Cinturón: aunque ningún test de aquí llegue a la red, si alguien añade
    # uno que sí, que falle en seco en vez de gastar cuota compartida.
    os.environ["LUMEN_CROMA_HABILITADO"] = "false"
    get_settings.cache_clear()

    with TestClient(app) as cliente:
        inicio = cliente.post(
            "/mcp",
            headers=AUTORIZADAS,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "1"},
                },
            },
        )
        assert inicio.status_code == 200
        sesion = {**AUTORIZADAS, "mcp-session-id": inicio.headers["mcp-session-id"]}
        cliente.post(
            "/mcp", headers=sesion, json={"jsonrpc": "2.0", "method": "notifications/initialized"}
        )
        yield cliente, sesion, _datos_del_evento(inicio)

    for clave, valor in previo.items():
        if valor is None:
            os.environ.pop(clave, None)
        else:
            os.environ[clave] = valor
    get_settings.cache_clear()


def test_la_url_canonica_no_redirige(cliente_mcp):
    """`/mcp` sin barra tiene que responder directo. Un 307 en cada petición es
    un round trip de más, y hay clientes que sueltan la credencial al seguirlo."""
    cliente, sesion, _ = cliente_mcp
    r = cliente.post(
        "/mcp",
        headers=sesion,
        json={"jsonrpc": "2.0", "id": 99, "method": "tools/list"},
        follow_redirects=False,
    )
    assert r.status_code == 200


def test_el_agente_recibe_las_instrucciones_al_conectarse(cliente_mcp):
    _, _, inicio = cliente_mcp
    instrucciones = inicio["result"]["instructions"]
    assert instrucciones == INSTRUCCIONES_SERVIDOR
    assert "ni siquiera cuando hay un solo candidato" in instrucciones


def test_el_cliente_ve_las_nueve_herramientas(cliente_mcp):
    cliente, sesion, _ = cliente_mcp
    r = cliente.post("/mcp", headers=sesion, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    nombres = {h["name"] for h in _datos_del_evento(r)["result"]["tools"]}
    assert nombres == HERRAMIENTAS_ESPERADAS


def test_analizar_sin_ninguna_llave_falla_sin_tocar_la_red(cliente_mcp):
    cliente, sesion, _ = cliente_mcp
    r = cliente.post(
        "/mcp",
        headers=sesion,
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "analizar_entidad", "arguments": {}},
        },
    )
    resultado = _datos_del_evento(r)["result"]
    assert resultado["isError"] is True
    assert "al menos uno" in resultado["content"][0]["text"]


def test_una_fecha_invalida_en_el_monitor_falla_en_validacion(cliente_mcp):
    cliente, sesion, _ = cliente_mcp
    r = cliente.post(
        "/mcp",
        headers=sesion,
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "contratos_nuevos_del_monitor", "arguments": {"desde": "ayer"}},
        },
    )
    assert _datos_del_evento(r)["result"]["isError"] is True


def test_resolver_con_texto_vacio_no_consulta_nada(cliente_mcp):
    """Sin texto no hace falta la fuente para saber que no hay nada que buscar:
    se responde antes de mirar su estado."""
    cliente, sesion, _ = cliente_mcp
    r = cliente.post(
        "/mcp",
        headers=sesion,
        json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "resolver_entidad", "arguments": {"texto": "   "}},
        },
    )
    resultado = _datos_del_evento(r)["result"]
    assert resultado["isError"] is False
    assert resultado["structuredContent"]["candidatos"] == []
    assert "NIT" in resultado["structuredContent"]["nota"]


def test_el_estado_del_sistema_no_gasta_cuota(cliente_mcp, monkeypatch: pytest.MonkeyPatch):
    """Un diagnóstico que cuesta créditos es un diagnóstico que nadie corre
    cuando hace falta."""
    from lumen.croma import client as croma_cliente

    async def _prohibido(*_a, **_k):  # noqa: ANN002, ANN003, ANN202
        raise AssertionError("estado_del_sistema salió a la red")

    monkeypatch.setattr(croma_cliente.CromaClient, "consultar", _prohibido)
    monkeypatch.setattr(croma_cliente, "probar_conexion", _prohibido)

    cliente, sesion, _ = cliente_mcp
    r = cliente.post(
        "/mcp",
        headers=sesion,
        json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "estado_del_sistema", "arguments": {}},
        },
    )
    estado = _datos_del_evento(r)["result"]["structuredContent"]
    assert estado["fuente_de_datos"]["encendida"] is False
    assert "no gastar créditos" in estado["fuente_de_datos"]["nota"]


@pytest.mark.parametrize(
    ("herramienta", "argumentos"),
    [
        ("resolver_entidad", {"texto": "Conalvías"}),
        ("analizar_entidad", {"nit": "900123456"}),
        ("ver_red_de_actores", {"nit": "900123456"}),
        ("contratos_nuevos_del_monitor", {}),
    ],
)
def test_con_la_fuente_apagada_las_herramientas_lo_dicen_en_vez_de_fingir_vacio(
    cliente_mcp, herramienta: str, argumentos: dict
):
    """El fallo más peligroso de este producto, encontrado en el Render real.

    Con Croma apagado, `resolver_candidatos` y `Consultas.get` degradan a vacío
    a propósito (son de cara al ciudadano). Para la web está bien; para un
    agente es veneno: `analizar_entidad` devolvería un caso con CERO señales y
    nivel `bajo`, y el agente lo narraría como "no encontré nada preocupante".
    Un visto bueno afirmado sobre cero datos.

    Apagado tiene que ser un error explícito, nunca un resultado vacío.
    """
    cliente, sesion, _ = cliente_mcp
    r = cliente.post(
        "/mcp",
        headers=sesion,
        json={
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {"name": herramienta, "arguments": argumentos},
        },
    )
    resultado = _datos_del_evento(r)["result"]
    assert resultado["isError"] is True, f"{herramienta} devolvió vacío en vez de decir que está apagada"
    texto = resultado["content"][0]["text"]
    assert "apagada a propósito" in texto
    assert "estado_del_sistema" in texto


def test_el_prompt_de_apertura_lleva_la_regla_de_desambiguar(cliente_mcp):
    cliente, sesion, _ = cliente_mcp
    r = cliente.post(
        "/mcp",
        headers=sesion,
        json={
            "jsonrpc": "2.0",
            "id": 7,
            "method": "prompts/get",
            "params": {"name": "buscar_empresa", "arguments": {"nombre": "Conalvías"}},
        },
    )
    texto = _datos_del_evento(r)["result"]["messages"][0]["content"]["text"]
    assert "Conalvías" in texto
    assert "No elijas por mí" in texto
