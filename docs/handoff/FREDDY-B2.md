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

### 01:35 — /resolver vivo, probado contra RUES real

**Qué cambié.** `api/lumen/ia/resolver.py` + wireado en `api/lumen/routers/ia.py`. Dos caminos:
camino barato (el texto ya es un nombre, va directo a `rues_entities_by_name`, cero LLM) y camino
con LLM (`Modelo.RAPIDO` extrae el nombre de una pregunta libre cuando el camino barato no
encuentra nada). Mapea la respuesta real de RUES a `Candidato`: NIT primero cuando hay varios
(sirve para seguir a `/analizar`), deduplicado por nombre, `ciudad` cae a `chamber_name` cuando
`commercial_municipality` viene vacío (casi siempre), `tipo` es una heurística documentada sobre
`legal_organization`/`category` porque RUES es sobre todo un registro mercantil.

**Hallazgo en vivo, no asumido:** RUES devuelve HTTP 400 si el texto tiene caracteres fuera de
letras/números/espacios/`.,'&-()/+` — una pregunta con "¿" o "?" nunca pasa el camino barato. Por
eso hay una validación de charset antes de llamar a Croma, y por eso el camino con LLM existe.

**Probado de punta a punta con Croma y Cursor reales** (no solo mocks):
- `"Conalvias"` → 5 candidatos reales, el que trae NIT primero.
- `"¿la alcaldía de mi pueblo tiene algo raro?"` → `[]` correctamente: el LLM no encontró un
  nombre propio, y no se inventa uno.
- `"el metro de Bogotá"` → candidatos reales relacionados, ninguno es literalmente "Metro de
  Bogotá" — coincide con lo que Jonatin ya había verificado ("no aparece como Empresa Metro en
  RUES"), no es un bug de mi lado.

**Guardarraíl añadido:** si el LLM no arranca (`CursorAgentError`, config/red) o corre y falla
(`LLMEjecucionError`), `/resolver` se degrada a lista vacía, nunca un 500 — es un endpoint de cara
al ciudadano y el camino barato ya cubre el caso común sin depender del LLM.

**Tests:** `api/tests/test_resolver.py`, 7 casos con Croma y LLM mockeados (sin red, sin
presupuesto). Ajusté `test_app.py`: el test de "endpoints en 501" ahora prueba `/justificacion`
(que sigue pendiente) en vez de `/resolver`. Suite completa: 49 passed.

**Qué sigue:** `/justificacion` — el lector de justificaciones, el núcleo del producto.

### 01:15 — llm_client vivo, modelos fijados con Cursor.models.list() real

**Qué cambié.** `Cursor.models.list()` corrido de verdad (no hardcodeado a ciegas): confirmé
`LUMEN_MODELO_RAPIDO=composer-2.5` (ya era el default sugerido) y fijé
`LUMEN_MODELO_FUERTE=claude-opus-5` para el lector de justificaciones — el más nuevo y capaz de
los disponibles en la cuenta, y hace pocas llamadas. `api/lumen/ia/llm_client.py`: único punto de
entrada al LLM (`preguntar(prompt, Modelo.RAPIDO|FUERTE)`), con las seis reglas de presupuesto del
handoff — `cwd`/`setting_sources` apuntando a `LUMEN_SCRATCH_DIR` nunca al repo,
`AsyncClient.launch_bridge` con `try/finally` + `aclose()` (nunca mezclar sync/async), y la higiene
de errores: `CursorAgentError` (nunca arrancó) vs `LLMEjecucionError` nueva (arrancó y no terminó
`finished`) son excepciones distintas a propósito.

**Hallazgo de presupuesto, medido en vivo:** sin restringir herramientas, cada llamada carga ~11.3k
tokens de entrada en definiciones de herramientas que este producto no usa (no navegamos el repo,
solo analizamos texto). Con `tools=[]` baja a ~3.3k — el default ahora, no una opción. Con US$50 de
presupuesto total esa diferencia importa.

**Instalación real:** `cursor-sdk==1.0.28` (confirmado instalándolo, no adivinado — requiere Python
≥3.10, que agregué al `.venv` local vía `brew install python@3.13` para tener el mismo entorno que
Render). Agregado al final de `api/requirements.txt`. `.env.example` y mi `.env` local ya traen
`LUMEN_MODELO_FUERTE=claude-opus-5`.

**Probado:** smoke test real contra la cuenta (gastó unos tokens, ~$0.00x) confirmó `status=finished`
end-to-end. `api/tests/test_llm_client.py` (5 tests, mockeados, sin gastar presupuesto en CI) fija
el guardarraíl de la higiene de errores. Suite completa: 44 passed.

**Qué sigue, en orden:** `/resolver` (contra el catálogo curado + `llm_client` para desambiguar),
luego `/justificacion` (el lector — el núcleo del producto), `/accion`, `/chat`.

**Nota de Twilio, en pausa:** el trial de Twilio (2026) exige `ContentSid` para mandar texto libre
por WhatsApp, y el sandbox clásico (+14155238886) ya no existe para cuentas nuevas — confirmado con
la API real y con la doc oficial. Sin resolver todavía: o encontramos la plantilla pre-aprobada del
trial, o se decide si vale la pena el upgrade de cuenta. Pausado por decisión de Freddy para priorizar
el bloque de IA, que estaba en cero.

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
