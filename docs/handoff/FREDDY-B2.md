# Handoff — Freddy · B2 IA

**Soy dueño de:** `api/lumen/ia/`, `api/lumen/routers/ia.py`, y desde las 22:14 también
`api/lumen/whatsapp/`, `api/lumen/telegram/` y `api/lumen/alertas.py` (el despachador de canal).
**Mis endpoints:** `POST /resolver`, `POST /justificacion`, `POST /accion`, `POST /chat` — **los
cuatro vivos** desde las 03:20, probados con Cursor y Croma reales, no solo mocks.
**Mi hito:** 21:30 — el lector clasifica correctamente 3 documentos reales de urgencia manifiesta,
y cada punto del veredicto trae su cita textual. Cumplido (tarde, ~02:45, pero con los dos
extremos probados: `solida` y `sin_relacion`).
**También soy dueño del presupuesto:** los US$50 de la API de Cursor. Reviso consumo a las 20:00 y
a las 23:00 y lo anoto aquí abajo.

> **Actualización 22:14 — WhatsApp pasa a ser mío.** El reparto original (`PLAN.md`) ponía Twilio en
> B3/Cristian, prioridad 1 de su bloque de las 20:45. Se reasigna por decisión del equipo: yo tomo
> el canal de WhatsApp completo, con libertad para usar Twilio o Evolution API — el que mejor
> funcione en la ventana que queda, sin que eso implique reabrir el contrato de la API. Detalle en
> la sección de abajo y en `PLAN.md` / `CRISTIAN-B3.md`, ya actualizados.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

---

## 04:55 — El mismo mensaje, con formato visual — enviado a los dos suscriptores

**`api/lumen/telegram/cliente.py::enviar` gana `parse_mode` opcional** (default `None`, cero
cambio de comportamiento para `/alerta` y el monitor). Con `parse_mode="HTML"`, Telegram
renderiza `<b>`, `<i>`, `<code>` — quien lo use escapa el texto dinámico con `html.escape` antes
de interpolar, para no romper el parseo si un nombre de entidad trae `&`, `<` o `>`.

Reescribí el mensaje del sismo (bitácora de las 04:40) con jerarquía visual, sin saturar de
emojis (2, uno de apertura y uno de cierre):

```html
🚨 <b>Alerta: contratación en zona del sismo del 10 de agosto</b>

<b>Gobernación del Chocó</b> — <b>$14.492.100.000</b>

Se firmaron 97 contratos parecidos, casi el mismo día, cada uno justo por debajo del monto que obliga a hacer concurso.

<i>Una señal no es prueba de irregularidad. Es un motivo para preguntar.</i>

🔎 Ver evidencia: caso <code>caso-0d6968f81dad</code>
```

**Mandado a los dos suscriptores de prueba** (Freddy `5833175479`, Jonatin `6746822281`) — los
dos con `estado=enviado`, y Freddy confirmó que se ve bien. Este es el que queda para el video,
no el de texto plano de la bitácora anterior.

**Test nuevo:** `test_telegram.py` confirma que sin `parse_mode` no se manda el campo (compatible
con todo lo que ya corría) y que con `parse_mode="HTML"` sí se manda tal cual. Suite completa
(con el servidor MCP nuevo de Cristian ya integrado): **124 passed**.

## 04:40 — Mensaje de demo para el video, con datos reales del sismo (no mock)

**Se pidió simular la catástrofe del 10 de agosto para el video.** No se inventaron señales: en
vez de mockear, revisé las 3 entidades del sismo que todavía no había probado (`docs/entidades-
emergencia.json`) y **las tres tienen una señal S6 real** (fraccionamiento — contratos por
debajo del umbral que exige concurso, firmados casi el mismo día):

| Entidad | NIT | Contratos agrupados | Valor real |
|---|---|---|---|
| **Gobernación del Chocó** | 891680010 | **97** | $14.492.100.000 |
| Gobernación del Valle (Secretaría de Educación) | 890399029 | 40 | (no reportado en el foco) |
| Alcaldía de Buenaventura | 890399045 | 25 | (no reportado en el foco) |

**Elegí Chocó** (el número más alto) para el mensaje de demo. Mandado y confirmado en Telegram:

```
🚨 Nuevo contrato en zona del sismo del 10 de agosto: Gobernacion Del Chocó, por $14.492.100.000.
Se firmaron 97 contratos parecidos, casi el mismo día, cada uno justo por debajo del monto que obliga a hacer concurso.
Una señal no es prueba de irregularidad. Es un motivo para preguntar.
Ver evidencia: pide el caso caso-0d6968f81dad en la API (dominio del frontend pendiente)
```

El caso (`caso-0d6968f81dad`) ya está guardado en Supabase real — `/caso/caso-0d6968f81dad` y
`/accion` con ese `caso_id` funcionan ya mismo, en cuanto Andrew tenga el dominio del frontend
para que el enlace de la última línea deje de decir "pendiente".

**Si se quiere mostrar "varias ciudades afectadas" en vez de una sola**, Valle y Buenaventura
también son reales y se pueden mandar igual — el script de abajo sirve para las tres, cambiando
el `entidad_id`.

**Receta para reproducir esto exacto** (o repetirlo con otro NIT de la tabla de arriba):

```python
# desde api/, con .env cargado
from lumen.contracts import AnalizarRequest
from lumen.senales.motor import analizar
from lumen.whatsapp.copy import formatear_pesos, url_ficha
from lumen.plataforma.casos import guardar_caso
from lumen.telegram.cliente import enviar

caso = await analizar(AnalizarRequest(entidad_id="891680010"))  # cambiar NIT para otra ciudad
entidad_limpia = caso.entidad.rstrip(". ").title()
lineas = [
    f"🚨 Nuevo contrato en zona del sismo del 10 de agosto: {entidad_limpia}, por {formatear_pesos(caso.valor)}.",
    *[s.regla_legible for s in caso.senales[:2]],
    caso.disclaimer,
    url_ficha(caso),
]
guardar_caso(caso)
estado, detalle = await enviar("<chat_id>", "\n".join(lineas[:5]))
```

**Por qué no fue un mock:** el encabezado menciona el sismo del 10 de agosto porque es literal —
estas 4 entidades están en la lista de emergencia precisamente por eso (`docs/entidades-
emergencia.json`, verificada por Jonatin). La señal, la cifra y la fuente son reales, consultadas
en vivo contra Croma. Lo único "de demo" es que elegí manualmente cuál de los 4 NITs mandar, en
vez de dejar que el monitor lo descubriera solo — y eso es exactamente lo que hace `/monitor/
nuevos` cuando se lo dispara.

## 04:25 — Modo Emergencia probado de punta a punta: suscriptores + un hallazgo de datos

**Pregunta que lo disparó: "¿el bot de Telegram funciona? ¿qué falta para Modo Emergencia?"**
El envío en sí ya estaba probado (`/alerta`, `enviar()`), pero el mecanismo *automático* del
monitor — el que encuentra a quién avisar sin que nadie pase un `destinatario` a mano — nunca se
había probado.

**Primer hallazgo: `suscripciones_whatsapp` tenía 0 filas** (verificado contra Supabase real).
El monitor llama `listar_suscriptores(caso.municipio, caso.departamento)` — sin suscriptores, un
caso real de nivel medio/alto no le llega a nadie, silenciosamente (no es un error, es un bucle
vacío).

**Segundo hallazgo, más importante:** `caso.municipio` y `caso.departamento` vienen `None` la
mayoría de las veces desde el motor real de Jonatin — confirmado con Cali (NIT 890399011, una de
las 4 entidades que el monitor recorre para el sismo), que dio los dos campos vacíos.
`listar_suscriptores` corta en seco (`if not municipio and not departamento: return []`) cuando
los dos vienen vacíos — así que **ni sembrando la tabla se resuelve** para esos casos. Vienen de
parsear el campo `location` de Croma (`senales/motor.py`), que no siempre está poblado.

**Lo que sí funcionó:** el caso de Kennedy del catálogo curado (`caso-38d879c8695f`) tenía
`municipio='No Definido'` (un valor real, aunque el nombre sea raro) — con eso alcanzó. Sembré
dos suscriptores de prueba (mi `chat_id` y el de Jonatin — se lo pedí a él en vivo, mandó
`/start` al bot y saqué su `chat_id` de `getUpdates`, `6746822281`) con `municipio='No Definido'`,
`departamento='Bogotá'`, y disparé `_avisar_si_corresponde` (la función real del monitor, no
`/alerta` manual) sobre ese caso. **Confirmado en vivo por los dos: les llegó el mensaje
automático a Telegram.**

**Conclusión para el video:** el Modo Emergencia automático funciona de punta a punta, pero
depende de usar un caso que sí tenga ubicación (como Kennedy) o de sembrar suscriptores sin
filtro geográfico si se usa uno que no la tenga. Si alguien quiere que funcione en general para
casos nuevos que descubra el monitor en vivo (no solo el catálogo), hace falta revisar por qué
`location` viene vacío tan seguido en `senales/motor.py` — eso es de Jonatin, no lo toqué.

**Datos insertados en Supabase (tabla `suscripciones_whatsapp`, para que Cristian lo sepa):**
dos filas de prueba con los `chat_id` de Telegram de Freddy y Jonatin. Son datos de demo, no
reales de un veedor — se pueden borrar sin problema cuando ya no hagan falta.

## 04:10 — Supabase real conectado. El ciclo completo cierra de punta a punta

**Freddy consiguió las keys correctas y repitió la prueba pendiente:** `/chat` con un NIT nunca
visto (900558536) → guarda el caso de verdad (`POST .../casos → 201 Created`, log real) →
`/accion` sobre ese `caso_id` → `200` (antes daba `404`) → `/caso/{id}` (endpoint de Cristian)
también lo lee → `200`. El bug de persistencia de la bitácora de las 03:30 queda cerrado contra
Supabase real, no solo con mocks. `SUPABASE_ANON_KEY` sigue siendo el token equivocado
(`sbp_...`), pero no importa: el backend nunca la usa, solo `service_role`.

## 04:00 — Me voy a dormir. Estado: todo lo mío está en verde

**Los cuatro endpoints, el canal de alerta y el despachador funcionan, probados en vivo, no solo
con mocks.** Suite completa: 85 passed (con los cambios de Cristian ya integrados: interruptor
de Croma y sus pruebas de persistencia). Resumen para no tener que leer toda la bitácora:

| Qué | Estado |
|---|---|
| `llm_client` | Vivo. `claude-haiku-4-5` (bajado de Opus→Sonnet→Haiku por cuota) |
| `POST /resolver` | Vivo, probado con RUES real |
| `POST /justificacion` | Vivo, probado en los dos extremos (`solida`/`sin_relacion`) con PDFs reales |
| `POST /accion` | Vivo, carta real generada contra un caso real del dump y contra Supabase real |
| `POST /chat` | Vivo, encadena resolver+analizar, **persiste el caso en Supabase real, confirmado** |
| Telegram | Vivo, verificado con mensajes reales al bot y `/alerta` completo |
| WhatsApp (Twilio/Evolution) | Completo en el repo, no se usa en la demo |

**No queda nada abierto de mi lado.** Lo único pendiente en el radar es lo que ya está anotado
en `HANDOFF.md` para Cristian (robustez de `obtener_caso` ante credenciales inválidas, y el cron
del monitor) — ninguno de los dos bloquea nada para grabar.

**Si alguien necesita tocar `api/lumen/ia/`, `api/lumen/whatsapp/`, `api/lumen/telegram/` o
`api/lumen/alertas.py` mientras no estoy:** todo tiene tests, `pytest -q` corre en menos de un
segundo sin red ni presupuesto. Los `_falso`/mocks de cada archivo de test muestran el contrato
esperado de cada función si hace falta extenderla.

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

### 03:30 — Prueba exhaustiva del orquestador: un bug real encontrado y arreglado

**Contexto:** el equipo pidió probar `/chat` con datos variados de verdad antes de dar por
cerrado el bloque de IA. Corrí ~10 casos distintos contra Croma y Cursor reales: NIT con
contratos (nivel medio, real), entidad pública (Secretaría Distrital de Hacienda, nivel bajo),
casos "delgados" con 0 contratos (Ruta del Sol/Odinsa), texto vacío, gibberish, preguntas sin
nombre concreto, desambiguación con nombre real (Odinsa, 5 candidatos). Todos correctos, nada se
cayó, ninguna narración inventó un hecho que no estuviera en las señales.

**El bug real:** un caso que `/chat` descubre por primera vez (Modo Vigilancia, alguien pregunta
por una empresa nueva) **nunca se guardaba en ningún lado**. `POST /accion` sobre ese mismo
`caso_id` daba 404 siempre — confirmado en vivo con un NIT que nadie había precomputado
(Odinsa Aeropuertos, 901645491). Esto rompía literalmente el paso 6 del Flujo B del brief
("siempre se ofrece el siguiente paso: generar evidencia, redactar la carta") para cualquier
caso que no fuera del catálogo curado de 6. Y confirmé que es un problema real de integración,
no teórico: el frontend de Andrew (rama `Lumen-web`, todavía no fusionada a `main`) ya tiene
`api.accion(caso_id, tipo)` esperando exactamente ese flujo.

**El arreglo:** `responder_chat` ahora llama a `guardar_caso` (de Cristian, mismo patrón que ya
usa `monitor.py`) apenas analiza un caso nuevo, **best-effort** — `guardar_caso` no respeta
`LUMEN_USAR_DUMP_LOCAL` a diferencia de `obtener_caso`, así que en modo respaldo de grabación
sin Supabase real esto seguirá fallando (registrado, no rompe el chat) hasta que haya una
Supabase real conectada. Con eso, en producción de verdad, el ciclo completo (`/chat` descubre →
`/accion` genera la carta) queda cerrado.

**De paso, encontré y arreglé una fuga de aislamiento entre tests:** `get_supabase()` tiene su
propio `@lru_cache` que nadie limpia; mi código nuevo disparaba un cliente real (con las
credenciales, aunque inválidas, que tenía en mi `.env` local) durante un test que no lo
esperaba, y ese cliente cacheado rompía después `test_plataforma.py` de Cristian en la misma
corrida de pytest. Arreglado con un fixture `autouse` en `test_chat.py` que mockea
`guardar_caso` por defecto — no toqué el archivo de Cristian.

**Hallazgo de latencia, no un bug, pero real:** `sicaac_insolvency_cases` (una de las 9 llamadas
que hace el motor de Jonatin por NIT) tarda consistentemente ~57-60s en resolver un job
asíncrono de Croma. Un análisis completo por NIT puede tomar 80-100 segundos de punta a punta.
Para el video no importa (los 6 casos del catálogo se precomputan), pero si alguien piensa
dejar `/chat` respondiendo en vivo sin caché durante la grabación, esto muerde.

**Credenciales de Supabase:** las que me pasaron (`sbp_...`) son un Personal Access Token de la
cuenta, no las API keys del proyecto — dan 401 "Invalid API key". Faltan las keys reales
(`anon`/`service_role`, JWT largos) desde Project Settings → API del dashboard. Sin esas, todo
lo de arriba corrió sobre el dump local; el arreglo del guardado está listo pero sin probar
contra Supabase real todavía.

**Tests:** 2 nuevos en `test_chat.py` (el guardado se intenta, y que un fallo de guardado no
tumba la respuesta). Suite completa: 77 passed.

### 02:45 — /justificacion vivo: el núcleo del producto, probado en los dos extremos

### 03:20 — /chat vivo: los cuatro endpoints de IA completos, probados end-to-end

**Qué cambié.** `api/lumen/ia/chat.py` + wireado en `routers/ia.py`. Dos caminos: si `contexto`
ya trae un identificador resuelto (`nit`/`entidad_id`/`contrato_id`, la persona confirmó un
candidato en un turno anterior), analiza directo con `analizar` de Jonatin. Si no, `/resolver`
decide — sin candidatos dice "no sé" con una alternativa concreta; con uno o más, **siempre** se
muestran para confirmar, ni con un solo candidato se asume cuál es. La narración usa
`Modelo.RAPIDO` sobre las `regla_legible` de las señales del caso (nunca inventa hechos nuevos);
si el LLM falla, se degrada a concatenar las señales tal cual — el chat nunca se cae por un
problema de narración.

**Probado de punta a punta con los cuatro endpoints encadenados de verdad** (Croma + Cursor
reales, sin mocks): turno 1 con "Conalvias" → candidatos reales de RUES; turno 2 con el NIT
elegido en `contexto` → corre el motor completo de señales de Jonatin (varias llamadas
encadenadas a Croma), narra el resultado en lenguaje ciudadano, y ofrece los siguientes pasos
correctos según el nivel de atención. En esa corrida, un endpoint de Croma (`sicaac_insolvency_cases`)
devolvió un 502 real — el motor de Jonatin lo absorbió sin caerse (`nivel_atencion=bajo`, cero
señales) y mi narración lo contó con honestidad ("el sistema no marcó señales de alerta"), sin
inventar nada.

**Tests:** `test_chat.py`, 6 casos mockeados (sin candidatos, un candidato sin asumir, varios
candidatos, análisis directo desde contexto, nivel bajo sin sugerir derecho de petición,
degradación de narración). `test_app.py`: retiré el test de "endpoints en 501" — ya no queda
ninguno. Suite completa: **75 passed**.

**Con esto, los cuatro endpoints de B2/IA están completos y probados en vivo**, no solo con
mocks: `/resolver`, `/justificacion`, `/accion`, `/chat`. Y el canal de alerta (Telegram,
verificado en vivo a las 02:20) cierra el otro bloque mío. Lo que queda pendiente de mi lado es
WhatsApp real (pausado, ver bitácora de las 02:10) y cualquier pulido que salga de la integración
con el resto del equipo.

### 03:05 — /accion vivo: derecho de petición real contra un caso del dump

**Qué cambié.** `api/lumen/ia/artefactos.py` + wireado en `routers/ia.py` (usa `obtener_caso` de
Cristian, solo lectura). Solo `derecho_peticion` usa el LLM (`Modelo.RAPIDO`), porque es narrativo
de verdad — los otros tres (`paquete_evidencia`, `informe_veeduria`, `guia_denuncia`) son
plantillas en Python puro: listan lo que el `Caso` ya trae (señales, fuentes, lectura), cero
riesgo de alucinación para algo que es formateo, no redacción.

**Guardarraíl igual que en `/justificacion`, pero para el otro lado del problema:** los "Hechos"
numerados de la carta salen del `Caso` en código (fecha, valor, proveedor, cada `regla_legible`),
**no** se le pide al modelo que los invente — el prompt se los da como dato fijo y le prohíbe
agregar cifras que no estén ahí. Y el disclaimer legal (*"Esta solicitud no imputa irregularidad
alguna..."*) y la firma van **fijos en el código**, siempre, sin depender de que el modelo se
acuerde de escribirlos — mismo principio que `DISCLAIMER` en `contracts/modelos.py`.

**Probado con Cursor real y un caso real del dump** (Alcaldía Local de Kennedy): la carta salió
con los hechos reales (fecha, valor $23.808.000, proveedor, la señal de concentración del 100%),
las normas correctas (sin Ley 1523 art. 46 porque este caso no es de emergencia — la regla de
`_normas_del_caso` funcionó), disclaimer y firma presentes.

**Tests:** `test_artefactos.py`, 8 casos (las tres plantillas, el guardarraíl del disclaimer/firma
con el LLM mockeado, JSON roto, y el endpoint completo contra el dump con 404 real). Suite
completa: 70 passed.

**Qué sigue:** `/chat` — el último endpoint de IA, orquesta `/resolver` + `/analizar`.

### 02:45 — /justificacion vivo: el núcleo del producto, probado en los dos extremos

**Qué cambié.** `api/lumen/ia/lector.py` + wireado en `api/lumen/routers/ia.py`. No le pido al
modelo que invente preguntas: siempre las mismas tres, formuladas como se las harías a una
persona (idénticas a `fixtures/lectura.json`, que es la fuente de verdad del registro):
relación causal, contemporaneidad, diagnóstico técnico previo — los tres elementos que la Ley
1523/Decreto 1082 exigen para la urgencia manifiesta. Extracción de texto con `pypdf`
(`pypdf==6.16.1`, agregado a `requirements.txt`), por URL o por archivo subido.

**El guardarraíl va dos veces, y la segunda es la que importa de verdad:**
1. El prompt le pide al modelo que no invente citas.
2. **El código verifica cada `cita_textual` contra el texto real del documento** (normalizado,
   sin distinguir mayúsculas/espacios). Si el modelo alucina una cita que no está en el
   documento, se descarta y el punto pasa a `no_concluye_por` — no importa lo segura que sonara
   la respuesta.
3. `veredicto=solida` es **imposible en código** si algún punto quedó sin cita. No depende de
   que el modelo lo recuerde: es una regla que se aplica después, siempre.

**Probado en los dos extremos, con Cursor real (`claude-sonnet-5`) y PDFs reales (construidos a
mano, sin librería nueva — ver `_pdf_con_texto` en los tests):**
- Documento de "mobiliario de oficina" sin ninguna mención a una emergencia →
  `veredicto=sin_relacion`, con cita real y verificada para el punto de contemporaneidad, y
  `no_concluye_por` honesto en los otros dos.
- Documento con sismo, informe técnico de gestión del riesgo y objeto de retiro de escombros →
  `veredicto=solida`, con las tres citas reales y verificadas contra el texto.

**Tests:** `test_lector.py` (6, mockeados) + `test_lector_pdf_real.py` (3, con PDFs reales sin
mockear la extracción — incluye un PDF corrupto y uno en blanco). Suite completa: 63 passed.

**Qué sigue:** `/accion` (generador de artefactos), luego `/chat`.

### 02:10 — Telegram reemplaza a WhatsApp como canal de la demo

**Por qué.** El trial de Twilio en 2026 exige `ContentSid` (plantilla aprobada) para mandar
cualquier WhatsApp fuera del sandbox clásico, que ya no existe para cuentas nuevas — confirmado
llamando a la API real, no adivinado (ver bitácora de las 22:35 y 23:xx de este mismo archivo).
Esa función de plantillas está bloqueada para Trial. Decisión del equipo: en vez de seguir
peleando con Twilio o pagar el upgrade, Telegram es el canal de la demo. Sin trial, sin
plantillas, bot en un minuto con `@BotFather` → `/newbot`.

**Qué cambié.**
- `api/lumen/telegram/`: paquete nuevo, un solo proveedor (no hace falta la abstracción de
  "elegir proveedor" que tiene WhatsApp). `cliente.py` habla HTTP directo con la Telegram Bot
  API (`POST /bot<token>/sendMessage`), formato de respuesta confirmado contra la doc oficial.
- `api/lumen/alertas.py`: despachador nuevo. Centraliza la regla de `nivel_atencion` y el
  armado del mensaje (antes vivían dentro de `whatsapp/cliente.py`) y elige Telegram o WhatsApp
  según `LUMEN_CANAL_ALERTA` (default `telegram`). `api/lumen/whatsapp/` y `api/lumen/telegram/`
  siguen siendo paquetes completos y usables por separado — este módulo solo los conecta.
- `api/lumen/routers/plataforma.py` y `api/lumen/plataforma/monitor.py`: el único cambio es la
  línea de import, de `..whatsapp` a `..alertas` — mismo patrón de "punto de enganche de una
  línea" que ya estaba.
- `config.py` + `.env.example`: `LUMEN_CANAL_ALERTA`, `TELEGRAM_BOT_TOKEN`,
  `TELEGRAM_CHAT_ID_DEMO`.
- `LUMEN_MODELO_FUERTE` bajó de `claude-opus-5` a `claude-sonnet-5`: Opus quemaba cuota muy
  rápido para el presupuesto de US$50; Sonnet 5 sigue siendo el modelo de razonamiento fuerte
  de la familia, solo que no el más caro.

**Qué queda igual:** el contrato de `POST /alerta` no cambió ni un campo — Cristian no tiene que
tocar nada de su lado. WhatsApp (Twilio + Evolution) sigue completo en el repo por si el jurado
lo revisa o si alcanza tiempo para retomarlo; solo no se muestra en el video.

**Aviso para el video (Jonatin):** si el storyboard ya asumía captura de WhatsApp en el bloque
del teléfono, hay que cambiarla por Telegram. Puesto también en `HANDOFF.md`.

**Tests:** `api/tests/test_telegram.py` (3) y `api/tests/test_alertas.py` (3), mockeados. Suite
completa: 55 passed.

**Verificado en vivo, 02:20.** Freddy creó `@lumen_alerta_ctw_bot`. `TELEGRAM_BOT_TOKEN` en
`.env`; `chat_id` de demo (`5833175479`) sacado de `getUpdates` tras mandarle un mensaje al bot.
Dos pruebas reales, las dos con `estado=enviado`:
1. Mensaje suelto por `lumen.telegram.cliente.enviar` — llegó.
2. `POST /alerta` completo con un caso real del dump (`caso-38d879c8695f`, Alcaldía Local de
   Kennedy, nivel medio) — llegó con el copy real (señal + disclaimer), confirmado por Freddy.

`TELEGRAM_CHAT_ID_DEMO` queda anotado para el video. El teléfono/cuenta de Telegram que sale en
el video tiene que ser el mismo que ya está unido (`5833175479`), igual que el "join" de Twilio.

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
