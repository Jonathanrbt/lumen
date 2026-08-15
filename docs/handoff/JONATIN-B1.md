# Handoff — Jonatin · B1 Datos (+ video desde las 22:00)

**Soy dueño de:** `api/lumen/croma/`, `api/lumen/senales/`, `api/lumen/routers/analisis.py`,
`video/`, y la coordinación (`PROYECTO.md`, `README.md`, `HANDOFF.md`).
**Mis endpoints:** `POST /analizar`, `GET /red/{nit}`.
**Mis hitos:** 20:45 el motor escupe señales con fuente sobre un caso real · 22:00 congelo B1 y me
voy al video · 03:30 primer corte grabado · 08:00 video final subido.
**Mi suplente después de las 22:00:** Cristian, para la revisión final de señales y fuentes.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

---

## 17:30 — Andamio montado

**Qué cambié.** Monté el repositorio entero desde cero: git, protección de secretos, los documentos
que `AGENTS.md` exige, el contrato de la API con sus fixtures, el esqueleto de FastAPI y el cliente
de Croma.

**El hallazgo importante.** Croma es un servidor MCP remoto, no una API REST. Lo probé en vivo: es
stateless, un `POST` JSON-RPC basta, y devuelve datos reales. El transporte ya está resuelto en
`api/lumen/croma/client.py`, así que arranco directo en las reglas de señales.

**Qué quedó a medias.** `api/lumen/senales/` está vacío salvo el esqueleto. Ninguna de las 8 señales
está implementada.

**Qué no hay que tocar.** El cliente de Croma mientras yo esté dentro. Si necesitas una herramienta
nueva de Croma, `client.call_tool(nombre, argumentos)` ya sirve para cualquiera de las que expone el
servidor: no hace falta modificar el cliente.

**Cómo se prueba lo mío en 30 segundos.** `GET /health/croma` hace una llamada real y devuelve el
nombre del servidor y cuántas herramientas expone.

---

## Pendientes míos, en orden

1. **Verificar las tres capas de datos de §6 antes de las 20:00.** Es el riesgo número uno del
   proyecto. Si el análogo histórico no da señales, hay que saberlo esta noche.
2. Las 8 señales corriendo en CLI, cada una con regla legible, dato y fuente con fecha.
3. Grafo de actores, curado, entre 5 y 12 nodos.
4. Validar a mano los 6 casos del catálogo. Ninguno puede tener un falso positivo vergonzoso:
   aparecen en el video.

---

## Notas para el video (se llenan desde las 22:00)

- Caso elegido para el bloque de 0:28–0:40:
- Documento de urgencia manifiesta que se muestra:
- Teléfono que recibe la alerta:
