# Handoff — Jonatin · B1 Datos (+ video desde las 22:00)

**Soy dueño de:** `api/lumen/croma/`, `api/lumen/senales/`, `api/lumen/routers/analisis.py`,
`video/`, y la coordinación (`PROYECTO.md`, `README.md`, `HANDOFF.md`).
**Mis endpoints:** `POST /analizar`, `GET /red/{nit}`.
**Mis hitos:** 20:45 el motor escupe señales con fuente sobre un caso real · 22:00 congelo B1 y me
voy al video · **23:00 soy el dueño del hito crítico** · 03:30 primer corte grabado · 08:00 video
final subido.
**Mi suplente después de las 22:00:** Cristian, para la revisión final de señales y fuentes.

## Soy el dueño del hito de las 23:00 — tres reglas, decidido a las 19:30

Encaja porque a esa hora mi bloque es validar a mano los 6 casos curados, y recorrer el flujo y
elegir el caso que sale grabado son la misma tarea. Pero el riesgo de que me trague la noche es real,
así que:

1. **No toco el teclado del backend.** Recorro el flujo como usuario y miro. Si vuelvo a codear a las
   23:00, no vuelvo al video hasta la una.
2. **Digo en voz alta si el flujo existe o no.** Sin matices, sin "ya casi". Existe cuando va de dato
   a señal a lectura de IA a alerta sin tocar nada a mano. Feo cuenta.
3. **Si no existe, aplico el orden de hard-cuts sin abrir debate.** Se recorta alcance, no se
   extiende el horario.

**A las 23:20 vuelvo al video, pase lo que pase.**

Y hay una dependencia que me llega esa noche: **si Twilio se corta a las 21:45, tengo que reescribir
el bloque 0:15–0:26 del storyboard** antes de empezar a grabar. Cristian me avisa en cuanto lo sepa.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

---

## 19:20 — Qué me cambió el v3.1

El parche no toca mis endpoints ni mi cronograma, pero me cambia **qué texto tiene que salir del
motor** y **cómo se cuenta el video**. Dos cosas nuevas, ninguna trivial.

### 1. Soy dueño de las nueve frases de señal

El Parche 3 traduce las 8 señales a lenguaje ciudadano. Esos textos salen en el campo
`regla_legible` de cada `Senal`, que es mío, así que **los escribo yo** — pero los leen tres
personas más: Freddy los usa de referencia para narrar, Andrew los pinta en las tarjetas y Cristian
los mete en el WhatsApp.

Por eso viven en un solo sitio: **[`docs/COPY-SENALES.md`](../COPY-SENALES.md)**. Si me invento una
variante al escribir la señal S4, el veedor lee dos voces distintas en la misma pantalla.

Las reglas duras: máximo 20 palabras, sujeto-verbo-cifra, cero siglas sueltas en texto visible
("RUES", "SECOP" y "BDME" van solo en la línea de fuente), y la cifra en pesos redondeados. El test
es literal: **si mi mamá no lo entiende, se reescribe.**

Ojo con una tentación: la plantilla no puede quedar genérica. "Esta empresa se creó hace 2 meses y
ya ganó un contrato de $X" necesita que yo calcule los meses y formatee los pesos, no que imprima
`dias_transcurridos=41`. El dato crudo va en `datos_usados`, que es para auditar; la frase es para
leer.

### 2. El video cambió de guion entero

Nada de leyes, nada de cifras en dólares, y hay protagonista. El storyboard v3.1 completo está en
[`docs/brief-final-claude.md`](../brief-final-claude.md) §8.

Lo que tengo que interiorizar antes de las 22:00:

- **Abre con una pregunta, no con una cifra.** "Llega la plata para reconstruir." → "¿Quién está
  mirando?" La cifra de US$450 millones impresiona a un economista; la pregunta le llega a
  cualquiera.
- **Hay una persona.** "Ella es veedora de su municipio." Un producto con usuario se recuerda; una
  plataforma no.
- **Se dice "la carta para preguntarle a la alcaldía"**, no "derecho de petición".
- **Se muestra el hallazgo, no se explica la norma.** "El documento que justifica la urgencia no
  menciona ningún daño del terremoto" en vez de citar el artículo 46.
- Las leyes no desaparecen: se mudan al README y a las respuestas al jurado.
- Test antes de grabar: **si mi mamá no entiende los primeros siete segundos, se regraba.**

Se conservan las reglas de producción del v3: grabar a tamaño de teléfono real y hacer zoom, una
tipografía, un color de acento, subtítulos quemados, y respaldo grabado apenas exista el flujo.

---

## Lo que hice antes (17:30) — el andamio

Monté el repositorio entero: git, protección de secretos, los documentos que `AGENTS.md` exige, el
contrato de la API con sus fixtures, el esqueleto de FastAPI y el cliente de Croma.

**El hallazgo importante (17:20):** Croma se podía hablar por MCP; el transporte viejo era JSON-RPC.

**Decisión (22:20, Jonatin):** el producto consulta **solo la API HTTP**. Cliente reescrito en
`api/lumen/croma/client.py` (`consultar`). Guías en [`HERRAMIENTAS.md`](../../HERRAMIENTAS.md) §1.

**Cómo se prueba lo mío en 30 segundos:** `GET /health/croma` hace una llamada real a RUES.

**Qué no hay que tocar:** el cliente de Croma mientras yo esté dentro. Fuente nueva del corte:
agregar la ruta en `RUTAS` de `client.py` y la guía en `HERRAMIENTAS.md`.

---

## Pendientes míos, en orden

1. Completar NITs del catálogo curado que **aún no aparecen en Croma** (Metro SAS, UNGRD, Mocoa,
   Providencia, Centros Poblados). No inventar: si RUES/SECOP no lo trae, queda vacío.
2. Video (guion / grabación). El motor ya no está en 501.

---

## 23:30 — Motor B1 vivo contra Croma HTTP

**1. Qué cambié**

- `POST /analizar` y `GET /red/{nit}` dejan de ser 501. Paquete `api/lumen/senales/` (motor, copy
  de COPY-SENALES, S1–S8 y S10, grafo, nivel stub).
- Croma se llama **directo** (`CromaClient.consultar`). No usamos `cache_croma` de Cristian hasta
  que exista Supabase.
- `nivel_atencion` por conteo de señales (0 bajo, 1 medio, ≥2 alto). Sin lectura de Freddy.
- CLI: `python -m lumen.senales --nit 79372917`.
- `tzdata` al final de `api/requirements.txt`: en Windows, sin eso no arranca la app.

**2. Forma real de Croma (iteración 0)**

- Contratos: `contracts[]` con `contract_id`, `provider_document`, `entity_nit`, `value`,
  `sign_date`, `modality`, `object`, `legal_rep_name`.
- Procesos de entidad: `processes[]` con `notice_uid`, `base_price`, `modality`, `published_date`.
- RUES por NIT: `{ found, entity.registration_date, related_parties[], financials[] }`.

**3. Sujetos verificados en vivo (no mocks)**

| Quién | NIT / doc | Qué salió |
|---|---|---|
| Proveedor de prueba (persona) | `79372917` | 6 contratos SECOP reales. `/analizar` y `/red` 200. |
| Entidades de Bogotá (NIT compartido) | `899999061` | 500 procesos; **333 desde 2026-08-11** (capa 1: no está vacío). |
| Odinsa S.A. | `800169499` | RUES sí; **0 contratos** SECOP. |
| Conalvías liquidación | `890318278` | RUES sí; **0 contratos**. |
| Odinsa Aeropuertos | `901645491` | RUES sí; **0 contratos**. |
| NIT que se creía UNGRD | `900144920` | **0 procesos**. No usar. |

**Catálogo curado — para Cristian (`CATALOGO_CURADO`). No edité su script.**

| Caso | nit / entidad_id | Estado |
|---|---|---|
| Metro de Bogotá | *(pendiente)* | No aparece como Empresa Metro en RUES. No inventar. |
| Ruta del Sol / Odinsa | `800169499` | RUES ok; SECOP 0. |
| Centros Poblados | *(pendiente)* | El nombre no da la empresa del escándalo. |
| UNGRD 2024 | *(pendiente)* | `900144920` no sirve. |
| Mocoa 2017 | *(pendiente)* | Sin NIT verificado. |
| Providencia post-Iota | *(pendiente)* | Sin NIT verificado. |
| Smoke técnico | `79372917` o entidad `899999061` | Para el hito, no son el catálogo reputacional. |

**4. Monitor (Cristian: no toqué `monitor.py`)**

No existe barrido por departamento. Recorre entidades con `secop_processes_by_entity`:

- `899999061` (Bogotá), `from_date=2026-08-11`.
- Luego `POST /analizar` con `contrato_id` (`CO1.PCCNTR.*`) o `nit` del proveedor.

**5. Cómo se prueba en 30 segundos**

```
GET /health/croma
POST /analizar  {"nit":"79372917"}
GET /red/79372917
python -m pytest api/tests/test_senales.py -q
python -m pytest api/tests/test_senales_croma.py -q
```

**6. Qué no hay que tocar**

Plataforma de Cristian, `ia/` de Freddy, `web/` de Andrew, `contracts/` (no cambió).

---

## Notas para el video (se llenan desde las 22:00)

- Caso elegido para el bloque de 0:26–0:38:
- Documento de urgencia que se muestra:
- Teléfono que recibe la alerta:
- Quién es "ella", la veedora del guion (voz en off o texto):
