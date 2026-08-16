# Handoff — Freddy · B2 IA

**Soy dueño de:** `api/lumen/ia/`, `api/lumen/routers/ia.py`, y desde las 22:14 también
`api/lumen/whatsapp/`.
**Mis endpoints:** `POST /resolver`, `POST /justificacion`, `POST /accion`, `POST /chat`.
**Mi hito:** 21:30 — el lector clasifica correctamente 3 documentos reales de urgencia manifiesta,
y cada punto del veredicto trae su cita textual.
**También soy dueño del presupuesto:** los US$50 de la API de Cursor. Reviso consumo a las 20:00 y
a las 23:00 y lo anoto aquí abajo.

> **Actualización 22:14 — WhatsApp pasa a ser mío.** El reparto original (`PLAN.md`) ponía Twilio en
> B3/Cristian, prioridad 1 de su bloque de las 20:45. Se reasigna por decisión del equipo: yo tomo
> el canal de WhatsApp completo, con libertad para usar Twilio o Evolution API — el que mejor
> funcione en la ventana que queda, sin que eso implique reabrir el contrato de la API. Detalle en
> la sección de abajo y en `PLAN.md` / `CRISTIAN-B3.md`, ya actualizados.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

---

## 19:20 — Qué me cambió el v3.1

El parche no toca mis endpoints ni mi cronograma. Me cambia **el registro de todo lo que sale de un
modelo**, que en mi caso es casi todo.

**Para quién escribo ahora: el veedor.** No "el ciudadano que no sabe qué es SECOP" — ese usuario no
existe como usuario activo. Es la persona que ya hace veeduría: suele ser mayor, es la mamá, la tía,
el jubilado del barrio. Sabe perfectamente qué quiere revisar; lo que no tiene son las ocho horas
que cuesta cruzar SECOP con el RUES contrato por contrato. **No le explico cómo vigilar. Le entrego
el trabajo hecho.**

Lo que eso significa en mis tres salidas:

**Narración (`/chat`, `Caso.narracion`).** El registro y el vocabulario están fijados en
**[`docs/COPY-SENALES.md`](../COPY-SENALES.md)**, que es fuente única compartida con B1 y con
Andrew. No inventes sinónimos: si B1 escribe "sin concurso" y tú escribes "contratación directa" en
la misma pantalla, el veedor lee dos voces. La tabla de equivalencias ("adjudicación" → "le dieron
el contrato", "urgencia manifiesta" → "el documento que explica por qué era urgente") está ahí.

**Lector de justificaciones (`/justificacion`).** Las preguntas del veredicto se formulan como se las
harías a una persona, no como las formula la norma. Mira `fixtures/lectura.json`, ya está
actualizado: *"¿Lo que se está comprando tiene que ver con los daños del terremoto?"* en vez de
*"¿El objeto contractual guarda relación causal con el daño descrito?"*. **La cita textual del
documento no se toca:** esa se transcribe literal, porque es la prueba.

La frase de salida del lector, cuando el veredicto es `sin_relacion`, es la del parche:
*"El documento que explica por qué era urgente no menciona ningún daño del terremoto."*

**Artefacto (`/accion`).** En la interfaz se llama **"la carta para preguntarle a la alcaldía"**, no
"derecho de petición". Puede ir con las dos: *"Carta para la alcaldía (derecho de petición)"*. Pero
**dentro del documento las normas siguen citadas íntegras** — el Decreto 1171, el artículo 46, la
Ley 1755. Las leyes no se borran, se mudan: fuera de la interfaz, dentro del documento y del README.

**El disclaimer cambió de texto:** ahora es *"Una señal no es prueba de irregularidad. Es un motivo
para preguntar."* Ya está actualizado en la constante `DISCLAIMER` de `contracts/modelos.py`, así
que si lo tomas de ahí no tienes que hacer nada.

**El test, para las tres:** si tu mamá no lo entiende, se reescribe.

---

## Lo primero que tengo que hacer

1. **`Cursor.models.list()`** para ver a qué modelos tiene acceso la cuenta. No hardcodear un ID a
   ciegas. Punto de partida: `composer-2.5` para narración y resolución de entidades, y el modelo
   más fuerte disponible **solo** para el lector de justificaciones, que hace pocas llamadas y es la
   feature que gana los 25 puntos de IA. Los dos IDs se anotan en `.env` como
   `LUMEN_MODELO_RAPIDO` y `LUMEN_MODELO_FUERTE`.
2. **`llm_client` con interfaz mínima**, en `api/lumen/ia/llm_client.py`. Todo el código llama ahí y
   solo ahí. Si a las 22:00 el consumo se dispara o la latencia mata el chat, se cambia de proveedor
   en veinte minutos y no en seis horas.
3. **El lector de justificaciones.** Es el núcleo del producto, no una feature más.

## Las seis reglas de presupuesto, que no son opcionales

1. Un solo `llm_client`.
2. **`cwd` apuntando a `./scratch`, nunca al repo.** Es lo que más ahorra: un agente suelto sobre el
   repositorio lee archivos que nadie pidió y quema tokens.
3. `settingSources: []`.
4. Los 6 casos del catálogo, precomputados y cacheados. **Durante la grabación, cero llamadas al LLM
   en vivo.**
5. El SDK de Python es síncrono y FastAPI es async: usar `AsyncClient.launch_bridge` y no mezclar
   clientes sync y async en el mismo path.
6. Disponer siempre el agente con context manager, o se filtran procesos.

**Higiene de errores:** `CursorAgentError` significa que el run **nunca arrancó** (auth, config o
red). `result.status == "error"` significa que **arrancó y falló**. Son bugs distintos y confundirlos
cuesta una hora.

## El guardarraíl que va en el código, no en la documentación

**Toda salida del LLM cita el fragmento fuente. Si no puede citar, dice que no puede concluir.** El
modelo `Lectura` tiene un campo `no_concluye_por` justamente para eso: existe para usarse, no para
decorar.

---

## WhatsApp — mío desde las 22:14

**Vive en `api/lumen/whatsapp/`, carpeta nueva, separada de `api/lumen/plataforma/` de Cristian.**
No toco su territorio: Supabase, el monitor y `/alerta` siguen siendo suyos. Lo que construyo es un
cliente de WhatsApp con la misma filosofía que `llm_client`: una interfaz mínima detrás de la cual
puede vivir Twilio o Evolution API, y se cambia de proveedor sin tocar el resto del código. El brief
fijaba Twilio, pero lo que importa es que un mensaje real le llegue a un teléfono real esta noche —
si Evolution API resuelve eso mejor o más rápido, se usa esa.

**Frontera con Cristian:** su router (`api/lumen/routers/plataforma.py`, endpoint `POST /alerta`)
sigue siendo la puerta pública del contrato — eso no cambia sin anunciarlo. Lo que cambia es qué hay
detrás: en vez de que él implemente el envío, `/alerta` llama a mi cliente de `api/lumen/whatsapp/`.

**Copy:** las nueve frases y el disclaimer ya están fijados en
[`docs/COPY-SENALES.md`](../COPY-SENALES.md) — máximo 5 líneas, cero siglas sueltas, cifras en pesos
redondeados, "la carta para preguntarle a la alcaldía" nunca "derecho de petición". No reescribo
nada, lo consumo tal cual está ahí.

**Detalle operativo que ya estaba anotado y sigue aplicando (venía del handoff de Cristian):** en el
sandbox de Twilio, el teléfono que recibe tiene que unirse antes mandando `join <código>` al número
de Twilio, y tiene que estar unido desde temprano, no a las 03:00. Va en `TWILIO_WHATSAPP_TO_DEMO`.
Si termino usando Evolution API en su lugar, este detalle no aplica y lo anoto aquí cuando decida.

---

## Bitácora

### 22:35 — Esqueleto de WhatsApp listo, Twilio funcionando

**Qué cambié.** Paquete nuevo `api/lumen/whatsapp/`: `base.py` (interfaz `WhatsAppClient`,
un método `enviar(destinatario, mensaje)`), `copy.py` (arma el mensaje desde `Senal.regla_legible`
y `Caso.disclaimer`, portado 1:1 del fallback de Cristian), `twilio_client.py` (proveedor real, SDK
síncrono detrás de `asyncio.to_thread` para no bloquear el event loop), `evolution_client.py`
(esqueleto sin probar contra un servidor real todavía) y `cliente.py` (el factory: lee
`LUMEN_WHATSAPP_PROVIDER` y elige el proveedor). Añadí el campo a `config.py` y las variables de
Evolution a `.env.example` — aditivo, nada renombrado. Apliqué el swap de una línea que Cristian dejó
listo en `api/lumen/routers/plataforma.py` y encontré que `api/lumen/plataforma/monitor.py` también
importaba el fallback: mismo swap ahí. Borré `api/lumen/plataforma/whatsapp.py`, como el propio
comentario de Cristian autorizaba una vez mi cliente existiera. Agregué `api/tests/test_whatsapp.py`
con el guardarraíl explícito: nunca se fabrica `'enviado'`, ni con Twilio ni con Evolution sin
configurar, y `nivel_atencion=bajo` no llega a ningún proveedor.

**Qué quedó a medias y dónde.** Evolution API es un esqueleto sin verificar contra un servidor real
(`api/lumen/whatsapp/evolution_client.py`, endpoint asumido `POST {url}/message/sendText/{instancia}`
según su documentación pública, no probado). Twilio sigue necesitando cuenta/sandbox real y el
`join <código>` del teléfono de demo — eso no cambió, sigue siendo lo que anotó Cristian.

**Qué no hay que tocar y por qué.** `api/lumen/whatsapp/` es mío. `api/lumen/routers/plataforma.py`
y `api/lumen/plataforma/monitor.py` los tocué solo en la línea de import que ya estaba acordada como
punto de enganche — el resto sigue siendo de Cristian.

**Cómo se prueba en 30 segundos.**
`.venv/bin/python -m pytest -q api/tests/test_whatsapp.py` — 4 pruebas, sin red ni credenciales.
Para probar contra un teléfono real: poner `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
`TWILIO_WHATSAPP_FROM` en `.env` y llamar `POST /alerta` con un `caso_id` de nivel `alto` o `medio`.

*(Nota aparte, no de producto: en mi máquina solo hay Python 3.9, no el 3.13 que pide
`requirements.txt` — tuve que instalar `eval_type_backport` solo en mi venv local para poder correr
pytest. No toqué `requirements.txt` por esto; en Render corre 3.13 y no aplica.)*

### 17:30 — Todavía no arranco

El esqueleto de mis cuatro endpoints ya está en `api/lumen/routers/ia.py`, devolviendo `501` con un
mensaje que dice de quién es cada uno. Los modelos que tengo que devolver están en
`api/lumen/contracts/` y hay un JSON de ejemplo por endpoint en `fixtures/`.

**Consumo de la API de Cursor:** sin medir todavía.
