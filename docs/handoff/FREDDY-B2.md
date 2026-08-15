# Handoff — Freddy · B2 IA

**Soy dueño de:** `api/lumen/ia/`, `api/lumen/routers/ia.py`.
**Mis endpoints:** `POST /resolver`, `POST /justificacion`, `POST /accion`, `POST /chat`.
**Mi hito:** 21:30 — el lector clasifica correctamente 3 documentos reales de urgencia manifiesta,
y cada punto del veredicto trae su cita textual.
**También soy dueño del presupuesto:** los US$50 de la API de Cursor. Reviso consumo a las 20:00 y
a las 23:00 y lo anoto aquí abajo.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

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

## Bitácora

### 17:30 — Todavía no arranco

El esqueleto de mis cuatro endpoints ya está en `api/lumen/routers/ia.py`, devolviendo `501` con un
mensaje que dice de quién es cada uno. Los modelos que tengo que devolver están en
`api/lumen/contracts/` y hay un JSON de ejemplo por endpoint en `fixtures/`.

**Consumo de la API de Cursor:** sin medir todavía.
