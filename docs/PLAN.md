# PLAN.md — cómo trabajamos las próximas horas

Somos cuatro personas metiendo commits al mismo monorepo con quince horas por delante. Este archivo
existe para una sola cosa: **que nadie se pise con nadie.** Léelo entero una vez, ahora. Después es
consulta.

Congelado el sábado 15.ago.2026 a las 17:30. Actualizado a las 19:20 con el reparto del parche v3.1
y el dueño del hito de las 23:00.

---

## 1. Quién es quién

| Rol | Persona | De qué es dueño | Endpoints suyos |
|---|---|---|---|
| **B1 — Datos** | **Jonatin** | Cliente Croma, normalización, las 8 señales, el grafo de actores, validación a mano del catálogo curado y de los casos históricos | `/analizar`, `/red/{nit}` |
| **B2 — IA** | **Freddy** | `llm_client` blindado, lector de justificaciones, resolución de entidades, prompts, narración ciudadana, generador de artefactos | `/resolver`, `/justificacion`, `/accion`, `/chat` |
| **B3 — Plataforma** | **Cristian** | FastAPI y ensamblado, monitor programado, Supabase y sus migraciones, despliegue en Render, Twilio si sobrevive | `/caso/{id}`, `/monitor/nuevos`, `/alerta` |
| **UI/UX** | **Andrew** | **Todo el frontend, incluidas las decisiones de tecnología.** Las 4 pantallas, el grafo, el copy, y su propio despliegue | — |
| **Video** | **Jonatin**, desde las 22:00 | Guion, grabación, subtítulos, corte final | — |

**Jonatin lleva dos sombreros y eso tiene un costo real.** A las 22:00 deja B1 y se va al video. Por
eso el motor de señales tiene que estar congelado a las 22:00, y por eso **Cristian es su suplente**
para la revisión final de señales y fuentes de la madrugada.

**Andrew es dueño único del frontend, y eso incluye el stack.** El brief proponía React con Vite,
Tailwind y Cloudflare Pages; eso ya no aplica como decisión tomada. `web/` se entrega vacía. Ningún
backend entra ahí ni le sugiere librerías. Lo único que Andrew necesita del backend es el contrato
de la API y los fixtures, que ya están en el repo.

---

## 2. Mapa de propiedad del repo

La regla es simple: **nadie edita un archivo que no le pertenece.** Si necesitas un cambio en
territorio ajeno, lo pides por el chat del equipo. Cuesta un minuto y ahorra un conflicto.

| Ruta | Dueño | Nota |
|---|---|---|
| `api/lumen/croma/` | Jonatin | Cliente de Croma |
| `api/lumen/senales/` | Jonatin | Motor de las 8 señales |
| `api/lumen/routers/analisis.py` | Jonatin | |
| `api/lumen/ia/` | Freddy | `llm_client`, lector, prompts, narración, artefactos |
| `api/lumen/routers/ia.py` | Freddy | |
| `api/lumen/plataforma/` | Cristian | Supabase, monitor, alertas, cache |
| `api/lumen/routers/plataforma.py` | Cristian | |
| `api/lumen/main.py`, `api/lumen/config.py` | Cristian | Ya están escritos. Tocarlos debería ser raro |
| `supabase/migrations/` | **Cristian y nadie más** | Dos personas migrando a la vez rompen la base compartida |
| `scripts/`, `render.yaml` | Cristian | |
| `web/` | **Andrew y nadie más** | |
| `video/` | **Jonatin y nadie más** | |
| `docs/handoff/<TU-NOMBRE>.md` | Cada uno el suyo | |
| `PROYECTO.md`, `README.md`, `HANDOFF.md` | Jonatin | Coordinación |

### Quién es dueño de qué en el v3.1 (validación cruzada)

El parche v3.1 añade trabajo que no estaba repartido. Esto lo reparte, sin cambiar los roles:

| Lo que pide el v3.1 | Dueño | Quién lo consume | Dónde vive |
|---|---|---|---|
| Escribir las 9 frases de señal en lenguaje ciudadano | **Jonatin** (es su campo `regla_legible`) | Freddy, Andrew, Cristian | `docs/COPY-SENALES.md` |
| Que la narración y el lector hablen en ese mismo registro | **Freddy** | Andrew | `api/lumen/ia/` |
| Que las tarjetas y los botones usen ese texto sin reescribirlo | **Andrew** | — | `web/` |
| Que el WhatsApp use las mismas frases, máximo 5 líneas | **Cristian** | — | `api/lumen/plataforma/` |
| Storyboard nuevo del video, sin leyes y con protagonista | **Jonatin**, desde las 22:00 | — | `video/` |
| Que las leyes sigan íntegras donde sí suman | **Jonatin** (README) y **Freddy** (cuerpo de la carta) | Jurado | `README.md`, `/accion` |
| Reconocer a la mentora, si autoriza | **Jonatin** | — | `README.md` |
| Decidir qué pasa con Twilio ahora que WhatsApp es la tesis | **El equipo** | — | pendiente |

**La regla que hace que esto funcione:** las nueve frases se escriben **una sola vez**, en
[`COPY-SENALES.md`](COPY-SENALES.md). Nadie las reescribe en su capa. Si cuatro personas maquillan el
mismo texto, el veedor lee cuatro voces distintas en la misma pantalla y el video se nota cosido.

### El dueño del hito de las 23:00

El propio parche v3.1 lo señala como el único hueco del reloj: a las 22:00 Jonatin pasa a ser dueño
del video, y el hito crítico es a la hora siguiente.

> **Dueño del hito de las 23:00: `[PENDIENTE — designar por nombre, no a las 23:05]`**

Quien sea, su trabajo esa hora no es codear: es recorrer el flujo completo de punta a punta, decir
en voz alta si existe o no, y si no existe, **aplicar los hard-cuts sin pedir permiso**.

### Los tres archivos compartidos, y cómo no romperlos

Solo hay tres sitios donde dos personas pueden chocar de verdad:

**`api/lumen/contracts/`** — los modelos Pydantic de §5.5. Es el vocabulario común: si cambia, se
mueve el suelo de los cuatro a la vez.

> Para cambiarlo: **lo anuncias en el chat del equipo antes de pushear**, y lo escribes en tu
> archivo de handoff. Un cambio silencioso de esquema a las 23:00 cuesta dos horas de depuración a
> las 23:30. Añadir un campo opcional es barato; renombrar o quitar uno, no.

**`fixtures/`** — un JSON de ejemplo por endpoint. Lo escribe el dueño del endpoint. Andrew
construye contra esto sin esperar a nadie.

**`api/requirements.txt`** — para añadir una dependencia, **agrégala al final del archivo**, nunca en
medio. Así git resuelve casi todos los conflictos solo.

---

## 3. Protocolo de git

**Push directo a `main`. Sin ramas, sin PRs.** Los caminos no se solapan, y un code review a las
tres de la mañana es tiempo muerto.

```bash
git pull --rebase        # SIEMPRE antes de pushear
git add <rutas>          # NUNCA "git add ." — el repo es publico
git commit               # mensaje segun AGENTS.md: conventional + cuerpo largo
git push
```

**Cadencia: pusheas al menos cada 30 minutos.** Aunque esté a medias. Tres horas de trabajo sin
integrar es un conflicto garantizado y un riesgo de perderlo todo si se cae una máquina.

**Nunca `git add .`.** Es la forma número uno de commitear un `.env`. Hay un hook que lo bloquea
(`.githooks/pre-commit`), pero el hook es la segunda línea de defensa, no la primera.

**Mensajes de commit.** Conventional más cuerpo largo, punto por punto, en humano. El log tiene que
poder leerse como bitácora, porque el jurado evalúa el código y porque el siguiente agente lo lee.
Está prohibido el commit de una línea tipo "wip" o "fix".

```
feat(senales): S1 detecta empresas constituidas menos de un ano antes de ganar

- Cruzamos la fecha de registro de RUES contra la de adjudicacion de SECOP.
- La regla legible dice "la empresa se creo N dias antes de ganar", no la formula.
- Cada senal guarda la herramienta de Croma y la fecha de consulta como fuente.
- Si RUES no devuelve fecha de registro, no se dispara la senal: no inventamos.
```

**Conflicto en un archivo compartido:** gana quien pusheó primero. El segundo hace `pull --rebase`,
reaplica lo suyo y avisa en el chat si el resultado cambió algo del contrato.

---

## 4. Entorno y secretos

**Python: `venv` más `pip` más `requirements.txt`.** Nada de instalar `uv` o Poetry hoy.

```powershell
git clone <url> && cd HackathonCTW
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Mac/Linux: source .venv/bin/activate
pip install -r api/requirements.txt
Copy-Item .env.example .env           # y pega los valores del chat privado
git config core.hooksPath .githooks   # activa el hook anti-secretos
uvicorn lumen.main:app --reload --app-dir api
```

Verifica que arrancaste bien: `http://127.0.0.1:8000/health` y
`http://127.0.0.1:8000/health/croma`. El segundo hace una llamada real a Croma; si responde, tu
token funciona.

**Secretos.** El `.env` real circula por el chat privado del equipo y nunca entra al repo. En el
repo solo vive `.env.example`, con las llaves y sin los valores. Si alguna vez se te cuela un
secreto y ya lo pusheaste, **no lo tapes con otro commit**: avísalo en el chat y rotamos la
credencial. El repo es público y el historial también.

**Supabase: un solo proyecto cloud compartido.** Nadie levanta Docker. Y **Cristian es el único que
escribe migraciones**, versionadas en `supabase/migrations/`, nunca aplicadas a mano desde el
dashboard. Si necesitas una tabla o una columna, se la pides.

**Cuota de Croma: un token para cuatro personas más el monitor.** Es un recurso compartido y se
puede agotar. Nadie corre barridos masivos "a ver qué sale" sin avisar, y todo lo que se consulta se
cachea desde la primera hora.

---

## 5. El reloj, recalculado

El brief planificaba desde las 16:00. Son las 17:30 y el bloque de arranque no había ocurrido.
**Perdimos una hora y media, y se la come el bloque de arranque, no el de build.** El hito crítico
de las 23:00 no se mueve.

| Hora | Los cuatro | Jonatin · B1 + video | Freddy · B2 IA | Cristian · B3 Plataforma | Andrew · UI/UX |
|---|---|---|---|---|---|
| **17:30–18:15** | **Arranque.** Clonar, `.env`, venv, `/health` en verde. **Leer y aprobar el contrato de la API — es ahora o nunca** | Verificar las 3 capas de datos de §6 | `Cursor.models.list()` y fijar los dos modelos | Proyecto de Supabase + primera migración | Montar su stack |
| **18:15–19:00** | | Cliente Croma en marcha (el transporte ya está hecho) | `llm_client` blindado | **Hello world desplegado en Render** | Wireframes |
| **19:00–20:45** | | **Las 8 señales corriendo en CLI** | **Lector de justificaciones** | Esqueleto de endpoints + cache | Las 4 pantallas contra fixtures |
| **20:45** | | ✅ *El motor escupe señales con fuente sobre un caso real* | | | |
| **20:45–22:00** | | Grafo de actores | Resolución de entidades + narración | Monitor + Twilio si existe | Pantallas navegables |
| **21:30** | | | ✅ *El lector clasifica bien 3 documentos reales* | | |
| **22:00–23:00** | **Integración.** Todos contra la API real | 🎬 **Jonatin sale de B1 y arranca el guion del video** | | | ✅ *4 pantallas contra fixtures* |
| **23:00** | 🚨 **HITO CRÍTICO: flujo completo aunque sea feo.** Dato → señal → lectura IA → alerta. Si no existe, se aplican los hard-cuts. **No se extiende el horario** | | | | |
| **23:00–02:00** | | Validar a mano los 6 casos curados *(esto es también elegir el caso del video)* | Generador de artefactos | Precomputar y cachear los casos + dump JSON | Integrar contra la API real |
| **02:00** | 🧊 **Congelación de features. Lo que no exista, no existe** | | | | |
| **02:00–03:30** | | 🎬 **Primer corte del video, aunque esté feo. Respaldo grabado** | | | |
| **03:30–06:30** | | 🎬 Montaje | Revisión de salidas del LLM | **Despliegue verificado desde otro dispositivo** + revisión de señales (suplencia de B1) | Pulido de UI |
| **06:30–08:00** | README final con todas las fuentes declaradas | 🎬 Video final con subtítulos quemados | | | |
| **08:00–09:00** | **Subir al repo oficial. Verificar que abre desde otro dispositivo** | | | | ✅ **ENTREGADO** |

**Se entrega a las 08:00, no a las 08:55.** El deck dice que no se aceptan retrasos, y una subida
que falla a las 08:50 no tiene plan B.

### Los dos momentos en los que se corta, sin discusión

- **23:00.** Si no hay flujo completo, se aplica el orden de hard-cuts de `PROYECTO.md`. Se recorta
  alcance, no se estira el horario.
- **02:00.** Cero features nuevas. Solo lo que haga falta para grabar.

---

## 6. Cómo desbloquearse sin robarle tiempo a otro

**Regla de los 15 minutos.** Si llevas quince minutos parado esperando algo de otra persona, deja de
esperar: usa el fixture de `fixtures/` como si fuera la respuesta real y sigue con lo tuyo. Lo
anotas en tu handoff y lo cambias cuando el endpoint exista. Esto vale para los cuatro, y es la
razón de que los fixtures estén en el repo desde el primer commit.

**Si detectas una decisión técnica que nadie ha debatido**, no la tomes solo. Pregunta en el chat.
Eso lo dice `AGENTS.md` y aplica igual a las personas y a los agentes.

**Si abres una feature nueva**, dilo en el chat **y** en tu handoff: cómo se llama, para quién es y
qué queda fuera. Nadie debería descubrir una feature leyendo el diff.

---

## 7. Ritual de handoff

Cada uno mantiene `docs/handoff/<SU-NOMBRE>.md`. Se actualiza **al cerrar cada bloque del reloj**:
20:45, 22:00, 23:00, 02:00 y antes de irse a dormir si alguien duerme.

Cuatro preguntas, respuestas cortas:

1. Qué cambié
2. Qué quedó a medias y dónde exactamente
3. Qué no hay que tocar y por qué
4. Cómo se prueba lo mío en 30 segundos

El `HANDOFF.md` de la raíz lleva solo el estado global y apunta a los cuatro archivos. Así nadie
edita el mismo archivo a la vez y no hay conflictos.

---

## 8. Definición de "listo" por hito

No vale "ya casi". Un hito está listo cuando otro miembro del equipo puede verificarlo sin ayuda.

| Hito | Está listo cuando |
|---|---|
| Arranque (18:15) | Los cuatro tienen `/health/croma` en verde y el contrato de la API aprobado o corregido |
| Despliegue (19:00) | La URL de Render responde `/health` desde el celular de alguien, con datos móviles |
| Motor B1 (20:45) | Un comando de CLI recibe un NIT o una entidad y escupe señales, cada una con su regla legible, su dato y su fuente con fecha |
| Lector B2 (21:30) | Tres documentos reales de urgencia manifiesta clasificados, y cada punto del veredicto trae su cita textual |
| Hito crítico (23:00) | Se recorre dato → señal → lectura IA → alerta sin tocar nada a mano. Puede ser feo |
| Frontend (22:00) | Las 4 pantallas navegan entre sí contra fixtures, en el navegador de Andrew |
| Integración (02:00) | El frontend consume la API real desplegada, no `localhost` |
| Video (03:30) | Existe un archivo de video reproducible con el flujo completo. Feo cuenta |
| Entrega (08:00) | El repo público abre desde un dispositivo ajeno al equipo, el video está subido y el README declara todas las fuentes |
