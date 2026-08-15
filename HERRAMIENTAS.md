# HERRAMIENTAS.md — con qué contamos

Inventario de accesos verificados. **No es un menú para inventar stack.** Si algo no está aquí, no
lo tenemos; si está aquí y no lo usamos, es porque no hace falta.

Última verificación: sábado 15.ago.2026, 17:20.

---

## 1. Croma — fuente única de datos ✅ VERIFICADO EN VIVO

Lo más importante que hay que saber, y que el brief no decía:

> **Croma no es una API REST. Es un servidor MCP remoto** en `https://api.croma.run/mcp`, que habla
> JSON-RPC sobre HTTP y responde en formato SSE (`text/event-stream`), con autenticación por
> `Authorization: Bearer <token>`.

Y la buena noticia, comprobada con una llamada real:

> **El servidor es stateless.** No hace falta handshake ni `Mcp-Session-Id`. Un solo `POST` con
> `method: "tools/call"` devuelve el resultado. El cliente son unas 60 líneas de `httpx` más el
> parseo del SSE. **No necesitamos el SDK de MCP.**

Consecuencias que desbloquean el plan:

- El backend en Render **sí** puede llamar a Croma. No estamos atados a que corra dentro de Cursor.
- El cliente ya está escrito en [`api/lumen/croma/client.py`](api/lumen/croma/client.py) y probado
  contra el servidor real.

Prueba que se corrió: `rues_entities_by_name` con `name="Conalvias"` devolvió registros reales de
Cámara de Comercio con `registry_id`, `registration_status`, `registration_date` y demás.

### Herramientas de Croma que usan nuestras 8 señales

| Señal | Herramientas Croma |
|---|---|
| S1 · Empresa recién creada que gana | `rues_entity_by_nit` + `secop_contracts_by_provider` |
| S2 · Representante compartido | `rues_entity_by_nit` + `secop_processes_by_entity` |
| S3 · Sancionado que sigue contratando | `secop_sanctions_by_provider` + `procuraduria_disciplinary_records` + `contraloria_fiscal_records` |
| S4 · Contrato desproporcionado | `supersociedades_financial_statements` + `secop_contract` |
| S5 · Insolvente contratando | `sicaac_insolvency_cases` + `secop_contracts_by_provider` |
| S6 · Fraccionamiento | `secop_processes_by_entity` |
| S7/S8 · Concentración y directa recurrente | `secop_processes_by_entity` + `secop_contracts_by_provider` |
| S10 · Deudor moroso del Estado contratando | `contaduria_state_delinquent_debtors` + `secop_contracts_by_provider` |

Para la resolución de entidades: `rues_entities_by_name` → `rues_entity_by_nit`.
Para el fundamento normativo del derecho de petición: `legalize_laws_search` y
`ancp_cce_conceptos_search`.

**Cuota:** un solo token para 4 personas más el monitor. Es un recurso compartido y se puede
agotar. Todo lo que se consulte se cachea desde la primera hora. Ver la regla de cuota en
[`docs/PLAN.md`](docs/PLAN.md).

---

## 2. Cuentas y accesos

| Servicio | Estado | Quién lo tiene | Nota |
|---|---|---|---|
| **Croma** | ✅ Verificado con llamada real | Jonatin | Token por el chat privado. Va en `CROMA_API_KEY` |
| **API de Cursor (US$50)** | ✅ Disponible | — | Presupuesto duro. Dueño del consumo: **Freddy (B2)** |
| **Supabase** | ✅ Cuenta lista | — | Un proyecto cloud compartido. Dueño de migraciones: **Cristian (B3)** |
| **Cloudflare** | ✅ Cuenta lista | — | Para el frontend. **Andrew decide** si la usa |
| **GitHub** | ✅ Los 4 con cuenta | Repo en la cuenta de Jonatin | Público desde el primer commit |
| **Render** | ✅ Conectado por MCP | Jonatin | Dos workspaces: `gambito` y `migratory` |
| **Twilio** | ❌ **No tenemos cuenta** | — | Decisión aplazada. Hard-cut #3 |
| **HeyGen** | ❌ Descartado | — | Bonus menor, no compensa el tiempo |
| **Discord del evento** | Canal oficial | — | Ahí se anuncia el link del repositorio de entrega |

### Lo que falta confirmar hoy

- [ ] **El link del repositorio oficial de entrega.** El deck dice "PENDIENTE, se anuncia por el
      canal oficial". Que alguien se lo pregunte a un Ops Manager **antes de las 20:00**.
- [ ] Equipo registrado en la plataforma oficial y **Track 01 confirmado** en el registro.
- [ ] Qué hacemos con Twilio.

---

## 3. MCP disponibles en la máquina de Jonatin

Solo los que pueden servir. El resto está conectado pero es de otros proyectos.

| Servidor | Para qué serviría aquí |
|---|---|
| **croma** | La fuente de datos. El backend lo llama por HTTP, no por MCP de Cursor |
| **renderGambito / renderMigratory** | Crear el servicio, ver logs, disparar deploys y setear variables de entorno sin salir del editor. Con esto el deploy del backend no tiene fricción |
| **apify** | Scraping y `rag-web-browser`. Útil solo si hay que bajar un PDF de urgencia manifiesta que Croma no expone |
| **upstash** | Redis y QStash. QStash podría programar el cron del monitor si Render se queda corto. **No se usa salvo que Cristian lo pida** |
| Linear, Canva, ms365, google-workspace, n8n | Conectados, pero de otros proyectos. No entran aquí |

---

## 4. Herramientas locales verificadas

Comprobadas en la máquina de Jonatin. Los demás deberían verificar lo mismo antes de las 18:00.

| Herramienta | Versión | Nota |
|---|---|---|
| git | 2.49.0 | |
| Node | 22.16.0 | Para lo que Andrew decida |
| npm | 11.4.2 | `pnpm` **no** está instalado |
| Python | 3.13.5 | Es una versión nueva; si alguna dependencia pelea, se avisa en el chat |
| Docker | presente | No lo necesitamos: Supabase es cloud compartido |
| Supabase CLI | presente | Para las migraciones versionadas |
| ffmpeg | 8.1.1 | Para cortar y comprimir el video |

`uv` no está instalado. Decisión del equipo: **venv + pip + requirements.txt**, para que los cuatro
arranquen igual sin instalar nada previo.

---

## 5. Cursor: skills y agentes

Los cuatro trabajamos con el agente de Cursor y con el mismo [`AGENTS.md`](AGENTS.md) en la raíz del
repo, así que todos los agentes se comportan igual y leen los mismos archivos.

Skills que pueden aparecer y para qué:

- **webapp-testing** — probar el frontend con Playwright, sacar capturas y ver logs del navegador.
  Útil para el README y para el ensayo del video.
- **canvas** — artefactos analíticos. No lo necesitamos: el entregable es el producto, no un informe.
- **create-rule / create-skill** — solo si el equipo quiere fijar convenciones. No hoy.

### Reglas de presupuesto del SDK de Cursor (US$50, dueño: Freddy)

Estas seis son obligatorias y salen del brief §5.2:

1. **Un solo `llm_client`** con interfaz mínima. Todo el resto del código llama ahí. Si a las 22:00
   el consumo se dispara o la latencia mata el chat, se cambia de proveedor en 20 minutos.
2. **`cwd` apuntando a `./scratch`, nunca al repo.** Solo el documento que se está analizando. Es lo
   que más ahorra: un agente suelto sobre el repo lee archivos que nadie pidió.
3. **`settingSources: []`** (el default). Que no cargue configuración de entorno.
4. **Los 6 casos del catálogo van precomputados y cacheados.** Durante la grabación: **cero llamadas
   al LLM en vivo.**
5. **El SDK de Python es síncrono por defecto y FastAPI es async.** Usar `AsyncClient.launch_bridge`
   y no mezclar clientes sync y async en el mismo path.
6. **No hardcodear un ID de modelo a ciegas.** Correr `Cursor.models.list()` primero.

Higiene de errores, que ahorra una hora de depuración a ciegas: una excepción `CursorAgentError`
significa que el run **nunca arrancó** (auth, config o red). Un `result.status == "error"` significa
que **arrancó y falló**. Son bugs distintos. Y siempre disponer el agente con context manager, o se
filtran procesos.
