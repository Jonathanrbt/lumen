# LUMEN — Brief v3 (final)

**Hackathon CTW 2026 · Track 01: Tecnología para la Transparencia**
**Equipo:** 4 personas · **Ventana real restante:** ~17 h (arranque 16:00 sábado · deadline domingo 16.ago 09:00)
**Versión:** v3 — 15 de agosto de 2026 · consolida el v1 "La Red" y el v2 "Lumen"
**Nombre:** Lumen

---

## 0. Qué es este documento

El v1 ("La Red") tenía el producto completo pero sin foco: toda la contratación pública de Colombia, pitch de 5 minutos que ya no existe. El v2 acertó el corte (sismo, push, IA al centro, video de 60 s) pero amputó la mitad del producto y se quedó con una duda de datos que ya está resuelta.

Este v3 **cierra las dos cosas**: mantiene el corte del v2 y recupera lo que el v1 tenía bien.

### Cambios frente al v2

| # | Cambio | Razón |
|---|---|---|
| 1 | **Un motor, dos modos.** Modo Emergencia (push, sismo) + Modo Vigilancia (pull, contratación ordinaria) | El sismo es la ventana abierta hoy; la fuga de plata pública es el problema de fondo. El v2 ya lo decía en su §12 ("modo latente") pero enterrado en el roadmap. Es producto, no visión |
| 2 | **Croma queda cerrado como fuente única.** Se elimina el condicional "si el reglamento lo permite / si no, Socrata" | Croma ya está confirmado, con acceso funcionando, y trae SECOP limpio + 6 fuentes más. El cruce multi-fuente **es** el diferencial técnico |
| 3 | Se recupera el **agente conversacional** con resolución de entidades y catálogo curado | Es lo que hace que la herramienta sirva los otros 364 días y en los 1.100 municipios que el push no vigila |
| 4 | El motor sube de **5 a 8 señales** | Con Croma, S4, S5 y S10 son una llamada más cada una. Alto retorno por bajo costo |
| 5 | Se recupera la **capa de acción completa** (4 artefactos, no solo el derecho de petición) | Responde "¿y ahora qué hago?", que era la brecha #2 del v1 |
| 6 | Se recuperan la **tabla competitiva internacional** y las **4 brechas** | El v2 solo defendía una brecha. El jurado pregunta por las otras tres |
| 7 | Cronograma recalculado desde las 16:00 | El v2 planificaba desde las 14:00 y ya íbamos tarde en su propio reloj |

### Reformulación del cambio #3 del v2 (importante, era una contradicción)

El v2 decía: *"no es un chatbot que responde, es un vigilante que avisa; chatbot que analiza contratos está saturado en esta sala"*. Sigue siendo cierto **como jerarquía**, no como prohibición:

> El diferenciador nunca fue *no tener chat*. Fue **no depender del chat**. El hook es el push. El agente no es la puerta de entrada del producto — es la puerta de entrada del ciudadano cuando ya sabe qué preguntar.

### Lo que NO se reabre

Nombre (Lumen), track (01), el push como hook, la IA como núcleo, el video de 60 s como especificación del producto, y **todo el stack de §5** (Croma, FastAPI, Cursor SDK, React+Vite, Supabase, Twilio, Render, Cloudflare Pages, monorepo).

### Dónde está cada cosa para empezar a codear

| Necesito… | Sección |
|---|---|
| El recorrido paso a paso de la app, con dueño por paso | **§4.6** |
| Qué tecnología usamos y por qué | **§5** |
| Las reglas del repo (monorepo, secretos, README) | **§5.1** |
| Cómo no quemar los US$50 de la API de Cursor | **§5.2** |
| Endpoints, modelo de datos y esquemas | **§5.5** |
| Quién hace qué y qué endpoints le pertenecen | **§10** |
| El reloj hora por hora y por persona | **§11** |

---

## 1. Resumen ejecutivo

**Lumen** es un sistema de vigilancia ciudadana sobre la plata pública, encendido hoy sobre la reconstrucción del terremoto del 10 de agosto de 2026.

**Modo Emergencia (push — el hook).** Corre solo. Revisa los contratos nuevos que entran por el régimen excepcional de emergencia, lee las justificaciones que la ley exige, detecta patrones que merecen revisión, y **le avisa por WhatsApp** al veedor, al periodista local o al líder comunal del municipio afectado — con la evidencia y con un derecho de petición listo para enviar.

**Modo Vigilancia (pull — el que lo hace durar).** El mismo motor, expuesto como agente conversacional. Cualquier persona escribe en lenguaje natural —"¿la alcaldía de mi pueblo tiene algo raro?", el nombre de una empresa que vio en una valla— y recibe la red de actores detrás del contrato, las señales con su evidencia, y el artefacto para actuar. Sin pedir un NIT. Sin saber qué es SECOP.

**Pitch de una frase:**
> "El control de la plata de la reconstrucción es posterior. Nosotros lo hacemos hoy."

**La frase que justifica los dos modos:**
> "El sismo es la ventana que está abierta hoy. La fuga de plata pública está abierta todos los días."

**Frase de seguridad (repetir siempre, y decirla en el video):**
> "No acusamos: priorizamos dónde mirar y entregamos evidencia verificable para preguntar mejor."

---

## 2. El problema

### 2.1 La urgencia: la ventana que se abrió hace cinco días

El 11 de agosto, el Decreto 1171 declaró desastre nacional. Con eso:

- Se activó el **artículo 46 de la Ley 1523**, que permite adjudicar demolición, retiro de escombros y reconstrucción **de forma directa, sin licitación**.
- El manejo de recursos quedó en una subcuenta temporal del Fondo Nacional de Gestión del Riesgo llamada **SISMO 2026**.
- La declaratoria tiene vigencia inicial de hasta **12 meses, prorrogable**.
- El Gobierno gestiona un crédito contingente de hasta **US$450 millones con el Banco Mundial**; EE. UU. elevó su asistencia a **US$26,5 millones**.
- Ya hay urgencias manifiestas declaradas (la Rama Judicial, Acuerdo PCSJA26-12569, por dos meses).
- El control de la Contraloría sobre esa contratación es, según el propio marco, **posterior**.

Escala del daño (UNGRD, corte 14 de agosto): 15 departamentos, 448 municipios, 57.516 familias y 145.601 personas afectadas; 288 fallecidos; 80.744 viviendas averiadas y 12.504 destruidas; 2.595 centros educativos afectados.

**El hueco:** miles de millones se van a mover durante 12 meses por contratación directa, en 448 municipios, muchos de ellos sin capacidad institucional ni prensa local. Cuando el control llegue, la plata ya se gastó. El antecedente inmediato es el escándalo de la UNGRD de 2024: la propia agencia de gestión del riesgo, convertida en caso de corrupción.

### 2.2 El fondo: por qué esto no es un problema del sismo

La contratación de emergencia es una ventana **más ancha** sobre un hueco que está abierto siempre:

- Los datos de contratación pública **existen y son públicos** (SECOP I y II, millones de registros), pero están dispersos, en formatos técnicos, y exigen saber de contratación estatal para interpretarse.
- Un ciudadano, una veeduría o una junta comunal que quiere vigilar una obra **no sabe por dónde empezar**: no tiene el NIT del contratista, no conoce los campos de SECOP, no sabe qué es una adición ni qué documento pedir.
- El costo de entrada al control ciudadano es tan alto que la mayoría abandona antes de formular la primera pregunta.
- Y la consecuencia encadena: sin plata no hay recursos, sin recursos no hay respuesta a la próxima emergencia ni movilidad social. La fuga no es un problema entre otros — es el que apaga a los demás.

**El dolor en dos frases, una por modo:**
> *Emergencia:* "Mi municipio va a recibir plata para reconstruirse y no tengo forma de saber si se está gastando bien, hasta que sea tarde."
> *Vigilancia:* "Sé que el dinero público debería poder vigilarse, pero no sé por dónde empezar ni cómo distinguir un contrato normal de uno que merece revisión."

---

## 3. La IA como núcleo (esto es lo que gana los 25 pts)

Cuatro funciones que **no se pueden hacer con reglas deterministas**. Esta sección es la que hay que defender.

### 3.1 Lector de justificaciones de urgencia manifiesta ← *la feature estrella*

La norma exige que toda contratación bajo urgencia manifiesta tenga **relación directa y verificable con los hechos que dieron lugar a la emergencia**, precedida de diagnósticos técnicos. Esa justificación es un **PDF en texto libre**.

El LLM lee ese documento y evalúa:

- ¿La justificación menciona daños concretos, ubicados y verificables, o es lenguaje genérico de plantilla?
- ¿El objeto contractual guarda relación causal con el daño descrito? (¿Se está comprando algo que estaba en el plan de compras de junio y se coló por la ventana de emergencia?)
- ¿Se invocan los diagnósticos técnicos que la norma exige, o se afirman sin soporte?
- ¿La fecha del hecho justificante es posterior al 10 de agosto?

**Salida:** un veredicto de tres niveles (justificación sólida / genérica / sin relación aparente con el sismo), con la cita textual del documento que sustenta cada punto.

**Por qué es defendible:** es análisis semántico de documento no estructurado contra un estándar legal. No hay regla SQL que lo haga. Y es literalmente el control que la ley pide y que nadie está ejerciendo en tiempo real.

### 3.2 Resolución de entidades desde lenguaje natural ← *el motor del Modo Vigilancia*

El usuario escribe "el contrato de los escombros en Quimbaya", "la alcaldía de mi pueblo" o el nombre de una empresa que vio en una valla. El sistema resuelve a entidad contratante + NIT + procesos, y desambigua mostrando candidatos. **Sin pedir NIT.** Es la brecha #4 del panorama competitivo y es lo que baja el costo de entrada al control ciudadano de horas a segundos.

### 3.3 Narración en lenguaje ciudadano

Traducir el hallazgo técnico a algo que se entienda sin saber de contratación: *"el 61 % del valor se lo llevaron 2 empresas"* en vez de *"índice Herfindahl 0,61"*. No es cosmética: es la diferencia entre un dashboard y una herramienta que alguien usa.

### 3.4 Generación del artefacto de acción

Derecho de petición fundamentado: hechos numerados, dato usado, norma citada, entidad destinataria correcta. Redactado a partir del hallazgo específico, no de plantilla.

### 3.5 Lo que sigue siendo determinista (y está bien)

El motor de señales. La IA **narra y contextualiza** estas reglas, no las inventa. Es correcto y hay que decirlo — la trazabilidad es parte del producto.

| # | Señal | Lógica | Fuentes Croma | Por qué importa |
|---|---|---|---|---|
| S1 | Empresa recién creada que gana | < 365 días entre constitución y adjudicación | `rues_entity_by_nit` + `secop_contracts_by_provider` | El patrón clásico post-desastre |
| S2 | Representante compartido | Mismo rep. legal en ≥2 empresas contratando con la misma entidad | `rues_entity_by_nit` + `secop_processes_by_entity` | Detecta competencia simulada |
| S3 | Sancionado que sigue contratando | Sanción vigente + contratos posteriores | `secop_sanctions_by_provider` + `procuraduria_disciplinary_records` + `contraloria_fiscal_records` | Filtro básico que la urgencia se salta |
| S4 | Contrato desproporcionado | Valor del contrato > ingresos anuales reportados, o empresa sin reportes ganando contratos grandes | `supersociedades_financial_statements` + `secop_contract` | Empresa sin músculo financiero ejecutando obra grande |
| S5 | Insolvente contratando | Proceso de insolvencia + adjudicaciones activas | `sicaac_insolvency_cases` + `secop_contracts_by_provider` | Riesgo directo de obra abandonada |
| S6 | Fraccionamiento | ≥2 contratos de objeto similar, misma entidad, fechas cercanas, bajo umbral | `secop_processes_by_entity` | Evade incluso los controles que quedan |
| S7/S8 | Concentración + directa recurrente | % del valor total a un solo proveedor o grupo | `secop_processes_by_entity` + `secop_contracts_by_provider` | En emergencia todo es directo: lo que importa es la concentración |
| S10 | Deudor moroso del Estado contratando | Registro en BDME + contratos activos | `contaduria_state_delinquent_debtors` + `secop_contracts_by_provider` | Le debe al Estado y el Estado le sigue pagando |

**Ocho señales. S9 (adiciones significativas) queda fuera del MVP** — depende de que el dato de modificaciones esté disponible y no vale el riesgo hoy. Va al roadmap.

**Calibración honesta:** las implementaciones serias encuentran señales en 12–40 % de los contratos (anticorrupcion.co: 12,46 %; RICG: ~12 %; FUNES: 40 %). Se comunica como **priorización**, nunca como escándalo. Nunca "probabilidad de corrupción".

---

## 4. Arquitectura de producto: un motor, dos modos

```
                    ┌─────────── MOTOR LUMEN ───────────┐
                    │ 1. Resolución de entidades (IA)   │
                    │ 2. Motor de 8 señales (determinista)
                    │ 3. Lector IA de justificación (PDF)
                    │ 4. Grafo de actores                │
                    │ 5. Generador de acción             │
                    └────┬─────────────────────┬─────────┘
         ┌───────────────┘                     └───────────────┐
         ▼                                                     ▼
┌── MODO EMERGENCIA (push) ──┐              ┌── MODO VIGILANCIA (pull) ──┐
│ Monitor cada N horas:       │              │ El ciudadano pregunta en    │
│ contratos nuevos con causal │              │ lenguaje natural, o sube    │
│ de urgencia en dptos        │              │ el PDF de un contrato que   │
│ afectados                   │              │ vio en su municipio         │
└─────────────┬───────────────┘              └─────────────┬───────────────┘
              ▼                                            ▼
   ┌──────────┬──────────┬──────────┐          ┌───────────┬───────────┐
   ▼          ▼          ▼          ▼          ▼           ▼
WHATSAPP  PLATAFORMA  DIGEST    API/MCP     CHAT WEB   WHATSAPP
(alerta)  (ficha +   (semanal  (roadmap)   (la demo)  (mismo canal)
          grafo)     por dpto)
                            │
                            ▼
                    Cache local (Croma cacheado = demo offline posible)
```

**La inversión clave frente al v1:** en el Modo Emergencia el usuario no inicia la interacción, el sistema lo busca a él. **El complemento frente al v2:** el Modo Vigilancia existe porque el push solo cubre a quien ya está suscrito en un municipio vigilado — y el problema es nacional y permanente.

### Los dos sentidos del canal WhatsApp

- **Push (el diferenciador):** "🔔 Nuevo contrato de $X en [municipio] con 3 señales. La justificación de urgencia no menciona daños específicos del sismo. Ver evidencia / Generar derecho de petición."
- **Pull (el complemento):** el ciudadano manda una foto o PDF de un contrato que vio y recibe el análisis. Útil justo donde no hay datos abiertos todavía.

---

## 4.5 Modo Vigilancia: consulta ciudadana

*(recuperado del v1 §5 e integrado como segundo modo del mismo motor)*

### 4.5.1 Rutas de resolución de entidades

| Entrada del usuario | Ejemplo | Ruta de resolución | Herramientas Croma |
|---|---|---|---|
| Empresa o persona | "¿Quién es Conalvías?" | Búsqueda por nombre → candidatos (NIT, ciudad, CIIU) → el usuario confirma | `rues_entities_by_name` → `rues_entity_by_nit` |
| Entidad pública | "¿Cómo contrata la Alcaldía de Medellín?" | Procesos de la entidad → proveedores frecuentes → grafo inverso | `secop_processes_by_entity` |
| Obra o proyecto famoso | "¿Y el metro de Bogotá qué?" | Catálogo curado → entidad contratante + palabras clave de objeto | Catálogo propio + `secop_processes_by_entity` |
| Contrato o proceso específico | "el proceso LP-123" | Consulta directa | `secop_process` / `secop_contract` |

### 4.5.2 Reglas del agente conversacional (no negociables)

1. **Desambiguar antes de analizar.** Si hay 3 empresas con nombres parecidos, mostrar candidatos con NIT, ciudad y actividad. Nunca asumir.
2. **Narrar en lenguaje ciudadano.** Ver §3.3.
3. **Cada afirmación con fuente.** Toda señal muestra dato usado, regla aplicada, enlace oficial y fecha de consulta.
4. **Siempre ofrecer el siguiente paso.** ¿Ver la red? ¿Generar evidencia? ¿Redactar derecho de petición?
5. **Lenguaje seguro.** Jamás "corrupto", "ilegal" o "robo". Siempre "señal", "patrón inusual", "merece revisión".
6. **Saber decir "no sé".** Si no hay datos, decirlo y sugerir qué documento pedir.

### 4.5.3 Guion de diálogo (para la demo y para el video)

> **Usuario:** oye, ¿el metro de Bogotá tiene algo raro?
> **Lumen:** Encontré la Empresa Metro de Bogotá S.A.S. con 340 procesos en SECOP II. ¿Analizo los contratos de mayor valor o los proveedores más recurrentes?
> **Usuario:** los proveedores
> **Lumen:** El 61 % del valor se concentra en 2 consorcios. En el principal detecté 3 señales: (1) adjudicación sin competencia efectiva, (2) uno de sus integrantes comparte representante legal con otra firma que contrata con la misma entidad, (3) esa firma tiene un proceso de insolvencia abierto. Aquí está la evidencia de cada una con su enlace a la fuente oficial. ¿Genero el paquete de evidencia o un derecho de petición?

### 4.5.4 Catálogo curado (6 casos, mixto)

Precargados y **validados a mano**, mapeados a entidad contratante + palabras clave + análisis cacheado.

| Caso | Para qué sirve en la demo |
|---|---|
| Metro de Bogotá | La pregunta obvia del jurado. Respuesta instantánea |
| Ruta del Sol | Caso reconocible de red de actores |
| Centros Poblados / MinTIC | Empresa sin músculo financiero ganando contrato enorme (S4 en vivo) |
| **UNGRD 2024** | El antecedente directo: la agencia de gestión del riesgo como caso de corrupción |
| **Mocoa 2017** | Emergencia pasada: valida el motor sobre contratación de desastre |
| **Providencia post-Iota 2020** | Emergencia pasada: reconstrucción con control posterior fallido |

Los tres últimos son también las semillas del **análogo histórico** (§6). Un caso sirve dos veces.

**Por qué curado:** garantiza que la demo responda al instante y que ninguna señal mostrada en video sea un falso positivo vergonzoso.

---

## 4.6 Flujo de uso end-to-end

El diagrama de §4 son cajas. Esto es el recorrido. **Cada paso numerado corresponde a un endpoint de §5.5 y tiene un dueño en §10.**

### Flujo A — Modo Emergencia (push) · el del video

1. **El monitor despierta** (cada N horas). Pide a Croma los contratos nuevos con causal de urgencia o emergencia en los departamentos afectados, desde el 11 de agosto. → *B3*
2. **Filtro de novedad.** Los que ya están en Supabase se descartan. Solo se procesa lo nuevo. → *B3*
3. **Enriquecimiento.** Por cada contrato nuevo, se traen las fuentes que las señales necesitan: RUES del proveedor, sanciones, estados financieros, insolvencia, morosidad, histórico con esa entidad. → *B1*
4. **Motor de señales.** Se evalúan las 8 reglas. Cada señal disparada guarda su regla legible, el dato que la disparó y la fuente oficial con fecha de consulta. → *B1*
5. **Lector de justificaciones.** Si el contrato tiene PDF de justificación de urgencia, la IA lo lee y emite veredicto de tres niveles con cita textual. → *B2*
6. **Nivel de atención.** Función determinista de cuántas señales, su peso y el veredicto del lector. **Tres estados con color. Nunca un número.** → *B1*
7. **Se arma el Caso** y se guarda en Supabase: entidad, proveedor, municipio, valor, objeto, señales, lectura, subgrafo de actores, narración en lenguaje ciudadano. → *B3*
8. **Si el nivel es medio o alto**, se busca a quién avisar: suscriptores de ese municipio o departamento. → *B3*
9. **Sale el WhatsApp.** Máximo 5 líneas, lenguaje ciudadano, con enlace a la ficha del caso. → *B3*
10. **El usuario abre el enlace** y ve la ficha completa: señales como tarjetas con su evidencia y su fuente, el grafo, el disclaimer visible. → *UI*
11. **Pulsa "Generar derecho de petición".** La IA redacta el borrador a partir de ese hallazgo específico, con hechos numerados y norma citada. → *B2*
12. **Copia o descarga** y lo manda. Fin del flujo. → *UI*

### Flujo B — Modo Vigilancia (pull) · el que lo hace durar

1. **El usuario escribe en lenguaje natural**: "¿la alcaldía de mi pueblo tiene algo raro?", el nombre de una empresa, o pega el número de un proceso. → *UI*
2. **Resolución de entidades.** La IA interpreta y devuelve candidatos con NIT, ciudad y actividad. Si el texto cae en el catálogo curado, resuelve directo. → *B2*
3. **Desambiguación.** Si hay más de un candidato, se muestran como tarjetas y **el usuario elige**. Nunca se asume. → *UI*
4. **A partir de aquí es el mismo motor**: pasos 3 a 7 del Flujo A. Si el caso ya está cacheado en Supabase, responde al instante. → *B1 / B3*
5. **Respuesta narrada** en lenguaje ciudadano, con las mismas tarjetas de señal de la ficha. → *B2 / UI*
6. **Siempre se ofrece el siguiente paso**: ¿ver la red de actores? ¿generar el paquete de evidencia? ¿redactar el derecho de petición? → *UI*
7. **Ruta alterna:** el usuario sube el PDF de un contrato que vio en su municipio. Se salta la resolución y entra directo al lector de justificaciones. Es la ruta que sirve donde todavía no hay datos abiertos. → *B2*

### Lo que los dos flujos comparten

Pasos 3 a 7 del Flujo A son **el mismo código**. El Modo Vigilancia no construye backend nuevo: cambia el disparador (una persona en vez de un cron) y la salida (chat en vez de WhatsApp). Por eso cabe en el reloj. Si alguien empieza a escribir un segundo motor, se está saliendo del plan.

---

## 5. Stack y decisiones cerradas

Todo lo de esta sección está **decidido**. No se reabre sin que lo pida Jonatin.

| Capa | Decisión | Notas |
|---|---|---|
| **Datos** | **Croma**, fuente única | Confirmado, con acceso funcionando. No hay plan B de Socrata |
| **Backend** | Python · FastAPI + Pydantic | Cliente Croma encapsulado en un solo servicio con interfaz única |
| **IA** | **Cursor SDK** (`cursor-sdk`, Python) | Ver §5.2. Presupuesto duro de US$50 |
| **Frontend** | **React + Vite** + Tailwind | **Vite, no Next.** Grafo con `react-force-graph` o `vis-network` |
| **Base de datos / cache** | **Supabase**, gestionado por **Supabase CLI** | Migraciones versionadas en el repo. Ver §5.3 |
| **WhatsApp** | **Twilio sandbox** | No Meta Business API: la verificación tarda días. Timebox duro de 2 h |
| **Deploy backend** | **Render** | Prueba de despliegue obligatoria antes de las 06:30 |
| **Deploy frontend** | **Cloudflare Pages** | Prueba de despliegue obligatoria antes de las 06:30 |
| **Repo** | **Monorepo**, público desde el minuto uno | Ver §5.1 |
| **MCP server** | **Congelado** | No se toca hoy. README + roadmap. Ver §10 |

### 5.1 Regla del repo (para quien lo monte)

**Es un monorepo.** Una sola raíz git, un solo README, un solo `.env.example`, backend y frontend en el mismo árbol.

**La organización interna de carpetas la define el equipo, no este brief.** Lo único no negociable:

- Raíz git única, repo **público** desde el primer commit.
- **Cero secretos en el repo.** Todo por variables de entorno, con un `.env.example` que liste las claves sin valores: `CURSOR_API_KEY`, `CROMA_*`, `SUPABASE_*`, `TWILIO_*`.
- README con: problema, arquitectura, cómo correrlo, capturas, y **todas las fuentes y APIs declaradas** (Croma incluida). El código se evalúa: son 15 pts de ejecución técnica.
- Las migraciones de Supabase van versionadas en el repo, no aplicadas a mano en el dashboard.
- El dump JSON de los 6 casos de demo va versionado (ver §5.3).

### 5.2 IA: Cursor SDK, y cómo no quemar los US$50

**El SDK de Cursor no es una API de completions: es un SDK de agentes.** Cada llamada lanza un agente que corre contra un directorio de trabajo y puede usar herramientas. Funciona para lo nuestro, pero hay que blindarlo. Estas seis reglas son obligatorias:

1. **Un solo `llm_client`** con una interfaz mínima. Todo el resto del código llama ahí. Si a las 22:00 el consumo se dispara o la latencia mata el chat, se cambia de proveedor en 20 minutos y no en seis horas.
2. **`cwd` apuntando a un directorio scratch, nunca al repo.** Solo el documento que se está analizando. Es lo que más ahorra: un agente suelto sobre el repo lee archivos que nadie pidió y quema tokens.
3. **`settingSources: []`** (el default). Que no cargue configuración de entorno.
4. **Los 6 casos del catálogo van precomputados y cacheados.** Durante la grabación del video: **cero llamadas al LLM en vivo.** Protege el presupuesto y protege la demo.
5. **SDK de Python es síncrono por defecto y FastAPI es async.** Usar `AsyncClient.launch_bridge` y no mezclar clientes sync y async en el mismo path.
6. **Modelo: no hardcodear un ID a ciegas.** En los primeros 45 min correr `Cursor.models.list()` para ver a qué tiene acceso la cuenta. Punto de partida: `composer-2.5` (rápido y barato) para narración y resolución de entidades; el modelo más fuerte disponible solo para el **lector de justificaciones**, que es la feature estrella y hace pocas llamadas.

**Higiene de errores** (viene del SDK y evita perder una hora): una excepción `CursorAgentError` significa que el run **nunca arrancó** — es auth, config o red. Un `result.status == "error"` significa que **arrancó y falló**. Son bugs distintos. Y siempre disponer el agente con context manager: si no, se filtran procesos.

**Toda salida del LLM debe citar el fragmento fuente.** Si no puede citar, dice que no puede concluir. Esto es guardarraíl (§16.9), no preferencia.

### 5.3 Supabase y el respaldo de grabación

Supabase es la base real: casos, señales calculadas, lecturas de justificación, suscripciones de WhatsApp. Gestionada por CLI, con migraciones en el repo.

**Pero Supabase es Postgres alojado: si internet falla mientras grabas, el cache no te salva.** Por eso:

> **Dump JSON de los 6 casos del catálogo, versionado en el repo**, y un flag que hace que el frontend lea de ahí. Es el respaldo de grabación, no la arquitectura. Existe para que un corte de red a las 07:00 no cueste el hackathon.

### 5.4 Pruebas de despliegue (no dejarlas para el final)

Render y Cloudflare Pages tienen que haber recibido **un despliegue real y verificado antes de las 06:30**, abierto desde un dispositivo que no sea el del equipo. Un deploy que se estrena a las 08:00 es un deploy que falla a las 08:00.

---

## 5.5 Contrato de la API y modelo de datos

**Esto se acuerda entre los cuatro en los primeros 45 minutos, antes de que nadie escriba lógica.** Los esquemas Pydantic y un JSON de ejemplo por endpoint se suben al repo en el primer commit. A partir de ahí:

- El frontend construye contra los **fixtures**, sin esperar al backend.
- B1, B2 y B3 trabajan en paralelo sin bloquearse.
- Si alguien necesita cambiar el contrato, **lo anuncia en el chat del equipo**. Un cambio silencioso de esquema a las 23:00 cuesta dos horas.

### Modelo de datos (el vocabulario compartido)

| Objeto | Campos | Regla |
|---|---|---|
| `Candidato` | `nombre`, `nit`, `ciudad`, `actividad`, `tipo` | Lo que devuelve la resolución de entidades para desambiguar |
| `Fuente` | `herramienta_croma`, `url_oficial`, `consultado_en` | **Obligatoria.** Ver regla de abajo |
| `Senal` | `codigo` (S1…S10), `nombre`, `nivel`, `regla_legible`, `datos_usados`, `fuente` | `regla_legible` es texto que un ciudadano entiende, no la expresión de la regla |
| `Lectura` | `veredicto` (`solida` / `generica` / `sin_relacion`), `puntos[]` con `pregunta`, `hallazgo`, `cita_textual`, `pagina`, `no_concluye_por` | Salida del lector de justificaciones |
| `Actor` | `id`, `tipo` (`empresa` / `persona` / `entidad`), `nombre`, `nit`, `rol` | Nodo del grafo |
| `Grafo` | `nodos[Actor]`, `aristas[]` con `origen`, `destino`, `tipo`, `fuente` | 5–12 nodos. Curado |
| `Caso` | `id`, `modo` (`emergencia` / `vigilancia`), `entidad`, `proveedor`, `municipio`, `valor`, `objeto`, `fecha`, `nivel_atencion`, `senales[]`, `lectura`, `grafo`, `narracion`, `disclaimer`, `generado_en` | El objeto central. Todo gira alrededor de esto |
| `Artefacto` | `tipo`, `titulo`, `cuerpo_markdown`, `normas_citadas[]`, `destinatario` | Los 4 productos de la capa de acción (§7) |

**Dos guardarraíles escritos en el tipo, no en la documentación:**

1. **`Senal` no se puede construir sin `fuente`.** Si no hay fuente oficial con fecha, no hay señal. El guardarraíl ético deja de depender de que alguien se acuerde.
2. **`nivel_atencion` es un enum de tres valores** (`bajo` / `medio` / `alto`). No es un número, no es un porcentaje, no es un score. Si aparece un float en ese campo, alguien rompió el producto.

### Endpoints

| Método | Ruta | Entrada | Salida | Dueño |
|---|---|---|---|---|
| `POST` | `/resolver` | `{ texto }` | `Candidato[]` | B2 |
| `POST` | `/analizar` | `{ nit? , entidad_id? , contrato_id? }` | `Caso` | B1 |
| `GET` | `/caso/{caso_id}` | — | `Caso` | B3 |
| `POST` | `/justificacion` | PDF (multipart) o `{ url }` | `Lectura` | B2 |
| `GET` | `/red/{nit}` | — | `Grafo` | B1 |
| `POST` | `/accion` | `{ caso_id, tipo }` | `Artefacto` | B2 |
| `GET` | `/monitor/nuevos` | `?desde=` | `Caso[]` | B3 |
| `POST` | `/alerta` | `{ caso_id, destinatario }` | `{ estado }` | B3 |
| `POST` | `/chat` | `{ mensaje, contexto? }` | `{ narracion, caso?, candidatos?, siguientes_pasos[] }` | B2 |

`/chat` es el único endpoint exclusivo del Modo Vigilancia, y por dentro orquesta `/resolver` + `/analizar`. **No es un motor aparte.**

---

## 6. El problema de datos y cómo se resuelve

Con Croma cerrado, el riesgo ya no es la fuente. **El riesgo #1 real es que los contratos del sismo casi no existen todavía en SECOP: llevamos cinco días.** Si la demo depende de encontrar un contrato sospechoso del sismo, el video sale vacío.

**Resolución en tres capas, y las tres van en el video:**

1. **Lo que ya existe.** Un barrido de lo poco que haya entrado desde el 11 de agosto. Aunque salga limpio, sirve: demuestra que el monitor está vivo y que el watchlist está encendido desde el día uno.
2. **El análogo histórico (esto es lo potente, y Croma lo hace barato).** Correr el motor sobre contratación de emergencia pasada — ola invernal 2010-2011 / Fondo Adaptación, Mocoa 2017, Providencia post-Iota 2020, UNGRD 2024 — y mostrar que **detecta los patrones que después resultaron ser escándalos**. El argumento es demoledor: *"esto es lo que habríamos visto en tiempo real, en vez de en la Contraloría cuatro años después."*
3. **El lector de justificaciones sobre documentos reales de urgencia manifiesta** que ya se están publicando (el Acuerdo de la Rama Judicial es de anteanoche). Aunque el contrato aún no exista, el acto administrativo sí.

Y el Modo Vigilancia tiene su propio colchón: **no depende del sismo en absoluto.** Si las tres capas fallan, el catálogo curado sigue dando demo.

**Acción inmediata (primeros 45 min):** alguien confirma que existe algo real que analizar en las tres capas. Si la capa 2 no da, hay que saberlo a las 17:00, no a las 4 de la mañana.

---

## 7. Capa de acción

Cada análisis, venga del push o del pull, termina en un artefacto usable. Es la brecha #2: nadie más pasa de la alerta a la acción.

| Artefacto | Contenido | Fundamento |
|---|---|---|
| **Paquete de evidencia** | Señal + regla + datos + captura + enlace oficial + fecha de consulta | Trazabilidad total |
| **Derecho de petición** | Borrador con hechos numerados, dato usado y norma citada, dirigido a la entidad correcta | `legalize_laws_search` + `ancp_cce_conceptos_search` |
| **Informe de veeduría** | Resumen ejecutivo + tabla de señales + preguntas sugeridas para la entidad | Exportable y compartible |
| **Guía de denuncia** | Canal formal según el tipo de señal (PACO, Contraloría, Procuraduría, SIC si hay indicio de colusión) | Enlaces oficiales |

**Prioridad de construcción:** el derecho de petición primero (es el que sale en el video). Los otros tres si el reloj lo permite; el paquete de evidencia es prácticamente gratis porque ya se calcula.

---

## 8. El video de 60 segundos — se diseña PRIMERO

**No es el último entregable. Es la especificación del producto.** Si algo no cabe en estos 60 segundos, no se construye hoy.

### Storyboard

| Tiempo | Qué se ve | Qué se oye |
|---|---|---|
| 0:00–0:07 | Texto grande sobre negro: **US$450.000.000. Sin licitación. Control posterior.** | Silencio o un solo golpe de sonido |
| 0:07–0:16 | Cifra UNGRD: 448 municipios, 145.601 personas afectadas. Mapa | "El 11 de agosto Colombia habilitó contratación directa por 12 meses para reconstruirse. El control llega después de que la plata se gastó." |
| 0:16–0:28 | **Teléfono. Llega el WhatsApp.** Se lee la alerta completa en pantalla | "Lumen vigila esos contratos y avisa." |
| 0:28–0:40 | Tap → plataforma. Señales con evidencia, grafo de actores de fondo. **Zoom al lector de IA marcando la justificación que no menciona daños del sismo, con la cita subrayada** | "La ley exige que la justificación tenga relación verificable con el sismo. Nuestra IA lee ese documento y verifica si la tiene." |
| 0:40–0:48 | Botón → derecho de petición generándose, con norma citada | "Y convierte el hallazgo en un derecho de petición listo para enviar." |
| **0:48–0:56** | **Modo Vigilancia: se escribe "¿la alcaldía de mi municipio tiene algo raro?" y salen las señales con su fuente** | **"El sismo es la ventana que está abierta hoy. La fuga de plata pública está abierta todos los días — y Lumen también."** |
| 0:56–1:00 | Logo + frase de seguridad en texto | "No acusamos. Ayudamos a preguntar mejor." |

**Qué se sacrificó para meter los 8 s del Modo Vigilancia:** el tramo dedicado del grafo. El grafo sigue apareciendo, pero como fondo del bloque 0:28–0:40, no como protagonista. Es la decisión correcta: el grafo es bonito pero no se lee en 5 segundos en un video pequeño.

### Reglas de producción

- **Grabar la pantalla a tamaño de teléfono real y hacer zoom.** El jurado ve el video pequeño; un dashboard full-width es ilegible.
- Una sola tipografía, un solo color de acento, fondo oscuro. Cero chrome de navegador.
- Cada texto en pantalla ≤ 7 palabras.
- Locución: puede usarse **HeyGen** (es sponsor del evento). Bonus menor, pero es señal de que leíste el material.
- **Subtítulos quemados.** Muchos jurados ven sin audio.
- Grabar una versión de respaldo apenas exista el flujo end-to-end, aunque esté feo. La versión bonita se hace encima.

---

## 9. UX/UI — lo que siempre se descuida

**Una persona dedicada en exclusiva desde el minuto cero, que diseña y codea.** No es "la que maqueta al final": es dueña única del frontend, y arranca contra fixtures sin esperar al backend.

Cuatro pantallas. Nada más.

1. **La alerta (WhatsApp).** Copy en lenguaje ciudadano. "El 61 % del valor se concentró en 2 empresas", nunca "índice Herfindahl 0,61". Máximo 5 líneas.
2. **La ficha del caso.** Arriba: municipio, valor, entidad, nivel de atención. Centro: las señales como tarjetas, cada una con su regla, su dato y su enlace oficial con fecha de consulta. Abajo: el subgrafo de actores. Un solo scroll.
3. **El chat (Modo Vigilancia).** Entrada libre, candidatos de desambiguación como tarjetas clicables, respuesta narrada con las mismas tarjetas de señal de la pantalla 2. **Reusa componentes: no es una pantalla nueva, es un envoltorio distinto.**
4. **El artefacto.** El derecho de petición generándose, con botón de copiar/descargar.

**Reglas de diseño no negociables:**
- **Nivel de atención en tres estados con color**, nunca un score numérico de "corrupción".
- **Disclaimer visible en cada resultado**, no en un footer: *"Herramienta de priorización ciudadana. Una señal no es prueba de irregularidad."*
- Cada dato con enlace a la fuente oficial y fecha de consulta. Eso es UI, no solo ética: es lo que hace que el jurado te crea.
- El grafo se muestra **curado y pequeño** (5–12 nodos). Un hairball es peor que no mostrar grafo.

---

## 10. Roles (4 personas: 3 backend + 1 UI/UX)

| Rol | Responsabilidad | Endpoints que le pertenecen | Hito propio |
|---|---|---|---|
| **B1 — Datos** | Cliente Croma, normalización, las **8 señales**, el grafo de actores, validación a mano del catálogo curado y de los casos históricos | `/analizar`, `/red/{nit}` | **h+4 (20:00):** el motor corre en CLI sobre un caso real y escupe señales con fuente |
| **B2 — IA** | `llm_client` blindado (§5.2), lector de justificaciones (el núcleo), resolución de entidades, prompts del agente, narración ciudadana, generador de artefactos | `/resolver`, `/justificacion`, `/accion`, `/chat` | **h+5 (21:00):** el lector clasifica correctamente 3 documentos reales de urgencia manifiesta |
| **B3 — Plataforma** | FastAPI y ensamblado, monitor programado, Supabase + migraciones por CLI, Twilio, despliegue en Render | `/caso/{id}`, `/monitor/nuevos`, `/alerta` | **h+7 (23:00):** llega un WhatsApp real a un teléfono real |
| **UI/UX** | **Diseña y codea** el frontend completo en React + Vite: las 4 pantallas, el grafo, el copy. Dueño único del frontend y del despliegue en Cloudflare Pages | — | **h+6 (22:00):** las 4 pantallas navegables contra fixtures · **h+10 (02:00):** integradas contra la API real |
| **Jonatin — video** | **Dueño del video de 60 s desde las 22:00**, en paralelo a su trabajo de coordinación. Guion, grabación, subtítulos, corte final | — | **h+10 (02:00):** primer corte feo grabado · **h+16 (08:00):** final subido |

**Sobre el reparto:** UI/UX no toca backend y ningún backend toca `/web`. Eso es lo que permite que cuatro personas hagan commit al mismo monorepo sin pisarse. El puente entre los dos mundos es el contrato de §5.5, acordado antes de escribir la primera línea.

**Sobre el video:** es la entrega, no un extra. Que Jonatin sea el dueño resuelve el hueco de que UI/UX ya no puede hacer las dos cosas — pero significa que **a las 22:00 Jonatin deja de coordinar y se pone a grabar**. Hay que asumirlo, no descubrirlo a las 4 de la mañana.

**Hito crítico global — hora 7 (23:00 de hoy):** existe un flujo completo aunque sea feo — dato → señal → lectura IA → alerta. Si a las 23:00 no existe, **se recorta alcance, no se extiende el horario.**

**Orden de hard-cuts si el reloj aprieta (en este orden exacto):**
1. Informe de veeduría y guía de denuncia (§7)
2. Grafo de actores visual (se sustituye por lista de vínculos)
3. Twilio (se muestra la plataforma en vez del WhatsApp real)
4. Modo Vigilancia en el video (se queda en la plataforma y el README)

**Regla anti-scope-creep:** el **MCP server no se toca** hasta que el flujo end-to-end corra y el primer corte del video exista. Es el diferenciador que más emociona al equipo y el que menos se ve en 60 segundos. Va en el README y en el roadmap, y se nombra como brecha en el panorama competitivo.

---

## 11. Cronograma (desde las 16:00 del sábado · 17 h)

| Hora | Los 4 juntos | B1 Datos | B2 IA | B3 Plataforma | UI/UX |
|---|---|---|---|---|---|
| **16:00–16:45** | **Acordar el contrato de §5.5** · monorepo público · `.env.example` · probar credenciales Croma · `Cursor.models.list()` · confirmar que hay datos reales en las 3 capas de §6 | | | | |
| 16:45–20:00 | | Cliente Croma + 8 señales en CLI | `llm_client` + lector de justificaciones | Esqueleto FastAPI + Supabase por CLI | Wireframes y las 4 pantallas contra fixtures |
| 20:00–22:00 | | Grafo de actores | Resolución de entidades + narración | Monitor + Twilio (**timebox duro 2 h**) | Pantallas navegables |
| **22:00–23:00** | **Integración.** Jonatin arranca el guion del video | | | | |
| **23:00** | **HITO CRÍTICO h+7: flujo completo aunque sea feo.** Si no existe, se aplica el orden de hard-cuts. No se extiende el horario | | | | |
| 23:00–02:00 | | Validar a mano los 6 casos curados | Generador de artefactos | Precomputar y cachear los casos · dump JSON | Integrar contra la API real |
| **02:00** | **Congelación de features.** Lo que no exista, no existe | | | | |
| 02:00–03:30 | | | | | Jonatin: **primer corte del video, aunque esté feo.** Respaldo grabado |
| 03:30–06:30 | | Revisión final de señales y fuentes | Revisión de salidas del LLM | **Despliegue Render + Cloudflare verificado** | Pulido de UI |
| 06:30–08:00 | README final, fuentes declaradas | | | | Jonatin: video final con subtítulos quemados |
| **08:00–09:00** | Subir al repo oficial · verificar que abre desde otro dispositivo | | | | **ENTREGADO** |

**Entregar a las 08:00, no a las 08:55.** El deck dice "no se aceptan retrasos".

---

## 12. Riesgos y plan B

| Riesgo | Gravedad | Mitigación |
|---|---|---|
| No hay contratos del sismo publicados todavía | **Alta** | Las tres capas de §6 + el catálogo curado del Modo Vigilancia. Se verifica en los primeros 45 min |
| Croma o Supabase lentos o caídos durante la grabación | Alta | Casos precomputados + **dump JSON versionado** con flag de lectura local (§5.3). La grabación no depende de la red |
| **Se agotan los US$50 de la API de Cursor** | **Alta** | Las 6 protecciones de §5.2, sobre todo `cwd` scratch y cero llamadas en vivo durante la grabación. B2 revisa consumo a las 20:00 y a las 23:00 |
| La latencia del SDK de agentes hace que el chat se vea lento en el video | Media | El `llm_client` es swappable en 20 min. Y los 6 casos del catálogo responden desde caché, instantáneo |
| El contrato de la API cambia a medianoche y rompe el frontend | Media | Se acuerda a las 16:45 con fixtures en el repo. **Cualquier cambio se anuncia en el chat del equipo**, nunca en silencio |
| El despliegue se estrena el domingo a las 08:00 | Media | Render y Cloudflare Pages verificados **antes de las 06:30**, abiertos desde otro dispositivo (§5.4) |
| Twilio no manda un mensaje real | Media | Timebox de 2 h. Si falla, el video muestra la plataforma y la alerta se ve como notificación en pantalla. No se mockea un WhatsApp falso |
| Falso positivo vergonzoso en el video | **Alta (reputacional)** | Solo casos validados a mano aparecen en el video. Lenguaje de "señal" siempre |
| Scope creep por el segundo modo | Media | El Modo Vigilancia **no construye backend nuevo**: reusa el mismo endpoint del motor. Su costo real es una pantalla y el catálogo. Si a las 23:00 el flujo push no está, se corta (ver orden de hard-cuts en §10) |
| El grafo sale feo o incompleto | Baja | Subgrafo curado de 5–12 nodos, o lista de vínculos |
| Quedarse construyendo cuando toca grabar | **Alta** | A las 02:00 se congelan features. Lo que no exista, no existe |

---

## 13. Vendibilidad: quién paga esto

La pregunta de "viabilidad + escala" (15 pts) no se responde con "es open source y gratis". Se responde nombrando compradores reales.

| Comprador | Por qué paga | Realismo |
|---|---|---|
| **Multilaterales (Banco Mundial, BID)** | El crédito de reconstrucción trae requisitos fiduciarios. El monitoreo de terceros sobre uso de fondos es una línea presupuestal que ya existe en sus programas | **El más fuerte.** Es plata ya aprobada que tiene que gastarse en supervisión |
| **Filantropía de tecnología cívica (OSF, Hivos, NED, Luminate)** | Financian veeduría y periodismo de datos en LATAM. Open Society es sponsor de este hackathon | Alto. Vocabulario y misión alineados |
| **Medios y periodismo de investigación** | Necesitan leads verificables. Modelo FUNES/OjoPúblico. Licencia o alianza | Medio. Poco presupuesto, mucho alcance |
| **Gobernaciones y alcaldías afectadas** | Un alcalde honesto quiere demostrar que gastó bien. Autoauditoría como escudo reputacional | Medio-alto y contraintuitivo: el vigilado también es cliente |
| **Veedurías y JAC** | Usuario principal, no pagador. Es el impacto, no el ingreso | Gratis siempre. Es la razón de existir |

**Modelo:** núcleo abierto y gratuito para ciudadanía y veedurías; monitoreo dedicado, API y reportes fiduciarios como servicio pagado a multilaterales y medios.

---

## 14. Escalamiento: por qué esto no muere el lunes

1. **Temporal.** La declaratoria dura hasta 12 meses prorrogables. El sistema tiene 12 meses de trabajo garantizado desde mañana.
2. **Agnóstico al desastre.** El disparador no es "terremoto", es **la declaratoria de desastre y la urgencia manifiesta**. La próxima ola invernal, el próximo deslizamiento, el próximo incendio: mismo artículo 46, mismas señales, mismo lector. Se configura, no se reconstruye.
3. **Agnóstico a la emergencia.** Sirve igual para contratación de urgencia sanitaria o de orden público.
4. **Exportable.** Perú y México ya están en Croma; Chile y Ecuador tienen regímenes equivalentes. Cambia la fuente, no el motor.
5. **No hay "modo latente": hay un segundo modo, y ya está construido.** El Modo Vigilancia corre sobre contratación ordinaria desde el día uno. El sismo es la puerta de entrada, no el techo.

**La frase para el video o el README:**
> "Los desastres se repiten. La ventana de contratación sin control también. Lumen se enciende cada vez que se abre — y entre una y otra, no se apaga."

### Roadmap post-hackathon

- Alertas suscritas por entidad, departamento o proveedor (digest semanal de patrones).
- **MCP server** (`investigar`, `red_de_vinculos`, `evidencia`): Croma expone *datos*, nosotros exponemos *hallazgos*.
- S9 (adiciones significativas) y el resto del catálogo de señales.
- Widgets embebibles para medios locales.
- Cruce con financiación de campañas (el salto estilo FUNES).
- Expansión a Perú y México.

---

## 15. Panorama competitivo y objeciones del jurado

### En Colombia

| Herramienta | Qué hace | Qué le falta |
|---|---|---|
| **PACO** (gobierno) | Banderas rojas por entidad/contratista; cruza SECOP con sanciones | Solo hechos **ya sancionados**; sin capa de acción; sin push |
| **anticorrupcion.co** | 26 señales sobre 1,27 M contratos, actualización diaria | Contrato aislado; sin grafo; sin lectura de documentos |
| **Contraloría — modelo predictivo (2025)** | ML sobre antecedentes 2014-2025 | Interno, no ciudadano |
| **SIC — Sherlock** | IA para detectar colusión | Enfoque de competencia; uso interno |
| **RICG** (académico) | Banderas rojas sobre SECOP II con API | Piloto sin producto vivo |
| **LuxIA** | Score 0-100, análisis de pliegos | Comercial cerrado |

### En el mundo

| Herramienta | Qué hace | Lección para nosotros |
|---|---|---|
| **FUNES** (OjoPúblico, Perú) | Cruzó 9 bases sobre 245 mil contratos; 40 % con riesgo; Sigma Award 2020 | El valor está en el **cruce de fuentes**, no en el contrato aislado. Es exactamente lo que Croma nos permite |
| **Opentender / Digiwhist** (UE) | 17,5 M licitaciones con filtro de integridad | Metodología validada académicamente |
| **OCP — banderas rojas + Cardinal** | 73 indicadores mapeados a OCDS, librería open-source | No reinventar las reglas: adaptar las públicas |
| **World Bank — GRAS** | 60 indicadores en 4 categorías | Categorías para organizar el catálogo |

### Las 4 brechas que nadie cubre (nuestro espacio)

1. **Grafo de actores** como producto abierto en Colombia — quién está detrás de quién. *(en el MVP)*
2. **De la alerta a la acción** — evidencia → derecho de petición → denuncia. *(en el MVP)*
3. **Distribución agente-nativa** — MCP/API para que otros agentes investiguen. *(roadmap, declarado)*
4. **Entrada conversacional con resolución de entidades** — sin pedir un NIT. *(en el MVP, Modo Vigilancia)*

Y una quinta que abrió el sismo: **lectura semántica de la justificación legal de urgencia manifiesta.** Nadie la hace.

### Las objeciones que van a caer y su respuesta

**"La Contraloría ya tiene control concomitante y preventivo desde 2019."**
> Cierto, y hay que reconocerlo primero. Pero es institucional, discrecional, cubre proyectos seleccionados, y **no es un feed público**. El ciudadano de Quimbaya no recibe nada. No reemplazamos a la Contraloría: le llevamos casos priorizados y le damos al ciudadano la capacidad de preguntar por su cuenta.

**"Esto ya lo hace PACO."**
> PACO muestra lo ya sancionado. Nosotros vigilamos lo que se está firmando esta semana. Y PACO no lee la justificación de la urgencia manifiesta ni te avisa al teléfono.

**"¿Otro chatbot de contratos?"**
> No. El producto es un vigilante que avisa sin que le preguntes. El chat es la segunda puerta, no la primera — y detrás de él no hay un LLM improvisando: hay ocho señales deterministas con su regla y su fuente.

**"Van a generar falsos positivos y señalar inocentes."**
> Por eso el lenguaje es "señal" y "merece revisión", nunca "corrupto". Por eso cada señal muestra su regla, su dato y su fuente. Y por eso el output es un **derecho de petición** — una pregunta formal, que es exactamente lo que un ciudadano tiene derecho a hacer. Los benchmarks serios encuentran señales en 12–40 % de contratos: eso es priorización, no acusación.

**"No tienen datos, el sismo fue hace 5 días."**
> Por eso el sistema se enciende hoy y el video muestra el motor validado contra emergencias pasadas. El watchlist arranca vacío a propósito: es un sistema de vigilancia, no un informe.

**"¿La IA es realmente el núcleo o es un wrapper?"**
> El lector de justificaciones. Análisis semántico de documento no estructurado contra un estándar legal. Ninguna regla lo hace. Y es exactamente el control que la ley exige y que nadie está ejerciendo.

**"¿Esto solo sirve para el sismo?"**
> No, y esa es la diferencia entre un proyecto de hackathon y un producto. El disparador es la declaratoria de desastre, no el terremoto. Y entre desastres el mismo motor vigila contratación ordinaria por consulta ciudadana. La ventana del sismo dura 12 meses; el problema dura siempre.

---

## 16. Guardarraíles (no negociables)

1. **Señales, no acusaciones.** Nunca "X es corrupto". Siempre "patrón que merece revisión".
2. **Disclaimer visible en cada resultado**, no en un footer.
3. **Solo fuentes oficiales**, siempre enlazadas, con fecha de consulta.
4. **No exponer datos sensibles de personas.** El análisis es sobre empresas y contratos. Las personas aparecen solo en su rol público (representante legal) y solo con datos de registro mercantil. Nada de antecedentes penales, salud o estado de cédula, aunque Croma los exponga.
5. **Nómina y sueldos fuera del alcance.** No aporta y multiplica el riesgo.
6. **Tono sobrio.** Hay 288 muertos y esto pasó hace cinco días. Nada de estética de thriller ni de denuncia. La contención comunica seriedad.
7. **Declarar Croma abiertamente** en el video, el README y cualquier respuesta al jurado, junto con todas las fuentes y APIs usadas.
8. **Respetar los términos de uso de Croma:** límites de cuota y reglas de redistribución de datos. No republicamos bases, publicamos hallazgos con enlace a la fuente.
9. **El lector de IA nunca afirma sin citar.** Si no puede citar el fragmento del documento, dice que no puede concluir.

---

## 17. Checklist de entrega

- [ ] Equipo creado en la plataforma / canal oficial (verificado con un Ops Manager)
- [ ] Track 01 confirmado en el registro
- [ ] Repo público (monorepo) con README: problema, arquitectura, capturas, cómo correrlo, **Croma y todas las fuentes declaradas**
- [ ] `.env.example` completo y **cero secretos commiteados** (verificado con una búsqueda en el historial)
- [ ] Backend desplegado en Render y frontend en Cloudflare Pages, **verificados antes de las 06:30**
- [ ] Dump JSON de los 6 casos versionado y el flag de lectura local probado
- [ ] Migraciones de Supabase versionadas en el repo, no aplicadas a mano
- [ ] Consumo de la API de Cursor por debajo del presupuesto, revisado a las 23:00
- [ ] Video ≤ 60 s, con subtítulos quemados, subido al repo oficial
- [ ] Demo desplegada y probada desde un dispositivo distinto al del equipo
- [ ] Cada señal del video muestra su evidencia y su fuente oficial
- [ ] Los 6 casos del catálogo curado validados a mano (ninguno con falso positivo)
- [ ] Los dos modos visibles: el push en el video, el pull en el video y en la demo
- [ ] La frase "no acusamos" aparece en el video
- [ ] Versión de respaldo del video grabada desde las 03:30
- [ ] Entregado a las **08:00**, no a las 08:55
