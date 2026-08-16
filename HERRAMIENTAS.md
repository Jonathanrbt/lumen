# HERRAMIENTAS.md — con qué contamos

Inventario de accesos verificados. **No es un menú para inventar stack.** Si algo no está aquí, no
lo tenemos; si está aquí y no lo usamos, es porque no hace falta.

Última verificación: sábado 15.ago.2026, 22:20.

---

## 1. Croma — fuente única de datos ✅ VERIFICADO EN VIVO

**Lumen consulta Croma por la API HTTP**, no por MCP.

`POST https://api.croma.run/co/…/v1` con JSON y `Authorization: Bearer $CROMA_API_KEY`.
Respuesta en `{ "data": … }`. `found: false` es una respuesta definitiva, no un error.
Overview: https://docs.usecroma.com/api-reference/overview
Índice: https://docs.usecroma.com/llms.txt

El cliente está en [`api/lumen/croma/client.py`](api/lumen/croma/client.py):
`croma.consultar("rues_entities_by_name", {"name": "Conalvias"})`. La URL no va en
`.env` ni en Render: está fija en el código.

El MCP de Cursor (`user-croma` en la máquina de Jonatin) **no lo usa el producto**.
Si lo usás para humear, es la misma key y la misma cuota. No hace falta para el motor.

### Obligatorio: leer la guía antes de armar una consulta

**No inventar parámetros.** Antes de un `consultar`:

1. Abrir la **guía de esa fuente** (tabla de abajo).
2. Copiar el contrato: sujeto (`document_number`, `contract_id`, `notice_uid`, `name`),
   opcionales (`from_date`, `to_date`, `page`), listas capadas.
3. Llamar `CromaClient.consultar(fuente, cuerpo)` con el alias de la tabla. El cliente
   traduce al `POST /co/…/v1`.
4. RUES por NIT: la API pide `document_number`. Si pasás `nit`, el cliente lo mapea.
5. Cachear. Token compartido entre cuatro personas + monitor.

Fuera del corte (no leer, no consultar): RUNT, SIMIT, cédula, policía, salud, México, Perú.

### Guías y rutas HTTP del corte

| Fuente | Guía | Alias `consultar` · ruta |
|---|---|---|
| RUES | https://docs.usecroma.com/guides/colombia/rues | `rues_entities_by_name` → `/co/rues/entities-by-name/v1` · `rues_entity_by_nit` → `/co/rues/entity-by-nit/v1` |
| SECOP | https://docs.usecroma.com/guides/colombia/secop | `secop_process` → `/co/secop/process/v1` · `secop_contracts_by_provider` → `/co/secop/contracts-by-provider/v1` · `secop_processes_by_entity` → `/co/secop/processes-by-entity/v1` · `secop_contract` → `/co/secop/contract/v1` · `secop_sanctions_by_provider` → `/co/secop/sanctions-by-provider/v1` |
| Supersociedades | https://docs.usecroma.com/guides/colombia/supersociedades | `supersociedades_financial_statements` → `/co/supersociedades/financial-statements/v1` |
| SICAAC | https://docs.usecroma.com/guides/colombia/sicaac | `sicaac_insolvency_cases` → `/co/sicaac/insolvency-cases/v1` |
| Contaduría | https://docs.usecroma.com/guides/colombia/contaduria | `contaduria_state_delinquent_debtors` → `/co/contaduria/state-delinquent-debtors/v1` |
| Procuraduría | https://docs.usecroma.com/guides/colombia/procuraduria | `procuraduria_disciplinary_records` → `/co/procuraduria/disciplinary-records/v1` |
| Contraloría | https://docs.usecroma.com/guides/colombia/contraloria | `contraloria_fiscal_records` → `/co/contraloria/fiscal-records/v1` |
| Legalize | https://docs.usecroma.com/guides/colombia/legalize | `legalize_laws_search` → `/co/legalize/laws/v1` · `legalize_law` → `/co/legalize/law/v1` |
| ANCP-CCE | https://docs.usecroma.com/guides/colombia/ancp-cce | `ancp_cce_conceptos_search` → `/co/ancp-cce/conceptos-search/v1` · `ancp_cce_concepto` → `/co/ancp-cce/concepto/v1` |

SECOP — cuerpo típico:

- process: `notice_uid`
- contracts-by-provider: `document_number`; opcional `entity_nit`, `from_date`, `to_date`, `page`
- processes-by-entity: `document_number`; opcional `from_date`, `to_date`, `page`
- contract: `contract_id` (trae `additions[]`, garantías, plan)
- sanctions-by-provider: `document_number`

No usar `web_search` / `research` de Croma para leer docs. Fetch a docs.usecroma.com.

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

## 2.bis El MCP que publicamos nosotros

No confundir con los de la sección 3: esos los consumimos, este lo **servimos**.

`lumen-api` expone un servidor MCP en `/mcp` (transporte streamable HTTP) para que un agente
externo —Claude, Cursor— busque empresas y contratos con las mismas herramientas que usa la web.
Código en [`api/lumen/mcp/`](api/lumen/mcp/), dueño: Cristian (B3).

**Cómo conectarse:**

| | |
|---|---|
| URL | `https://<servicio>.onrender.com/mcp` |
| Cabecera | `Authorization: Bearer $LUMEN_MCP_TOKEN` |
| Apagarlo | `LUMEN_MCP_HABILITADO=false` en el dashboard de Render (sin redesplegar) |

Sin token → `401`. Sin `LUMEN_MCP_TOKEN` configurado en el servidor → `503`, **no queda abierto**.

**Las nueve herramientas:**

| Herramienta | Qué hace | Coste |
|---|---|---|
| `resolver_entidad` | Nombre libre → candidatos con NIT | Barata |
| `analizar_entidad` | Las 8 señales sobre un NIT, entidad o contrato | **80-100 s**, mucha cuota |
| `ver_red_de_actores` | Subgrafo de quién está detrás de quién | Cuota |
| `obtener_caso` | Un caso ya calculado, por id | Sin cuota |
| `leer_justificacion_urgencia` | Veredicto sobre el PDF de urgencia manifiesta | LLM |
| `generar_artefacto` | Derecho de petición, evidencia, veeduría, guía | LLM |
| `contratos_nuevos_del_monitor` | Lo que encontró el monitor | Muy cara |
| `enviar_alerta` | **Manda un mensaje real a una persona** | Efecto externo |
| `estado_del_sistema` | Qué piezas están encendidas | Gratis |

`/chat` **no** se expone como herramienta: el agente conectado es el conversador. Envolverlo sería
un LLM dentro de otro, narrando dos veces y pagando el modelo dos veces.

> **Las reglas del asistente viven en dos sitios y se cambian juntas.**
> [`api/lumen/ia/chat.py`](api/lumen/ia/chat.py) las obedece para la web;
> [`api/lumen/mcp/instrucciones.py`](api/lumen/mcp/instrucciones.py) se las entrega a los agentes
> externos. No se importan entre sí —son dos registros: uno describe lo que hace ese módulo, el
> otro le da órdenes a otro agente— así que si tocas las seis reglas en uno, tócalas en el otro.
> `api/tests/test_mcp.py` comprueba que estén las seis, pero no puede comprobar que digan lo mismo.

---

## 3. MCP disponibles en la máquina de Jonatin

Solo los que pueden servir. El resto está conectado pero es de otros proyectos.

| Servidor | Para qué serviría aquí |
|---|---|
| **croma** | No entra al producto. Solo humear en el editor de Jonatin (misma cuota) |
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
