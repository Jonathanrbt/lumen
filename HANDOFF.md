# HANDOFF.md — estado global

Índice. El detalle vive en el archivo de cada uno, para que cuatro personas no editen el mismo sitio:

- [`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md) — datos, Croma, señales, grafo, video
- [`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) — IA, lector, prompts, artefactos
- [`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md) — FastAPI, Supabase, monitor, deploy
- [`docs/handoff/ANDREW-WEB.md`](docs/handoff/ANDREW-WEB.md) — frontend

Brief vivo: [`docs/brief-final-claude.md`](docs/brief-final-claude.md). Reloj y carpetas: [`docs/PLAN.md`](docs/PLAN.md). Contrato: [`docs/CONTRATO-API.md`](docs/CONTRATO-API.md). Copy de señales: [`docs/COPY-SENALES.md`](docs/COPY-SENALES.md).

## Ahora (domingo 16.ago ~02:10)

🚨 **Cambio que afecta el video: el canal de la demo pasa a ser Telegram, no WhatsApp.**
Twilio (2026) exige que cualquier cuenta trial mande WhatsApp con plantillas pre-aprobadas
(`ContentSid`) y esa función está bloqueada para trial — confirmado contra la API real, no
adivinado. Telegram no tiene ese problema (bot en un minuto, sin trial, sin plantillas).
`POST /alerta` sigue exactamente igual por fuera; por dentro `api/lumen/alertas.py` elige el
canal con `LUMEN_CANAL_ALERTA` (default `telegram`). El código de WhatsApp (Twilio y Evolution
API) queda completo y funcional en `api/lumen/whatsapp/`, pero **no se muestra en el video** —
si alguien ya planeó el storyboard con captura de pantalla de WhatsApp, hay que cambiarla por
Telegram. Detalle en [`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md).

**B1 motor vivo + lista de emergencia para el monitor:** Cali, Buenaventura, Valle y Chocó
están en [`docs/entidades-emergencia.json`](docs/entidades-emergencia.json). Cristian recorre
esos NITs; no hay barrido por ciudad. Detalle en
[`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md).

Andamio listo. Croma verificado. IA de Freddy: `llm_client` y `/resolver` vivos; `/justificacion`,
`/accion`, `/chat` siguen en 501 — es lo más atrasado del proyecto ahora mismo.

**Croma:** el motor consulta la **API HTTP** (`POST /co/…/v1`). Sin `CROMA_MCP_URL`.
Guías y aliases en `HERRAMIENTAS.md` §1. Leer la guía **antes** de cada `consultar`.

Pendiente de producto: `/justificacion` (el núcleo del producto, Freddy), `/accion`, `/chat`.
Link del repo oficial. Supabase cloud. Frontend (Andrew). NITs del catálogo curado que Croma
aún no resolvió (handoff B1). Bot de Telegram real (crearlo es cosa de Freddy/Cristian, quien
llegue primero — `@BotFather` → `/newbot`).

No tocar: `.githooks/pre-commit`, `api/lumen/contracts/` sin anunciarlo, `supabase/migrations/` si no eres Cristian, `web/` si no eres Andrew.
