# HANDOFF.md — estado global

Índice. El detalle vive en el archivo de cada uno, para que cuatro personas no editen el mismo sitio:

- [`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md) — datos, Croma, señales, grafo, video
- [`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) — IA, lector, prompts, artefactos
- [`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md) — FastAPI, Supabase, monitor, deploy
- [`docs/handoff/ANDREW-WEB.md`](docs/handoff/ANDREW-WEB.md) — frontend

Brief vivo: [`docs/brief-final-claude.md`](docs/brief-final-claude.md). Reloj y carpetas: [`docs/PLAN.md`](docs/PLAN.md). Contrato: [`docs/CONTRATO-API.md`](docs/CONTRATO-API.md). Copy de señales: [`docs/COPY-SENALES.md`](docs/COPY-SENALES.md).

## Ahora (domingo 16.ago ~04:00) — Freddy se va a dormir, backend en verde

**Freddy (B2) deja los cuatro endpoints de IA completos y probados en vivo** (`/resolver`,
`/justificacion`, `/accion`, `/chat`), el canal de alerta (Telegram) verificado, y un bug de
integración real encontrado y arreglado — ver el detalle completo de todo esto en
[`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md), que tiene la bitácora entera. Suite
de tests: **77 passed**. No vuelve a estar disponible hasta que se levante — lo de abajo es para
que Jonatin y Cristian puedan seguir sin esperarlo.

### ✅ Buenas noticias primero

- **`web/` ya no es un riesgo — está fusionado a `main`.** Andrew terminó las 4 pantallas +
  Landing (React/Vite/TS, grafo con react-flow), y sus tipos de TypeScript coinciden **campo por
  campo** con los contratos de Python — revisado a mano, cero sorpresas de integración
  esperables. `web/src/lib/api.ts` ya llama a los nueve endpoints con el contrato exacto y cae a
  `fixtures/` si la red falla.
- **No hay pitch presencial: solo se sube el video.** El jurado decide sin Q&A en vivo y
  probablemente sin revisar código — el video es el entregable que más pesa. Hay una propuesta
  de guion lista en [`docs/GUION-VIDEO-v3.2.md`](docs/GUION-VIDEO-v3.2.md) (actualiza el
  storyboard v3.1: Telegram en vez de WhatsApp, y el bloque del chat ya no es un hard-cut porque
  `/chat` funciona de verdad).

### Para Jonatin, cuando esté disponible

1. **Ya puedes grabar.** `web/` existe, los 9 endpoints responden, el canal de Telegram manda
   mensajes reales. Lo único que falta es que alguien dispare el flujo (ver punto 3 de Cristian)
   o uses el catálogo curado precomputado.
2. **Revisa `docs/GUION-VIDEO-v3.2.md` antes de grabar** — es una propuesta, no una decisión
   tomada, pero tiene los dos cambios reales que ya no son opcionales (Telegram, no WhatsApp; el
   chat ya no se corta).
3. **Dato para tu motor de señales:** `sicaac_insolvency_cases` (una de las 9 llamadas por NIT)
   tarda consistentemente ~57-60s en resolver un job asíncrono de Croma. Un análisis completo
   puede tomar 80-100s de punta a punta. No importa para el video si los 6 casos del catálogo ya
   están precomputados y cacheados — pero si vas a re-correr `scripts/precomputar_casos_demo.py`
   para refrescar el dump (ahora que `/accion` y `/chat` también funcionan), cuenta con que cada
   caso tarda ~1-1.5 minutos.

### Para Cristian, cuando esté disponible

1. ✅ **Supabase real, resuelto.** Freddy consiguió las keys correctas (JWT reales) y probó de
   punta a punta: `/chat` con un NIT nunca visto → guarda el caso (`POST .../casos → 201
   Created`) → `/accion` sobre ese mismo `caso_id` → `200` → `/caso/{id}` también lo lee. El
   ciclo completo Modo Vigilancia → persistencia → acción queda cerrado contra Supabase real, no
   solo mocks. `.env` local de Freddy ya tiene las keys si hace falta comparar.
2. **`obtener_caso` no distingue "Supabase no configurado" de "Supabase configurado pero con
   credenciales inválidas"** — lo segundo revienta con un `postgrest.exceptions.APIError` crudo
   (500) en vez de un 503 limpio, en `/caso/{id}`, `/accion` y `/alerta` (los tres usan la misma
   función). Vale la pena que `SupabaseNoConfigurado` también capture ese caso, o que
   `get_supabase()` valide antes de cachear el cliente. Sigue sin arreglar, no bloquea nada.
3. **`GET /monitor/nuevos` no tiene ningún cron real que lo dispare** — solo existe el
   keep-alive de `/health` cada 10 min. El monitor "corre solo" del brief hoy es manual. No
   bloquea el video (se dispara a mano al grabar), pero es la pieza que falta para que el
   Modo Emergencia sea automático de verdad.
4. **`chat.py` ahora llama a tu `guardar_caso`** cuando el Modo Vigilancia descubre un caso
   nuevo — verificado que ya persiste de verdad (punto 1). Sigue siendo best-effort: si Supabase
   falla, se registra y el chat no se cae.

### El resto, como estaba

**Twilio queda descartado como canal de demo** (Trial 2026 exige plantillas aprobadas,
bloqueado). WhatsApp (Twilio + Evolution) sigue completo y funcional en el repo, solo no se
muestra en video. `LUMEN_CANAL_ALERTA=telegram` es el default.

**B1 motor vivo + lista de emergencia para el monitor:** Cali, Buenaventura, Valle y Chocó
están en [`docs/entidades-emergencia.json`](docs/entidades-emergencia.json). Cristian recorre
esos NITs; no hay barrido por ciudad. Detalle en
[`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md).

**Croma:** el motor consulta la **API HTTP** (`POST /co/…/v1`). Sin `CROMA_MCP_URL`.
Guías y aliases en `HERRAMIENTAS.md` §1. Leer la guía **antes** de cada `consultar`.

Pendiente de producto: link del repo oficial. Supabase cloud con las keys reales (punto 1 de
Cristian arriba). NITs del catálogo curado que Croma aún no resolvió (handoff B1). WhatsApp
real, si sobra tiempo (pausado por decisión de Freddy).

No tocar: `.githooks/pre-commit`, `api/lumen/contracts/` sin anunciarlo, `supabase/migrations/` si no eres Cristian, `web/` si no eres Andrew.
