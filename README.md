# Lumen

**Vigilancia ciudadana sobre la plata de la reconstrucción.**

> El control de la plata de la reconstrucción es posterior. Nosotros lo hacemos hoy.

Hackathon CTW 2026 · Track 01: Tecnología para la Transparencia · Bogotá, 15–16 de agosto de 2026.

> **Herramienta de priorización ciudadana. Una señal no es prueba de irregularidad.**
> No acusamos: priorizamos dónde mirar y entregamos evidencia verificable para preguntar mejor.

---

## El problema

El 11 de agosto de 2026, el Decreto 1171 declaró desastre nacional tras el terremoto del día 10. Con
eso se activó el artículo 46 de la Ley 1523: demolición, retiro de escombros y reconstrucción se
pueden adjudicar **de forma directa, sin licitación**, durante hasta 12 meses prorrogables.

Los números de la UNGRD al 14 de agosto: 15 departamentos, 448 municipios, 57.516 familias, 145.601
personas afectadas, 288 fallecidos, 80.744 viviendas averiadas y 12.504 destruidas. El Gobierno
gestiona un crédito contingente de hasta US$450 millones con el Banco Mundial.

Y el control de la Contraloría sobre esa contratación es, según el propio marco, **posterior**.

Miles de millones se van a mover durante doce meses por contratación directa, en cientos de
municipios sin capacidad institucional ni prensa local. Cuando el control llegue, la plata ya se
gastó. El antecedente inmediato es el escándalo de la UNGRD de 2024: la propia agencia de gestión
del riesgo, convertida en caso de corrupción.

Debajo hay un problema más viejo. Los datos de contratación pública existen y son públicos, pero
están dispersos, en formatos técnicos, y exigen saber de contratación estatal para interpretarse. El
costo de entrada al control ciudadano es tan alto que la mayoría abandona antes de formular la
primera pregunta.

---

## Qué hace Lumen

Un motor, dos modos.

**Modo Emergencia (push).** Corre solo. Revisa los contratos nuevos que entran por el régimen
excepcional de emergencia, lee las justificaciones que la ley exige, detecta patrones que merecen
revisión, y avisa por WhatsApp al veedor, al periodista local o al líder comunal del municipio
afectado — con la evidencia y con un derecho de petición listo para enviar.

**Modo Vigilancia (pull).** El mismo motor, expuesto como agente conversacional. Cualquier persona
escribe en lenguaje natural — *"¿la alcaldía de mi pueblo tiene algo raro?"*, el nombre de una
empresa que vio en una valla — y recibe la red de actores detrás del contrato, las señales con su
evidencia y el artefacto para actuar. **Sin pedir un NIT. Sin saber qué es SECOP.**

> El sismo es la ventana que está abierta hoy. La fuga de plata pública está abierta todos los días.

---

## Dónde está la IA, y por qué no es decoración

Cuatro funciones que no se pueden hacer con reglas deterministas:

**1. El lector de justificaciones de urgencia manifiesta.** La norma exige que toda contratación bajo
urgencia manifiesta tenga relación directa y verificable con los hechos que dieron lugar a la
emergencia, precedida de diagnósticos técnicos. Esa justificación es un PDF en texto libre. El
modelo lo lee y evalúa si menciona daños concretos y ubicados o lenguaje genérico de plantilla, si
el objeto contractual guarda relación causal con el daño descrito, si se invocan los diagnósticos
que la norma exige, y si la fecha del hecho justificante es posterior al 10 de agosto. Devuelve un
veredicto de tres niveles **con la cita textual que sustenta cada punto**.

Es análisis semántico de documento no estructurado contra un estándar legal. No hay regla SQL que lo
haga. Y es literalmente el control que la ley pide y que nadie está ejerciendo en tiempo real.

**2. Resolución de entidades desde lenguaje natural.** Resolver *"el contrato de los escombros en
Quimbaya"* a entidad contratante, NIT y procesos, mostrando candidatos para desambiguar. Es lo que
baja el costo de entrada al control ciudadano de horas a segundos.

**3. Narración en lenguaje ciudadano.** *"El 61 % del valor se lo llevaron 2 empresas"* en vez de
*"índice Herfindahl 0,61"*. No es cosmética: es la diferencia entre un dashboard y una herramienta
que alguien usa.

**4. Generación del artefacto de acción.** Un derecho de petición con hechos numerados, dato usado,
norma citada y entidad destinataria correcta, redactado a partir del hallazgo específico.

**Lo que NO hace la IA, y está bien decirlo:** el motor de señales es determinista. La IA narra y
contextualiza esas reglas, no las inventa. La trazabilidad es parte del producto.

---

## Las ocho señales

Cada una guarda su regla legible, el dato que la disparó y la fuente oficial con su fecha de
consulta.

| # | Señal | Lógica | Por qué importa |
|---|---|---|---|
| S1 | Empresa recién creada que gana | Menos de 365 días entre constitución y adjudicación | El patrón clásico post-desastre |
| S2 | Representante compartido | Mismo representante legal en dos o más empresas que contratan con la misma entidad | Detecta competencia simulada |
| S3 | Sancionado que sigue contratando | Sanción vigente más contratos posteriores | Filtro básico que la urgencia se salta |
| S4 | Contrato desproporcionado | Valor del contrato mayor que los ingresos anuales reportados | Empresa sin músculo financiero ejecutando obra grande |
| S5 | Insolvente contratando | Proceso de insolvencia más adjudicaciones activas | Riesgo directo de obra abandonada |
| S6 | Fraccionamiento | Contratos de objeto similar, misma entidad, fechas cercanas, bajo umbral | Evade incluso los controles que quedan |
| S7/S8 | Concentración y directa recurrente | Porcentaje del valor total a un solo proveedor o grupo | En emergencia todo es directo: lo que importa es la concentración |
| S10 | Deudor moroso del Estado contratando | Registro en el BDME más contratos activos | Le debe al Estado y el Estado le sigue pagando |

**Calibración honesta:** las implementaciones serias encuentran señales en el 12–40 % de los
contratos (anticorrupcion.co: 12,46 %; RICG: ~12 %; FUNES: 40 %). Se comunica como **priorización**,
nunca como escándalo, y jamás como "probabilidad de corrupción".

---

## Fuentes y APIs declaradas

Todos los datos vienen de fuentes oficiales, a través de **[Croma](https://usecroma.com)**, que
expone datos del sector público colombiano, peruano y mexicano como un servidor MCP.

| Fuente oficial | Para qué la usamos |
|---|---|
| **SECOP I y II** (Colombia Compra Eficiente) | Procesos, contratos, sanciones a proveedores |
| **RUES** (Cámaras de Comercio) | Registro mercantil, fecha de constitución, representante legal |
| **Supersociedades** | Estados financieros |
| **SICAAC** | Procesos de insolvencia |
| **Procuraduría General de la Nación** | Antecedentes disciplinarios en su rol público |
| **Contraloría General de la República** | Responsabilidad fiscal |
| **Contaduría General de la Nación** | Boletín de Deudores Morosos del Estado |
| **Normativa colombiana** | Fundamento legal del derecho de petición |

**Servicios de terceros:** Croma (datos), Cursor SDK (modelos de lenguaje), Supabase (base de datos),
Render (backend), Twilio (WhatsApp, si aplica).

**Lo que no hacemos:** no republicamos bases de datos. Publicamos hallazgos con enlace a la fuente
oficial y fecha de consulta, respetando los términos de uso de Croma.

---

## Arquitectura

```
                       ┌──────── MOTOR LUMEN ─────────┐
                       │ 1. Resolución de entidades   │  IA
                       │ 2. Motor de 8 señales        │  determinista
                       │ 3. Lector de justificación   │  IA
                       │ 4. Grafo de actores          │
                       │ 5. Generador de acción       │  IA
                       └───┬──────────────────────┬───┘
          ┌────────────────┘                      └───────────────┐
          ▼                                                       ▼
  MODO EMERGENCIA (push)                              MODO VIGILANCIA (pull)
  El monitor despierta, filtra                        Una persona pregunta en
  novedad y arma casos                                lenguaje natural
          │                                                       │
          ▼                                                       ▼
    WhatsApp + ficha del caso                            Chat + ficha del caso
```

**Los dos modos comparten el mismo código.** El Modo Vigilancia no construye backend nuevo: cambia
el disparador (una persona en vez de un cron) y la salida (chat en vez de WhatsApp).

| Capa | Tecnología |
|---|---|
| Datos | Croma (servidor MCP remoto, JSON-RPC sobre HTTP) |
| Backend | Python 3.13 · FastAPI · Pydantic |
| IA | Cursor SDK |
| Base de datos y caché | Supabase, con migraciones versionadas |
| Despliegue del backend | Render |
| Frontend y su despliegue | Definidos por su responsable |
| Repositorio | Monorepo, público desde el primer commit |

```
api/lumen/
├── contracts/     modelos Pydantic: el vocabulario compartido
├── croma/         cliente de la fuente de datos
├── senales/       motor de las 8 señales
├── ia/            llm_client, lector, prompts, artefactos
├── plataforma/    Supabase, monitor, caché, alertas
└── routers/       un archivo por responsable
```

---

## Cómo correrlo

```bash
git clone <este-repo> && cd lumen
python -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt
cp .env.example .env               # y pon tus credenciales
uvicorn lumen.main:app --reload --app-dir api
```

| URL | Qué es |
|---|---|
| `http://127.0.0.1:8000/health` | Comprobación básica |
| `http://127.0.0.1:8000/health/croma` | Llamada **real** a Croma; confirma que tu token funciona |
| `http://127.0.0.1:8000/docs` | Documentación interactiva de los nueve endpoints |

Pruebas: `pytest -q`. Validan que los fixtures cuadran con los modelos y que los guardarraíles del
producto siguen en pie.

El contrato completo de la API está en [`docs/CONTRATO-API.md`](docs/CONTRATO-API.md), con un JSON de
ejemplo por endpoint en [`fixtures/`](fixtures/).

---

## Guardarraíles

Estos no son buenas intenciones del README: dos de ellos están escritos en los tipos y hay pruebas
que fallan si alguien los rompe.

1. **Señales, no acusaciones.** Nunca "X es corrupto". Siempre "patrón que merece revisión".
2. **`Senal` no se puede construir sin `fuente`.** Sin fuente oficial con fecha, no hay señal.
3. **`nivel_atencion` es un enum de tres valores**, nunca un score numérico de corrupción.
4. **Disclaimer visible en cada resultado**, no en un pie de página.
5. **El lector de IA nunca afirma sin citar.** Si no puede citar el fragmento, dice que no concluye.
6. **No exponemos datos sensibles de personas.** El análisis es sobre empresas y contratos. Las
   personas aparecen solo en su rol público de representante legal y solo con registro mercantil.
7. **Solo fuentes oficiales**, siempre enlazadas y con fecha de consulta.

---

## Por qué esto no muere el lunes

**El disparador no es "terremoto": es la declaratoria de desastre y la urgencia manifiesta.** La
próxima ola invernal, el próximo deslizamiento, el próximo incendio: mismo artículo 46, mismas
señales, mismo lector. Se configura, no se reconstruye. La declaratoria actual dura hasta doce meses
prorrogables, así que el sistema tiene un año de trabajo garantizado desde mañana.

Y entre desastres no se apaga: el Modo Vigilancia corre sobre contratación ordinaria desde el día
uno. Perú y México ya están en Croma; Chile y Ecuador tienen regímenes equivalentes. Cambia la
fuente, no el motor.

**Quién pagaría por esto:** los multilaterales son el comprador más fuerte, porque el crédito de
reconstrucción trae requisitos fiduciarios y el monitoreo de terceros sobre uso de fondos es una
línea presupuestal que ya existe en sus programas. Después, la filantropía de tecnología cívica que
financia veeduría y periodismo de datos en la región, y los medios de investigación que necesitan
leads verificables. Contraintuitivamente, también las alcaldías: un alcalde honesto quiere demostrar
que gastó bien.

**El modelo:** núcleo abierto y gratuito para ciudadanía y veedurías; monitoreo dedicado, API y
reportes fiduciarios como servicio pagado.

### Roadmap

- Alertas suscritas por entidad, departamento o proveedor, con digest semanal.
- **Servidor MCP propio** (`investigar`, `red_de_vinculos`, `evidencia`): Croma expone *datos*,
  nosotros expondríamos *hallazgos*, para que otros agentes puedan investigar.
- S9 (adiciones significativas) y el resto del catálogo de señales.
- Widgets embebibles para medios locales.
- Cruce con financiación de campañas.
- Expansión a Perú y México.
