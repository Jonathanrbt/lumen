# HANDOFF.md — estado global

Este archivo lleva **solo el estado del proyecto entero**. El detalle de cada persona vive en su
propio archivo, para que cuatro personas no editen el mismo sitio a la vez:

- [`docs/handoff/JONATIN-B1.md`](docs/handoff/JONATIN-B1.md) — datos, Croma, señales, grafo, video
- [`docs/handoff/FREDDY-B2.md`](docs/handoff/FREDDY-B2.md) — IA, lector, prompts, artefactos
- [`docs/handoff/CRISTIAN-B3.md`](docs/handoff/CRISTIAN-B3.md) — FastAPI, Supabase, monitor, deploy
- [`docs/handoff/ANDREW-WEB.md`](docs/handoff/ANDREW-WEB.md) — frontend completo

---

## Última actualización

**Sábado 15.ago.2026, 19:20 · por el agente de Jonatin**

### Se aplicó el parche v3.1 a todo el repo

Llegó [`docs/patch_v3.1_lumen_usuario_y_pitch.md`](docs/patch_v3.1_lumen_usuario_y_pitch.md), tres
reemplazos sobre el brief v3 a partir del feedback de una mentora en gestión de riesgo de desastres
que además es veedora. **No cambia el alcance, el stack, los roles ni el cronograma. Cambia para
quién es el producto y cómo se cuenta.**

Lo que se propagó:

- **Usuario primario: el veedor**, no "el ciudadano que no sabe qué es SECOP". Ese usuario no existe
  como usuario activo. El veedor sabe qué quiere revisar; lo que no tiene son las ocho horas que
  cuesta cruzar SECOP con el RUES contrato por contrato. Y suele ser una persona mayor, lo cual
  cambia el diseño de la interfaz de verdad, no solo el copy.
- **`docs/COPY-SENALES.md`, nuevo y fuente única.** Las nueve frases de señal en lenguaje ciudadano,
  las reglas de copy y la tabla de "no digas / di". Lo comparten B1 (las produce), B2 (narra en ese
  registro), Andrew (las pinta) y Cristian (las manda por WhatsApp). Se escriben una sola vez.
- **El disclaimer cambió de texto** a *"Una señal no es prueba de irregularidad. Es un motivo para
  preguntar."* Está en la constante `DISCLAIMER` de `contracts/modelos.py`, así que quien la use no
  tiene que hacer nada.
- **Los fixtures ya traen el copy nuevo**, incluidas las preguntas del lector, que ahora se formulan
  como se las harías a una persona. Lo que Andrew maquete contra ellos ya es el texto bueno.
- **Storyboard del video reemplazado:** sin leyes, sin cifras en dólares, con protagonista. Las
  leyes no se borran, se mudan al README, al cuerpo de la carta y a las respuestas al jurado.
- **Los cuatro handoffs actualizados** con lo que le cambia a cada quien, y `docs/PLAN.md` tiene una
  tabla nueva de validación cruzada: quién produce cada pieza del v3.1 y quién la consume.

### Las dos decisiones que el parche abrió, ya cerradas (19:30)

**1. Twilio sube a prioridad 1 de Cristian.** El parche convierte WhatsApp en la tesis del producto y
el storyboard le da 11 de los 60 segundos, así que el hard-cut #3 dejó de ser un recorte barato.
Cristian crea la cuenta esta noche y a las 20:45 Twilio es lo primero que toca, con **timebox de 60
minutos y corte a las 21:45**. Si se corta, se lo dice a Jonatin de inmediato, porque hay que
reescribir el bloque 0:15–0:26 del storyboard antes de grabar. Lo que no se hace nunca: mockear un
WhatsApp falso.

**2. El hito de las 23:00 tiene dueño: Jonatin.** Encaja porque a esa hora su bloque es validar los 6
casos curados, y recorrer el flujo y elegir el caso del video son la misma tarea. Con tres reglas
escritas en `docs/PLAN.md`: no toca el teclado del backend, dice en voz alta si el flujo existe, y si
no existe aplica los hard-cuts sin abrir debate. **A las 23:20 vuelve al video pase lo que pase.**

**3.** Se retiró la sección de agradecimientos del README, por decisión del equipo.

---

## Bloque anterior

**Sábado 15.ago.2026, 17:30 · por el agente de Jonatin**

### Qué se hizo en este bloque

Se montó el andamio del repositorio desde cero. No existía nada: ni git, ni backend, ni documentos
de trabajo. Solo `AGENTS.md`, el brief v3 y el PDF del deck.

Lo que quedó en pie:

- **Repositorio git inicializado** con `.gitignore` agresivo y un hook `pre-commit` que bloquea el
  commit si detecta un token de Croma, una llave de Render, un JWT de Supabase o una cadena de
  conexión con contraseña. El repo va a ser público desde el primer commit y manejamos credenciales
  reales, así que la protección va antes que el código.
- **`PROYECTO.md` y `HERRAMIENTAS.md`**, que `AGENTS.md` exige y no existían. El primero destila el
  brief y congela el corte; el segundo inventaria accesos verificados.
- **`docs/PLAN.md`** con el reparto por nombre, el mapa de propiedad de carpetas, el protocolo de
  git y el reloj recalculado desde las 17:30.
- **El contrato de la API de §5.5** implementado como modelos Pydantic, más un fixture JSON por
  endpoint. Esto es lo que permite que los cuatro trabajen en paralelo sin bloquearse.
- **Esqueleto de FastAPI** con configuración por variables de entorno, CORS configurable y los nueve
  endpoints declarados como stubs, repartidos en tres archivos de router para que cada dueño edite
  el suyo.
- **Cliente de Croma funcionando y probado contra el servidor real.**

### El hallazgo que cambia cosas

**Croma no es una API REST: es un servidor MCP remoto** en `https://api.croma.run/mcp`, que habla
JSON-RPC sobre HTTP con respuestas en SSE. El brief no lo especificaba y era la incógnita más grande
del proyecto, porque de ello dependía si el backend en Render podía usar Croma o no.

Se verificó en vivo y la respuesta es sí, con una ventaja: **el servidor es stateless**, así que no
hace falta handshake ni sesión. Un `POST` suelto con `tools/call` devuelve el resultado. Se probó
`rues_entities_by_name` con "Conalvias" y devolvió registros reales de Cámara de Comercio.

El cliente ya está escrito en `api/lumen/croma/client.py`. B1 no tiene que resolver transporte: se
sienta directamente sobre las señales.

### Qué quedó a medias

- **Twilio.** No tenemos cuenta y la decisión está aplazada. Es el hard-cut #3. Las variables de
  entorno ya están declaradas en `.env.example` por si se resuelve.
- **El link del repositorio oficial de entrega.** El deck lo deja pendiente y dice que se anuncia
  por Discord. Hay que preguntárselo a un Ops Manager antes de las 20:00.
- **El proyecto de Supabase** no está creado. Es lo primero de Cristian.
- **`web/` está vacía a propósito.** Andrew decide todo el stack del frontend.

### Qué no hay que tocar

- **`.githooks/pre-commit` y `.gitignore`.** Si el hook te estorba, avisa en el chat antes de
  desactivarlo.
- **`api/lumen/contracts/`** sin anunciarlo. Es el vocabulario compartido de los cuatro.
- **`supabase/migrations/`** si no eres Cristian.
- **`web/`** si no eres Andrew.

### Cómo probar que el andamio funciona

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt
Copy-Item .env.example .env      # pega CROMA_API_KEY del chat privado
uvicorn lumen.main:app --reload --app-dir api
```

Luego abre `http://127.0.0.1:8000/health` (debe responder `ok`) y
`http://127.0.0.1:8000/health/croma` (hace una llamada real a Croma y confirma que tu token sirve).
La documentación interactiva con los nueve endpoints está en `http://127.0.0.1:8000/docs`.

### Lo siguiente, por persona

- **Los cuatro, ahora:** clonar, `.env`, venv, `/health/croma` en verde, y **leer el contrato de la
  API en `docs/CONTRATO-API.md`**. Si algo no cuadra, se cambia ahora, no a medianoche.
- **Jonatin (B1):** verificar las tres capas de datos de §6 y empezar las 8 señales.
- **Freddy (B2):** `Cursor.models.list()`, fijar los dos modelos y blindar el `llm_client`.
- **Cristian (B3):** crear el proyecto de Supabase y dejar un hello world desplegado en Render
  antes de las 19:00.
- **Andrew (UI/UX):** montar su stack y empezar contra los fixtures.
