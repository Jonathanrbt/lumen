"""Agente conversacional: `POST /chat`. Dueno: Freddy (B2).

La única ruta exclusiva del Modo Vigilancia. Por dentro orquesta `/resolver`
y `/analizar` — **no es un motor aparte**, es un envoltorio de conversación
sobre los mismos dos (§CONTRATO-API.md).

Reglas del agente, no negociables:
- **Desambiguar antes de analizar.** Si `/resolver` devuelve candidatos, se
  muestran como tarjetas y la persona elige — nunca se asume cuál es, ni
  siquiera si hay un solo candidato.
- **Narrar en lenguaje ciudadano**, reusando el registro de `regla_legible`
  de cada `Senal` (fuente única: `docs/COPY-SENALES.md`) — no se inventa
  vocabulario nuevo aquí.
- **Cada afirmación con su fuente.** La narración no agrega hechos que no
  estén ya en las señales del `Caso`.
- **Siempre se ofrece el siguiente paso.** Nunca se deja a la persona sin
  salida, ni cuando no se encontró nada.
- **Jamás "corrupto" o "ilegal".** El vocabulario del proyecto entero evita
  esas palabras — es una señal, un motivo para preguntar, no una acusación.
- **Saber decir "no sé".** Si no hay candidatos, se dice y se ofrece una
  alternativa concreta, no una respuesta vaga.
"""

from __future__ import annotations

import logging

from ..contracts import AnalizarRequest, Caso, ChatResponse
from ..plataforma.casos import guardar_caso, obtener_caso
from ..routers.analisis import analizar
from ..senales.motor import id_caso
from .llm_client import CursorAgentError, LLMEjecucionError, Modelo, preguntar
from .resolver import resolver_candidatos

log = logging.getLogger(__name__)

_PROMPT_NARRACION = """Cuenta este hallazgo de contratación pública en Colombia como se lo \
dirías a tu mamá: frases cortas, sin jerga legal, sin siglas sueltas. Usa SOLO los datos que te \
doy abajo — no inventes cifras, fechas ni empresas que no estén ahí. Máximo 3 frases. Termina \
con una frase que deje claro que esto no es una acusación, es un motivo para preguntar (sin \
copiar literal el disclaimer). Nunca uses las palabras "corrupto" o "ilegal".

Entidad: {entidad}
Proveedor: {proveedor}
Valor: {valor}
Nivel de atención: {nivel}

Señales encontradas:
{senales}

Responde solo con el texto de la narración, sin comillas ni explicación extra.
"""


async def _narrar_caso(caso: Caso) -> str:
    senales_texto = "\n".join(f"- {s.regla_legible}" for s in caso.senales) or "(ninguna señal)"
    prompt = _PROMPT_NARRACION.format(
        entidad=caso.entidad,
        proveedor=caso.proveedor or "(no identificado)",
        valor=f"${caso.valor:,.0f}".replace(",", ".") if caso.valor else "(no reportado)",
        nivel=caso.nivel_atencion.value,
        senales=senales_texto,
    )
    try:
        return (await preguntar(prompt, Modelo.RAPIDO)).strip()
    except (CursorAgentError, LLMEjecucionError):
        log.exception("La narración del chat falló para el caso %s; degrado a un resumen simple.", caso.id)
        # Degradación honesta: seguimos ofreciendo las señales tal cual las
        # escribió Jonatin, solo sin la prosa que las conecta.
        return " ".join(s.regla_legible for s in caso.senales) or (
            "No encontré señales para este caso."
        )


def _siguientes_pasos_para(caso: Caso) -> list[str]:
    pasos = ["Ver la red de actores detrás de este contrato", "Generar el paquete de evidencia"]
    if caso.nivel_atencion.value in ("medio", "alto"):
        pasos.append("Redactar un derecho de petición")
    return pasos


def _caso_cacheado(llaves: dict) -> Caso | None:
    """El caso ya calculado, si existe. Brief §4.6, Flujo B paso 4.

    El id sale de la misma llave determinista que usa el motor, asi que se
    puede preguntar por el **sin** llamar a Croma. Importa de verdad: un
    analisis por NIT tarda 80-100 s (`sicaac_insolvency_cases` sola se lleva
    ~57 s), y los casos del catalogo curado ya estan precomputados. Esto es lo
    que hace que la demo responda al instante en vez de dejar a alguien mirando
    un spinner minuto y medio.

    Best-effort igual que `guardar_caso`: si Supabase no esta configurado o
    responde mal, se sigue por el camino largo en vez de tumbar el chat.
    """
    llave = llaves.get("contrato_id") or llaves.get("nit") or llaves.get("entidad_id")
    if not llave:
        return None
    try:
        return obtener_caso(id_caso(llave))
    except Exception:  # noqa: BLE001 - el cache es un atajo, nunca un requisito
        log.warning("No se pudo consultar el caso cacheado de %r; se re-analiza.", llave)
        return None


async def _analizar_desde_contexto(contexto: dict) -> Caso | None:
    llaves = {k: contexto[k] for k in ("nit", "entidad_id", "contrato_id") if contexto.get(k)}
    if not llaves:
        return None

    cacheado = _caso_cacheado(llaves)
    if cacheado is not None:
        log.info("Caso %s servido desde Supabase, sin re-analizar.", cacheado.id)
        return cacheado

    return await analizar(AnalizarRequest(**llaves))


def _guardar_caso_best_effort(caso: Caso) -> None:
    """Sin esto, un caso que el Modo Vigilancia descubre por primera vez
    nunca queda accesible por `/accion` (`caso_id` no existe en ningún
    lado) — confirmado en vivo el 16.ago ~03:00: /chat devuelve el caso,
    /accion sobre ese mismo caso_id da 404. El monitor de Cristian ya
    guarda los suyos (`plataforma/monitor.py`); esto hace lo mismo para
    el camino de una persona preguntando.

    `guardar_caso` no respeta `LUMEN_USAR_DUMP_LOCAL` (a diferencia de
    `obtener_caso`), así que esto es best-effort a propósito: si Supabase
    no está configurado o falla, se registra y se sigue — el chat nunca se
    cae por un problema de persistencia, igual que `scripts/precomputar_casos_demo.py`.
    """
    try:
        guardar_caso(caso)
    except Exception:  # noqa: BLE001 - persistir es deseable, no imprescindible aquí
        log.warning(
            "No se pudo guardar el caso %s desde el chat (Supabase no disponible); "
            "/accion no podrá encontrarlo por su id hasta que se guarde en algún lado.",
            caso.id,
            exc_info=True,
        )


async def responder_chat(mensaje: str, contexto: dict | None = None) -> ChatResponse:
    """Dos caminos, en este orden:

    1. Si `contexto` ya trae un identificador resuelto (la persona confirmó
       un candidato en un turno anterior), se analiza directo — no se vuelve
       a preguntar.
    2. Si no, `/resolver` decide: sin candidatos se dice "no sé" con una
       alternativa; con uno o más, **siempre** se muestran para que la
       persona confirme — nunca se asume cuál es, ni con un solo candidato.
    """
    contexto = contexto or {}

    caso = await _analizar_desde_contexto(contexto)
    if caso is not None:
        # Un caso que vuelve del cache ya trae su narracion escrita: reusarla
        # ahorra una llamada al modelo por cada vez que alguien reabre el mismo
        # caso, y el presupuesto de Cursor es de US$50 para los cuatro.
        narracion = caso.narracion or await _narrar_caso(caso)

        # La narracion vive DENTRO del caso, no solo en la respuesta del chat.
        # Si no, al reabrir la ficha por `/caso/{id}` el parrafo desaparecia:
        # `FichaCaso` solo lo pinta cuando `caso.narracion` existe, y el motor
        # siempre lo deja en None (`senales/motor.py`).
        caso = caso.model_copy(update={"narracion": narracion})
        _guardar_caso_best_effort(caso)

        return ChatResponse(
            narracion=narracion,
            caso=caso,
            candidatos=None,
            siguientes_pasos=_siguientes_pasos_para(caso),
        )

    candidatos = await resolver_candidatos(mensaje)

    if not candidatos:
        return ChatResponse(
            narracion=(
                "No encontré ningún registro que coincida con lo que escribiste. "
                "No es que no exista — puede que el nombre esté incompleto o distinto "
                "a como aparece en el registro oficial."
            ),
            caso=None,
            candidatos=None,
            siguientes_pasos=[
                "Intenta con el NIT si lo tienes a mano",
                "Prueba escribiendo el nombre completo de la empresa o entidad",
            ],
        )

    return ChatResponse(
        narracion=(
            f"Encontré {len(candidatos)} registros que coinciden con lo que escribiste. "
            "¿Cuál es el que te interesa?"
            if len(candidatos) > 1
            else f"Encontré un registro que coincide: {candidatos[0].nombre}. ¿Es este?"
        ),
        caso=None,
        candidatos=candidatos,
        siguientes_pasos=[
            "Elegir uno de los registros de arriba",
            "Buscar por número de proceso si lo tienes a mano",
        ],
    )
