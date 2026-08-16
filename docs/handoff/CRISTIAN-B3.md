# Handoff — Cristian · B3 Plataforma

**Soy dueño de:** `api/lumen/plataforma/`, `api/lumen/routers/plataforma.py`, `api/lumen/main.py`,
`api/lumen/config.py`, `supabase/`, `scripts/`, `render.yaml`.
**Mis endpoints:** `GET /caso/{caso_id}`, `GET /monitor/nuevos`, `POST /alerta`.
**Mi hito:** 23:00 — el flujo completo corre de extremo a extremo, aunque sea feo. **Lo verifica
Jonatin**, que es el dueño del hito: él lo recorre y decide si existe o si se recorta.
**Soy el único que escribe migraciones de Supabase.** Si alguien necesita una tabla o una columna, me
la pide por el chat.
**Desde las 22:00 soy suplente de Jonatin** para la revisión final de señales y fuentes, porque él
se va al video.
**Desde las 22:14, WhatsApp/Twilio ya no es mío.** Se reasignó a Freddy por decisión del equipo —
detalle abajo y en `docs/handoff/FREDDY-B2.md`. Sigo siendo dueño de `/alerta` como puerta pública
del contrato; lo que cambia es que el envío real lo implementa el cliente de Freddy en
`api/lumen/whatsapp/`, no yo.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

---

## 22:14 — WhatsApp/Twilio se reasigna a Freddy

Después del timebox de las 20:45–21:45, WhatsApp pasa a ser propiedad de Freddy (B2), con libertad
de usar Twilio o Evolution API, el que responda mejor. Vive en `api/lumen/whatsapp/`, carpeta nueva
que no toca `api/lumen/plataforma/`. Yo mantengo `/alerta` como endpoint del contrato — la puerta
pública no cambia — pero el envío real ya no lo escribo yo, lo consumo del cliente de Freddy. Todo
lo demás de mi bloque (Supabase, monitor, cache, deploy) sigue igual. Detalle completo en
[`docs/handoff/FREDDY-B2.md`](FREDDY-B2.md).

## 19:20 — Qué me cambió el v3.1, y te toca a ti más que a nadie

El parche dice que no cambia el alcance ni los roles, y es cierto para tres de los cuatro. **A ti te
mueve el suelo**, porque el Parche 1 reencuadra WhatsApp:

> *"Por eso el canal es WhatsApp. No es un truco de distribución. Es la única interfaz que nuestro
> usuario real ya usa todos los días, sin instalar nada, sin crear cuenta, sin aprender un
> dashboard."*

El usuario primario dejó de ser "cualquier ciudadano" y pasó a ser **el veedor**, que suele ser una
persona mayor. Bajo esa premisa, WhatsApp deja de ser un canal de salida entre varios y pasa a ser
el argumento de por qué el producto es usable. Y el storyboard nuevo le da **11 de los 60 segundos**
al teléfono recibiendo la alerta.

**Y por eso Twilio te sube a prioridad 1. Decidido a las 19:30.**

El hard-cut #3 decía que si Twilio falla se muestra la plataforma. Con el v3.1 encima eso ya no es un
recorte menor: corta la pata que sostiene el pitch. Así que:

1. **Crea la cuenta de Twilio ya**, esta noche, mientras terminas el bloque de las 19:00. La
   verificación telefónica come tiempo y no quieres descubrirlo a las 20:50.
2. **A las 20:45 Twilio es lo primero que tocas**, antes del monitor. Timebox duro de 60 minutos.
3. **Corte a las 21:45.** Si a esa hora no llegó un mensaje real a un teléfono real, se corta y lo
   dices en voz alta. No lo estires "diez minutos más" tres veces.

**Detalle operativo que muerde:** en el sandbox de Twilio, el teléfono que recibe tiene que haberse
unido antes mandando `join <código>` al número de Twilio. **El teléfono que sale en el video tiene
que estar unido desde temprano**, no a las 03:00. Ese número va en `TWILIO_WHATSAPP_TO_DEMO`.

**Y si se corta, avísale a Jonatin de inmediato**, porque tiene que reescribir el bloque 0:15–0:26
del storyboard antes de empezar a grabar a las 22:00. Lo que no se hace nunca, pase lo que pase:
**mockear un WhatsApp falso.**

### El copy de la alerta ya no lo escribes tú

Los textos de las señales son fuente única y viven en
**[`docs/COPY-SENALES.md`](../COPY-SENALES.md)**. El WhatsApp usa exactamente esas frases, las
mismas que salen en la tarjeta de la ficha y en el video. Máximo 5 líneas, cero siglas, cifras en
pesos redondeados, y el disclaimer nuevo:

> *"Una señal no es prueba de irregularidad. Es un motivo para preguntar."*

En el mensaje se dice **"la carta para preguntarle a la alcaldía"**, nunca "derecho de petición".

---

## Lo primero, y es urgente

**Deja un hello world desplegado en Render antes de las 19:00.** El brief lo dejaba para las 03:30 y
eso es un error: un despliegue que se estrena de madrugada es un despliegue que falla de madrugada.
Con `render.yaml` en la raíz y el repo conectado debería costar quince minutos.

Está listo cuando la URL de Render responde `/health` **desde el celular de alguien, con datos
móviles.** No desde tu navegador con la caché caliente.

## Después

1. **Crear el proyecto de Supabase** y la primera migración. Un solo proyecto cloud compartido; nadie
   levanta Docker.
2. **Tablas mínimas** para que el flujo cierre: casos, señales, lecturas, suscripciones de WhatsApp,
   y una tabla de cache de respuestas de Croma (importante: el token es compartido y tiene cuota).
3. **El monitor.** Despierta, pide a Croma los contratos nuevos con causal de urgencia en los
   departamentos afectados desde el 11 de agosto, descarta lo que ya está en base, y arma casos.
4. **Twilio.** Ya no va aquí abajo: subió a prioridad 1 del bloque de las 20:45. Ver arriba.
5. **Precomputar y cachear los 6 casos del catálogo, y generar el dump JSON** versionado en
   `fixtures/casos_demo.json`. Con `LUMEN_USAR_DUMP_LOCAL=true` la API responde desde ahí sin tocar
   Supabase ni Croma. Es el respaldo de grabación: existe para que un corte de red a las 07:00 no
   cueste el hackathon.

## Dos detalles que muerden si se descubren tarde

**CORS.** Andrew despliega el frontend en un dominio que todavía no sabemos. En cuanto lo tenga, va
a `LUMEN_CORS_ORIGINS` en local y en las variables de entorno de Render. Si esto se descubre a las
02:00, se pierden treinta minutos justo en la integración.

**Zona horaria.** Render corre en UTC y nosotros razonamos en hora de Bogotá, que es UTC-5. Todas
las fechas que salgan a Croma (`from_date`, `to_date`) y todo lo que se guarde en base va explícito.
"Desde el 11 de agosto" tiene que significar lo mismo en las dos máquinas.

---

## Bitácora

### 00:50 — Supabase vivo, barrido real y la suite vuelve a correr en segundos

Change `cerrar-flujo-emergencia-b3`. Las cuatro preguntas del ritual:

**1. Qué cambié**

- **Supabase aplicado.** Migración `20260815205000_esquema_minimo` corrida contra el proyecto
  `hsjosillhpejxwlsucpl`. Las tres tablas existen (`casos`, `suscripciones_whatsapp`,
  `cache_croma`) con **RLS activo y sin políticas**, que es lo que impide que la llave `anon`
  pública lea los teléfonos de las veedoras.
- **El barrido del monitor ahora es real.** Recorre los 4 NITs que Jonatin verificó
  (`senales/entidades_emergencia`) con `secop_processes_by_entity`. Comprobado en vivo:
  213 / 95 / 83 / 36 procesos, exactamente los números de su commit.
- **Arreglado un bug mío que devolvía `[]` pareciendo sano:** el monitor buscaba
  `id`/`contrato_id`/`numero_contrato`, campos que Croma no devuelve nunca, así que descartaba
  todos los procesos en silencio. La llave real es `notice_uid`.
- **Se analiza por entidad, no por proceso.** Los procesos son pre-adjudicación y su `notice_uid`
  (`CO1.NTC.*`) **no** es el `contract_id` (`CO1.PCCNTR.*`) que espera `/analizar`: pasarlo
  devuelve `found:false` y un caso vacío. Además son 4 análisis en vez de 427, que es lo único que
  cabe en la cuota compartida. Tope configurable en `LUMEN_MONITOR_MAX_CASOS`.
- **La suite pasó de 123s a 0.23s.** El marcador `croma` estaba declarado en `pytest.ini` pero
  **no aplicado a ninguna prueba**: `test_senales_croma` solo tenía `skipif`, que no salta nada
  cuando la llave sí está. Le añadí `pytest.mark.croma` y `pytest.ini` los deselecciona por
  defecto. `pytest -m croma` sigue corriendo la integración real.
- `cache_croma` y `contrato_ya_conocido` ya no revientan sin Supabase: degradan avisando una vez.

**2. Qué quedó a medias y dónde exactamente**

- **Falta `SUPABASE_SERVICE_ROLE_KEY` en `.env`.** El MCP de Supabase no expone esa llave (solo las
  publicables), así que el backend Python todavía no puede escribir en la base. Sin eso,
  `/caso/{id}` y `/monitor/nuevos` siguen respondiendo `503`, y el barrido no puede guardar.
  Está en Settings → API del proyecto.
- **Render sigue sin existir.** No hay ningún servicio en la cuenta. Se decidió crearlo por
  Blueprint desde el dashboard, para que `render.yaml` siga siendo la única fuente de verdad.
- `pytest.ini` es archivo compartido: **hay que avisarlo en el chat** (lo pide `docs/PLAN.md`).

**3. Qué no hay que tocar**

- No toqué `api/lumen/senales/` ni `api/lumen/whatsapp/`: se consumen, no se editan. La única
  excepción es `api/tests/test_senales_croma.py`, donde añadí el marcador `croma` sin cambiar la
  lógica del `skipif` — está comentado en el archivo.
- El razonamiento de cada decisión está en `openspec/changes/cerrar-flujo-emergencia-b3/design.md`.

**4. Cómo se prueba en 30 segundos**

```bash
source .venv/bin/activate
python -m pytest -q        # 39 passed, 3 deselected, <1s
python -m pytest -m croma  # integración real contra Croma (lenta, gasta cuota)
```

### 21:50 — Implementados los tres endpoints, Supabase, cache y keep-alive

Change de OpenSpec `plataforma-b3-flujo-completo` (`openspec/changes/plataforma-b3-flujo-completo/`)
aplicado. Resumen de las cuatro preguntas del ritual:

> **Nota al pushear (22:20):** todo lo de abajo se escribió antes de enterarme de la reasignación
> de WhatsApp de las 22:14 (ver arriba). `whatsapp.py` **ya no es "el" envío de WhatsApp del
> proyecto** — es un respaldo funcional para que `/alerta` no se quede mudo mientras el cliente
> real de Freddy en `api/lumen/whatsapp/` no exista. El punto de enganche para reemplazarlo es una
> sola línea de import en `api/lumen/routers/plataforma.py`, comentada ahí mismo. Hablado con
> Freddy: su reasignación queda firme.

**1. Qué cambié**

- Los tres endpoints de `api/lumen/routers/plataforma.py` dejaron de ser `501`:
  `GET /caso/{caso_id}`, `GET /monitor/nuevos`, `POST /alerta` ya tienen lógica real.
- Paquete nuevo `api/lumen/plataforma/`: `supabase_client.py`, `casos.py`, `cache_croma.py`,
  `monitor.py`, `whatsapp.py` (envío de **respaldo**, ver nota arriba — el dueño real de WhatsApp
  es Freddy desde las 22:14), `suscripciones.py`, `dump_local.py`, `tiempo.py`.
- Primera migración de Supabase: `supabase/migrations/20260815205000_esquema_minimo.sql` — tres
  tablas (`casos`, `suscripciones_whatsapp`, `cache_croma`), no cinco: `senales`/`lecturas` viven
  dentro del `jsonb` de `casos` (ver Decisión 3 del `design.md` del change).
- `.github/workflows/keep-alive.yml`: ping a `/health` cada 10 minutos para que Render free tier
  nunca duerma. **No corre hasta que esto se pushee a `main`** — GitHub Actions no lee workflows
  locales.
- `render.yaml`: bloque comentado con la alternativa nativa (`type: cron`), más `LUMEN_FRONTEND_URL`
  como variable nueva (para el enlace del WhatsApp, no para CORS).
- `config.py` y `.env.example`: campo nuevo `LUMEN_FRONTEND_URL` (opcional, vacío por defecto).
- `api/requirements.txt`: añadido `twilio==9.11.0` al final del archivo.
- `fixtures/casos_demo.json`: existe, pero es un **placeholder** (copia de `fixtures/caso.json`),
  no los 6 casos reales.
- `scripts/precomputar_casos_demo.py`: script para generar el dump real, con un diccionario
  `CATALOGO_CURADO` a la espera de que alguien (yo, con Jonatin) ponga los NIT de los 6 casos.
- `api/tests/test_plataforma.py`: 6 pruebas nuevas. Suite completa: **20/20 pasan**.

**2. Qué quedó a medias y dónde exactamente**

- **Nada de esto se probó contra servicios reales** — este entorno no tenía `.env`, ni cuenta de
  Twilio, ni proyecto de Supabase, ni acceso físico a un teléfono. Todo lo anterior corre sin red
  usando `LUMEN_USAR_DUMP_LOCAL=true` y pruebas automatizadas.
- El proyecto de Supabase **no existe todavía**: hay que crearlo y aplicar la migración con la
  CLI (`supabase link` + `supabase db push` o equivalente).
- Twilio **no está probado con un mensaje real**. El timebox del `PLAN.md` (corte 21:45) ya pasó
  la hora del reloj mientras yo trabajaba — corre esto ya, con prioridad, en cuanto tengas `.env`.
- `monitor.py` tiene dos `TODO(Jonatin/B1)`: el nombre exacto de la herramienta de Croma para un
  barrido amplio por departamento (no está en `HERRAMIENTAS.md`, que solo documenta herramientas
  puntuales por entidad/proveedor) y la lista `DEPARTAMENTOS_AFECTADOS` (vacía a propósito, para
  no inventar departamentos sin fuente). Sin esos dos datos, `/monitor/nuevos` no va a encontrar
  nada real, aunque no se cae.
- `/monitor/nuevos` también depende de que Jonatin implemente `/analizar` (sigue en `501`): mientras
  tanto, cada contrato que el monitor encuentre se salta con una advertencia en el log, no con un
  error. Es el comportamiento esperado, no un bug.
- `scripts/precomputar_casos_demo.py` no se pudo correr: falta el mapeo NIT/entidad_id de los 6
  casos del catálogo curado (brief §4.5.4), que es la validación a mano de Jonatin.

**3. Qué no hay que tocar**

- Todo lo de arriba sigue siendo mío (`api/lumen/plataforma/`, `routers/plataforma.py`,
  `supabase/migrations/`). Si algo de esto necesita cambiar, pídelo por el chat como siempre.
- No toqué `api/lumen/senales/`, `api/lumen/ia/`, `api/lumen/croma/client.py`, ni
  `routers/analisis.py` o `routers/ia.py` — siguen intactos, tal como los dejaron Jonatin y Freddy.
- `openspec/changes/plataforma-b3-flujo-completo/` documenta el porqué de cada decisión (por
  ejemplo, por qué 3 tablas y no 5, por qué GitHub Actions y no un cron nativo de Render).

**4. Cómo se prueba en 30 segundos**

```bash
source .venv/bin/activate   # o crea uno: python3 -m venv .venv
python -m pytest -q         # 20 passed
```

Sin `.env` y sin red. Para ver el flujo de casos "a mano": `LUMEN_USAR_DUMP_LOCAL=true uvicorn
lumen.main:app --reload --app-dir api` y luego `GET /caso/caso-ejemplo-0001`.

### 17:30 — Punto de partida

`api/lumen/main.py` y `api/lumen/config.py` ya están escritos y funcionando: la app arranca, tiene
CORS configurable por entorno, `/health`, `/health/croma` y los nueve endpoints declarados. Mis tres
endpoints están en `api/lumen/routers/plataforma.py` devolviendo `501`.

Nada de Supabase existe todavía. Nada está desplegado todavía.
