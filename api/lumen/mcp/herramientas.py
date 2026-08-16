"""Las nueve herramientas del servidor MCP. Dueno: Cristian (B3).

Cada herramienta llama **en proceso** a la misma funcion que ya usa su router
HTTP. No hay un segundo motor y no se da la vuelta por HTTP contra nosotros
mismos: seria un timeout mas que ajustar sobre una operacion que ya tarda 100
segundos, y obligaria al servicio a conocer su propia URL publica.

Las descripciones no son documentacion decorativa: son la **segunda capa** del
comportamiento del asistente (§design.md, decision 4). Un cliente MCP puede
truncar o ignorar las `instructions` del servidor, pero la descripcion de una
herramienta la lee siempre que pueda llamarla. Por eso la regla que se puede
desobedecer en cada camino esta repetida aqui, pegada a la herramienta.

Lo que NO se expone: `/chat`. El agente conectado es el conversador; envolver
`/chat` seria meter un LLM dentro de otro, narrar dos veces y pagar el modelo
dos veces.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import httpx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import ValidationError

from ..alertas import enviar_alerta as _enviar_alerta
from ..config import get_settings
from ..contracts import AnalizarRequest, TipoArtefacto
from ..croma.client import RUTAS, CromaDeshabilitado, CromaError, CromaSinRespuesta
from ..ia.artefactos import generar_artefacto as _generar_artefacto
from ..ia.lector import DocumentoIlegible, leer_justificacion_desde_url
from ..ia.llm_client import CursorAgentError, LLMEjecucionError
from ..ia.resolver import resolver_candidatos
from ..plataforma.casos import obtener_caso as _obtener_caso
from ..plataforma.monitor import monitor_nuevos
from ..plataforma.supabase_client import SupabaseNoConfigurado
from ..senales.motor import analizar as _analizar
from ..senales.motor import red as _red

log = logging.getLogger(__name__)

__all__ = ["registrar_herramientas", "traducir_error"]


# --- Mapa de errores --------------------------------------------------------
#
# De lo mas especifico a lo mas general: `CromaDeshabilitado` hereda de
# `CromaError`, asi que si se invierte el orden nunca se veria su mensaje.
#
# `CursorAgentError` y `LLMEjecucionError` se mantienen separados a proposito,
# igual que en `llm_client.py`: "nunca arranco" (auth, config, red) y "arranco
# y fallo" son bugs distintos, y aplanarlos aqui tiraria esa informacion justo
# donde alguien esta depurando en vivo.

_MENSAJES: tuple[tuple[type[Exception], str], ...] = (
    (
        CromaDeshabilitado,
        "La fuente de datos está apagada a propósito (LUMEN_CROMA_HABILITADO=false) para no "
        "gastar créditos del token compartido. No es una caída. Llama `estado_del_sistema` "
        "para confirmarlo y avísale a quien te está usando.",
    ),
    (
        CromaSinRespuesta,
        "La fuente de datos no devolvió una respuesta utilizable; suele ser la credencial. "
        "Llama `estado_del_sistema`.",
    ),
    (
        CromaError,
        "La fuente de datos no respondió. No significa que no exista lo que buscas: "
        "significa que no se pudo consultar. Dilo así y ofrece reintentar.",
    ),
    (
        SupabaseNoConfigurado,
        "El almacenamiento de casos no está disponible (sin configurar o con credenciales "
        "inválidas). Los casos nuevos se pueden analizar, pero no consultar por su id.",
    ),
    (
        CursorAgentError,
        "El modelo de lenguaje no llegó a arrancar (configuración, credencial o red). "
        "No es que fallara el análisis: es que no empezó.",
    ),
    (
        LLMEjecucionError,
        "El modelo de lenguaje arrancó y falló a mitad. Se puede reintentar.",
    ),
    (
        DocumentoIlegible,
        "No se pudo extraer texto del documento. Suele ser un PDF escaneado como imagen. "
        "Dilo tal cual y no emitas veredicto.",
    ),
    (
        httpx.HTTPError,
        "No se pudo descargar el documento de esa URL. Es un problema de la descarga, no "
        "del contenido.",
    ),
    (
        ValidationError,
        "Los datos de entrada no son válidos.",
    ),
)


def traducir_error(err: Exception) -> ToolError:
    """Convierte una excepcion del motor en un `ToolError` accionable.

    Ninguna herramienta devuelve una traza cruda: el agente al otro lado no
    puede hacer nada con un stack trace, pero sí con "está apagado a
    propósito, avisa" o "no se pudo descargar, no es el contenido".
    """
    for tipo, mensaje in _MENSAJES:
        if isinstance(err, tipo):
            return ToolError(f"{mensaje} (detalle: {err})")
    log.exception("Error no previsto en una herramienta MCP")
    return ToolError(f"Falló la herramienta por un error no previsto: {type(err).__name__}: {err}")


def _exigir_fuente_de_datos() -> None:
    """Corta antes de salir a la red si la fuente no va a poder responder.

    Existe porque "no hay nada" y "no se pudo mirar" son cosas distintas y el
    agente tiene que poder decirlas distinto. Sin esto, una búsqueda con Croma
    apagado vuelve vacía y el agente le dice a la persona que la empresa no
    aparece en el registro — afirmando algo que nadie comprobó.
    """
    ajustes = get_settings()
    if not ajustes.lumen_croma_habilitado:
        raise traducir_error(
            CromaDeshabilitado("LUMEN_CROMA_HABILITADO=false")
        )
    if not ajustes.croma_configurado:
        raise ToolError(
            "La fuente de datos no tiene credencial configurada (falta CROMA_API_KEY), así que "
            "no se consultó nada. NO le digas a la persona que no se encontró: dile que la "
            "fuente no está disponible. Llama `estado_del_sistema` para confirmarlo."
        )


def _caso_o_error(caso_id: str):  # noqa: ANN202 - Caso, evitando el import circular de tipos
    """Busca el caso y distingue los dos fallos que se confunden solos.

    "No existe ese caso" y "el almacenamiento no está disponible" son cosas
    distintas y el agente tiene que poder decirle cosas distintas a la
    persona.
    """
    try:
        caso = _obtener_caso(caso_id)
    except Exception as err:  # noqa: BLE001 - se traduce, no se traga
        raise traducir_error(err) from err

    if caso is None:
        raise ToolError(
            f"No existe ningún caso con id '{caso_id}'. Los ids de caso salen de "
            "`analizar_entidad` o de `contratos_nuevos_del_monitor`; no se inventan."
        )
    return caso


# --- Registro ---------------------------------------------------------------


def registrar_herramientas(servidor) -> None:  # noqa: ANN001 - MCPServer, sin importarlo aqui
    """Registra las nueve herramientas en el servidor MCP."""

    @servidor.tool(
        name="resolver_entidad",
        title="Resolver un nombre a candidatos",
        description=(
            "Traduce lo que escribió una persona ('Conalvías', 'el metro de Bogotá') a "
            "candidatos concretos del registro mercantil, con su NIT cuando existe. "
            "Pásale el texto TAL CUAL, sin limpiarlo. "
            "REGLA: muestra todos los candidatos y deja que la persona elija. Nunca "
            "asumas cuál es, NI SIQUIERA CUANDO SOLO HAY UNO — con uno solo se pregunta "
            "igual. Barata y rápida."
        ),
    )
    async def resolver_entidad(texto: str) -> dict[str, Any]:
        """El texto que escribió la persona, tal cual."""
        # Texto vacio se responde sin mirar nada: no hace falta la fuente para
        # saber que no hay nada que buscar, asi que se comprueba ANTES que el
        # estado de Croma.
        if not texto.strip():
            return {
                "candidatos": [],
                "nota": (
                    "No me diste nada que buscar. Pregúntale a la persona el nombre de la "
                    "empresa o entidad, o su NIT."
                ),
            }

        # `resolver_candidatos` se traga los fallos de Croma y devuelve lista
        # vacia (es de cara al ciudadano: degrada en vez de reventar). Bien
        # para la web, veneno aqui: el agente recibiria "no encontré ningún
        # registro" cuando en realidad la fuente NUNCA se consulto, y se lo
        # diria a la persona como si el dato no existiera. Eso es justo lo que
        # la regla 6 prohibe. Se comprueba antes, no despues.
        _exigir_fuente_de_datos()

        try:
            candidatos = await resolver_candidatos(texto)
        except Exception as err:  # noqa: BLE001
            raise traducir_error(err) from err

        if not candidatos:
            return {
                "candidatos": [],
                "nota": (
                    "No encontré ningún registro que coincida. No es que no exista: puede que "
                    "el nombre esté incompleto o distinto a como aparece en el registro "
                    "oficial. Dilo así y pide el NIT o el nombre completo."
                ),
            }

        return {
            "candidatos": [c.model_dump(mode="json") for c in candidatos],
            "nota": (
                "Muéstraselos todos y pregunta cuál es antes de analizar, también si hay uno "
                "solo. Los que traen NIT son los que sirven para `analizar_entidad`."
            ),
        }

    @servidor.tool(
        name="analizar_entidad",
        title="Correr las señales sobre una entidad, proveedor o contrato",
        description=(
            "Corre las 8 señales de Lumen y devuelve un caso completo: señales encontradas, "
            "nivel de atención, grafo de actores y descargo. Necesita al menos una de tres "
            "llaves: `nit` (mira al actor como proveedor), `entidad_id` (como entidad "
            "contratante) o `contrato_id`. "
            "CARA Y LENTA: son nueve consultas a la fuente de datos y tarda ENTRE 80 Y 100 "
            "SEGUNDOS — avísale a la persona antes de llamarla. La cuota es compartida y "
            "finita: no la repitas sin motivo. "
            "REGLA: `nivel_atencion` es `bajo`, `medio` o `alto`. Nunca lo conviertas en "
            "número ni en porcentaje. Narra con el `regla_legible` de cada señal y cita su "
            "`fuente`."
        ),
    )
    async def analizar_entidad(
        nit: str | None = None,
        entidad_id: str | None = None,
        contrato_id: str | None = None,
    ) -> dict[str, Any]:
        """NIT del proveedor, NIT de la entidad contratante o id del contrato."""
        try:
            peticion = AnalizarRequest(nit=nit, entidad_id=entidad_id, contrato_id=contrato_id)
        except ValidationError as err:
            raise ToolError(
                "Hay que enviar al menos uno de: `nit`, `entidad_id` o `contrato_id`. "
                "Si no tienes ninguno, resuélvelo antes con `resolver_entidad`."
            ) from err

        # Sin esto, con la fuente apagada el motor devuelve un Caso con CERO
        # señales y nivel `bajo`, porque `Consultas.get` convierte el fallo en
        # `{"found": false}`. El agente lo narraria como "no encontre nada
        # preocupante": un visto bueno afirmado sobre cero datos. Es el peor
        # fallo posible en este producto.
        _exigir_fuente_de_datos()

        try:
            caso = await _analizar(peticion)
        except Exception as err:  # noqa: BLE001
            raise traducir_error(err) from err
        return caso.model_dump(mode="json")

    @servidor.tool(
        name="ver_red_de_actores",
        title="Ver la red de actores alrededor de un NIT",
        description=(
            "Devuelve el subgrafo curado de quién está detrás de quién: nodos (empresas, "
            "personas, entidades) y aristas con el tipo de vínculo. Entre 5 y 12 nodos a "
            "propósito. "
            "REGLA: cada arista trae su `fuente` — cita de dónde sale cada vínculo. Un grafo "
            "vacío significa que no se encontraron relaciones, no que haya fallado algo. "
            "Cuesta cuota de la fuente de datos."
        ),
    )
    async def ver_red_de_actores(nit: str) -> dict[str, Any]:
        """NIT alrededor del cual construir la red."""
        # Mismo motivo que en `analizar_entidad`: un grafo vacío por fuente
        # apagada es indistinguible de "no tiene vínculos".
        _exigir_fuente_de_datos()
        try:
            grafo = await _red(nit)
        except Exception as err:  # noqa: BLE001
            raise traducir_error(err) from err
        return grafo.model_dump(mode="json")

    @servidor.tool(
        name="obtener_caso",
        title="Recuperar un caso ya calculado",
        description=(
            "Devuelve un caso que ya se analizó antes, por su id. Barata: no toca la fuente "
            "de datos. Los ids salen de `analizar_entidad` o de "
            "`contratos_nuevos_del_monitor` — no se inventan."
        ),
    )
    async def obtener_caso(caso_id: str) -> dict[str, Any]:
        """Id del caso, tal como lo devolvió otra herramienta."""
        return _caso_o_error(caso_id).model_dump(mode="json")

    @servidor.tool(
        name="leer_justificacion_urgencia",
        title="Leer una justificación de urgencia manifiesta",
        description=(
            "Lee el PDF de una justificación de urgencia manifiesta y emite un veredicto: "
            "`solida`, `generica` o `sin_relacion`. La norma exige que la contratación por "
            "urgencia tenga relación directa y verificable con los hechos de la emergencia. "
            "REGLA: cada punto trae o bien su cita textual del documento, o bien el motivo "
            "por el que no se pudo concluir. Si no hay cita, NO afirmes — muestra el motivo. "
            "Usa el modelo de lenguaje, así que tarda."
        ),
    )
    async def leer_justificacion_urgencia(url: str) -> dict[str, Any]:
        """Enlace directo al PDF de la justificación."""
        try:
            lectura = await leer_justificacion_desde_url(url)
        except Exception as err:  # noqa: BLE001
            raise traducir_error(err) from err
        return lectura.model_dump(mode="json")

    @servidor.tool(
        name="generar_artefacto",
        title="Convertir un hallazgo en algo que se puede enviar",
        description=(
            "Redacta el documento de acción a partir de un caso concreto, con hechos "
            "numerados y normas citadas. No es una plantilla con huecos. Tipos: "
            "`paquete_evidencia`, `derecho_peticion`, `informe_veeduria`, `guia_denuncia`. "
            "REGLA: el `derecho_peticion` solo se ofrece si el `nivel_atencion` del caso es "
            "`medio` o `alto`. Sobre un caso de nivel `bajo`, ofrece el paquete de evidencia."
        ),
    )
    async def generar_artefacto(caso_id: str, tipo: TipoArtefacto) -> dict[str, Any]:
        """Id del caso y cuál de los cuatro documentos redactar."""
        caso = _caso_o_error(caso_id)
        try:
            artefacto = await _generar_artefacto(caso, tipo)
        except Exception as err:  # noqa: BLE001
            raise traducir_error(err) from err
        return artefacto.model_dump(mode="json")

    @servidor.tool(
        name="contratos_nuevos_del_monitor",
        title="Contratos nuevos que encontró el monitor",
        description=(
            "Devuelve los contratos con causal de urgencia que el monitor encontró en los "
            "departamentos afectados y convirtió en casos. Lo ya conocido no se re-analiza "
            "pero sí se devuelve, así que el mismo contrato se puede consultar varias veces. "
            "MUY CARA: recorre varias entidades y analiza cada novedad. Cuesta mucha cuota "
            "compartida y tarda minutos. No la llames para explorar — es para revisar qué "
            "hay nuevo. "
            "REGLA: `forzar` re-analiza desde cero TODO lo que encuentre, incluso lo ya "
            "guardado — sale carísimo. Úsalo solo si te lo piden explícitamente porque un "
            "caso está desactualizado."
        ),
    )
    async def contratos_nuevos_del_monitor(
        desde: date | None = None, forzar: bool = False
    ) -> list[dict[str, Any]]:
        """Fecha mínima de publicación (AAAA-MM-DD) y si se re-analiza lo ya guardado."""
        # Con la fuente apagada devolveria lista vacia, que el agente leeria
        # como "no hay contratos nuevos". No los hay porque no se miro.
        _exigir_fuente_de_datos()
        try:
            casos = await monitor_nuevos(desde, forzar=forzar)
        except Exception as err:  # noqa: BLE001
            raise traducir_error(err) from err
        return [c.model_dump(mode="json") for c in casos]

    @servidor.tool(
        name="enviar_alerta",
        title="Enviar el aviso de un caso a una persona",
        description=(
            "MANDA UN MENSAJE REAL A UNA PERSONA por el canal configurado (Telegram o "
            "WhatsApp). Es la única herramienta con efecto hacia afuera y no se puede "
            "deshacer. "
            "REGLA: confirma con quien te está usando ANTES de llamarla — a quién se le "
            "manda y de qué caso. Nunca la llames por iniciativa propia."
        ),
    )
    async def enviar_alerta(caso_id: str, destinatario: str) -> dict[str, Any]:
        """Id del caso y destinatario (teléfono E.164 o chat id, según el canal)."""
        caso = _caso_o_error(caso_id)
        try:
            estado, detalle = await _enviar_alerta(caso, destinatario)
        except Exception as err:  # noqa: BLE001
            raise traducir_error(err) from err
        return {"estado": estado, "detalle": detalle}

    @servidor.tool(
        name="estado_del_sistema",
        title="Qué piezas están configuradas y encendidas",
        description=(
            "Diagnóstico rápido: si la fuente de datos está configurada y encendida, si el "
            "almacenamiento responde, si el modelo de lenguaje está configurado y cuál es el "
            "canal de alerta. GRATIS: no gasta ni una llamada a la fuente de datos. "
            "Llámala cuando algo falle y no entiendas por qué, antes de reintentar."
        ),
    )
    async def estado_del_sistema() -> dict[str, Any]:
        """Sin argumentos."""
        # A proposito NO se llama `probar_conexion()`: ese endpoint hace una
        # consulta REAL a RUES y gasta creditos. Un diagnostico que cuesta
        # cuota es un diagnostico que nadie corre cuando hace falta.
        ajustes = get_settings()
        return {
            "fuente_de_datos": {
                "credencial_configurada": ajustes.croma_configurado,
                "encendida": ajustes.lumen_croma_habilitado,
                "fuentes_disponibles": len(RUTAS),
                "nota": (
                    "Apagada: las búsquedas van a volver vacías a propósito, para no gastar "
                    "créditos del token compartido."
                    if not ajustes.lumen_croma_habilitado
                    else "Encendida."
                ),
            },
            "almacenamiento_de_casos": {
                "configurado": bool(ajustes.supabase_url and ajustes.supabase_service_role_key),
                "usando_dump_local": ajustes.lumen_usar_dump_local,
            },
            "modelo_de_lenguaje": {
                "configurado": bool(ajustes.cursor_api_key),
                "modelo_rapido": ajustes.lumen_modelo_rapido or None,
                "modelo_fuerte": ajustes.lumen_modelo_fuerte or None,
            },
            "canal_de_alerta": ajustes.lumen_canal_alerta,
            "entorno": ajustes.lumen_env,
        }
