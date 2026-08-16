# HANDOFF.md — estado global

Índice. El detalle vive en el archivo de cada uno, para que cuatro personas no editen el mismo sitio:

- [`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md) — datos, Croma, señales, grafo, video
- [`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) — IA, lector, prompts, artefactos
- [`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md) — FastAPI, Supabase, monitor, deploy
- [`docs/handoff/ANDREW-WEB.md`](docs/handoff/ANDREW-WEB.md) — frontend

Brief vivo: [`docs/brief-final-claude.md`](docs/brief-final-claude.md). Reloj y carpetas: [`docs/PLAN.md`](docs/PLAN.md). Contrato: [`docs/CONTRATO-API.md`](docs/CONTRATO-API.md). Copy de señales: [`docs/COPY-SENALES.md`](docs/COPY-SENALES.md).

## Ahora (sábado 15.ago ~23:40)

**B1 motor vivo + lista de emergencia para el monitor:** Cali, Buenaventura, Valle y Chocó
están en [`docs/entidades-emergencia.json`](docs/entidades-emergencia.json). Cristian recorre
esos NITs; no hay barrido por ciudad. Detalle en
[`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md).

Andamio listo. Croma verificado. IA de Freddy sigue en 501.

**Croma:** el motor consulta la **API HTTP** (`POST /co/…/v1`). Sin `CROMA_MCP_URL`.
Guías y aliases en `HERRAMIENTAS.md` §1. Leer la guía **antes** de cada `consultar`.

**Cambio de reparto:** WhatsApp/Twilio se reasignó de Cristian a Freddy tras el timebox de las
20:45–21:45. Vive en `api/lumen/whatsapp/`, carpeta nueva; Freddy puede usar Twilio o Evolution API.
Cristian conserva `/alerta` como puerta del contrato. Detalle en
[`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) y
[`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md).

Pendiente de producto: WhatsApp real (Freddy). Link del repo oficial. Supabase cloud. `llm_client` (Freddy). Frontend (Andrew). NITs del catálogo curado que Croma aún no resolvió (handoff B1).

No tocar: `.githooks/pre-commit`, `api/lumen/contracts/` sin anunciarlo, `supabase/migrations/` si no eres Cristian, `web/` si no eres Andrew.
