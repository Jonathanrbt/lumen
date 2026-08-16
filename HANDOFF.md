# HANDOFF.md — estado global

Índice. El detalle vive en el archivo de cada uno, para que cuatro personas no editen el mismo sitio:

- [`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md) — datos, Croma, señales, grafo, video
- [`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) — IA, lector, prompts, artefactos
- [`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md) — FastAPI, Supabase, monitor, deploy
- [`docs/handoff/ANDREW-WEB.md`](docs/handoff/ANDREW-WEB.md) — frontend

Brief vivo: [`docs/brief-final-claude.md`](docs/brief-final-claude.md). Reloj y carpetas: [`docs/PLAN.md`](docs/PLAN.md). Contrato: [`docs/CONTRATO-API.md`](docs/CONTRATO-API.md). Copy de señales: [`docs/COPY-SENALES.md`](docs/COPY-SENALES.md).

## Ahora (domingo 16.ago ~03:45)

🚨 **No hay pitch presencial: solo se sube el video.** El jurado decide sin Q&A en vivo y
probablemente sin revisar código — el video es el entregable que más pesa. Ver
[`docs/GUION-VIDEO-v3.2.md`](docs/GUION-VIDEO-v3.2.md) (propuesta de Freddy, actualiza el
storyboard v3.1 con Telegram y el chat ya no como hard-cut).

🚨 **`web/` sigue vacío — sin commits desde el andamio inicial (17:56), bitácora de Andrew sin
actualizar desde las 17:30.** Sin frontend no hay nada que grabar para los bloques 0:26–0:55 del
video, sin importar qué tan bueno esté el guion. Es el riesgo más grande del proyecto ahora
mismo. Andrew está trabajando, se espera su push.

🚨 **Jonatin (dueño del video) no está disponible ahora mismo.** El equipo necesita decidir quién
graba si él no puede retomarlo a tiempo para el corte de las 08:00.

✅ **Los cuatro endpoints de IA (B2/Freddy) están completos: `/resolver`, `/justificacion`,
`/accion`, `/chat`.** Probados de punta a punta con Croma y Cursor reales, encadenados (un turno
de `/chat` resuelve un nombre, el siguiente corre el motor completo de señales de Jonatin y
narra el resultado). Detalle y evidencia en
[`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md).

🚨 **El canal de la demo es Telegram, no WhatsApp — verificado en vivo.** Twilio (2026) exige
plantillas aprobadas (`ContentSid`) para cuentas trial, bloqueado para trial — confirmado contra
la API real. `POST /alerta` sigue igual por fuera; `api/lumen/alertas.py` elige el canal con
`LUMEN_CANAL_ALERTA` (default `telegram`). WhatsApp (Twilio + Evolution) queda completo en el
repo, **no se muestra en video**. Si el storyboard ya asumía WhatsApp en pantalla, cambiar por
Telegram.

**B1 motor vivo + lista de emergencia para el monitor:** Cali, Buenaventura, Valle y Chocó
están en [`docs/entidades-emergencia.json`](docs/entidades-emergencia.json). Cristian recorre
esos NITs; no hay barrido por ciudad. Detalle en
[`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md).

**Croma:** el motor consulta la **API HTTP** (`POST /co/…/v1`). Sin `CROMA_MCP_URL`.
Guías y aliases en `HERRAMIENTAS.md` §1. Leer la guía **antes** de cada `consultar`.

Pendiente de producto: link del repo oficial. Supabase cloud (para que `/accion` y `/alerta`
lean casos reales, no solo el dump). Frontend (Andrew). NITs del catálogo curado que Croma aún
no resolvió (handoff B1). WhatsApp real, si sobra tiempo (pausado por decisión de Freddy).

**Dato suelto para Cristian:** `GET /monitor/nuevos` no tiene ningún cron real que lo dispare —
solo existe el keep-alive de `/health`. El monitor "corre solo" del brief hoy es manual. No
bloquea el video (se puede disparar a mano al grabar), pero vale la pena saberlo.

No tocar: `.githooks/pre-commit`, `api/lumen/contracts/` sin anunciarlo, `supabase/migrations/` si no eres Cristian, `web/` si no eres Andrew.
