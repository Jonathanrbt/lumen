# HANDOFF.md — estado global

Índice. El detalle vive en el archivo de cada uno, para que cuatro personas no editen el mismo sitio:

- [`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md) — datos, Croma, señales, grafo, video
- [`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) — IA, lector, prompts, artefactos
- [`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md) — FastAPI, Supabase, monitor, deploy
- [`docs/handoff/ANDREW-WEB.md`](docs/handoff/ANDREW-WEB.md) — frontend

Brief vivo: [`docs/brief-final-claude.md`](docs/brief-final-claude.md). Reloj y carpetas: [`docs/PLAN.md`](docs/PLAN.md). Contrato: [`docs/CONTRATO-API.md`](docs/CONTRATO-API.md). Copy de señales: [`docs/COPY-SENALES.md`](docs/COPY-SENALES.md).

## Ahora (sábado 15.ago ~22:14)

Andamio listo. Empieza el build. Croma verificado. Endpoints en 501 por dueño.

**Cambio de reparto:** WhatsApp/Twilio se reasignó de Cristian a Freddy tras el timebox de las
20:45–21:45. Vive en `api/lumen/whatsapp/`, carpeta nueva; Freddy puede usar Twilio o Evolution API.
Cristian conserva `/alerta` como puerta del contrato. Detalle en
[`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) y
[`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md).

Pendiente de producto: WhatsApp real (ahora prioridad de Freddy). Link del repo oficial de entrega. Supabase cloud. Motor de señales (Jonatin). `llm_client` (Freddy). Frontend (Andrew).

No tocar: `.githooks/pre-commit`, `api/lumen/contracts/` sin anunciarlo, `supabase/migrations/` si no eres Cristian, `web/` si no eres Andrew.
