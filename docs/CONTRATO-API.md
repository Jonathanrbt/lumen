# Contrato de la API

**Este documento es el puente entre el backend y el frontend.** Se acordó antes de escribir la
primera línea de lógica, y por eso los cuatro pueden trabajar en paralelo sin bloquearse.

La implementación viva está en [`api/lumen/contracts/`](../api/lumen/contracts/). Los ejemplos, en
[`fixtures/`](../fixtures/). Si este documento y el código se contradicen, manda el código — y
alguien tiene que arreglar este documento.

**Para cambiarlo:** lo anuncias en el chat del equipo **antes** de pushear y lo anotas en tu
handoff. Añadir un campo opcional es barato. Renombrar o quitar uno, no.

---

## Los nueve endpoints

| Método | Ruta | Entrada | Salida | Dueño |
|---|---|---|---|---|
| `POST` | `/resolver` | `{ texto }` | `Candidato[]` | Freddy · B2 |
| `POST` | `/analizar` | `{ nit? , entidad_id? , contrato_id? }` | `Caso` | Jonatin · B1 |
| `GET` | `/caso/{caso_id}` | — | `Caso` | Cristian · B3 |
| `POST` | `/justificacion` | PDF (multipart) o `{ url }` | `Lectura` | Freddy · B2 |
| `GET` | `/red/{nit}` | — | `Grafo` | Jonatin · B1 |
| `POST` | `/accion` | `{ caso_id, tipo }` | `Artefacto` | Freddy · B2 |
| `GET` | `/monitor/nuevos` | `?desde=`, `?forzar=` | `Caso[]` | Cristian · B3 |
| `POST` | `/alerta` | `{ caso_id, destinatario }` | `{ estado, detalle? }` | Cristian · B3 |
| `POST` | `/chat` | `{ mensaje, contexto? }` | `{ narracion, caso?, candidatos?, siguientes_pasos[] }` | Freddy · B2 |

Sobre `/monitor/nuevos`: un contrato ya visto **no desaparece de la respuesta**. Si su caso ya está
en base se devuelve tal cual, sin re-analizar ni repetir la alerta, para que la misma entidad se
pueda consultar las veces que haga falta. `?forzar=true` re-analiza desde cero — caro (~80-100 s
por entidad de cuota compartida de Croma), úsalo solo para refrescar un caso viejo.

Más dos de salud, que no son del contrato pero los vas a usar todo el rato:

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/health` | Responde sin tocar nada externo. Es el health check de Render |
| `GET` | `/health/croma` | Hace una llamada **real** a Croma y confirma que tu token funciona |

Documentación interactiva generada por FastAPI: `/docs`.

**`/chat` es la única ruta exclusiva del Modo Vigilancia**, y por dentro orquesta `/resolver` y
`/analizar`. No es un motor aparte. Si alguien empieza a escribir un segundo motor, se salió del
plan.

---

## El vocabulario compartido

| Objeto | Campos | Regla |
|---|---|---|
| `Candidato` | `nombre`, `nit?`, `ciudad?`, `actividad?`, `tipo` | Lo que devuelve la resolución de entidades para desambiguar |
| `Fuente` | `herramienta_croma`, `url_oficial`, `consultado_en` | **Obligatoria** dentro de toda señal y toda arista |
| `Senal` | `codigo`, `nombre`, `nivel`, `regla_legible`, `datos_usados`, `fuente` | `regla_legible` es texto que un ciudadano entiende, no la expresión de la regla |
| `PuntoLectura` | `pregunta`, `hallazgo`, `cita_textual?`, `pagina?`, `no_concluye_por?` | Si no hay cita, tiene que haber motivo |
| `Lectura` | `veredicto`, `puntos[]`, `documento_url?`, `analizado_en?` | Salida del lector de justificaciones |
| `Actor` | `id`, `tipo`, `nombre`, `nit?`, `rol?` | Nodo del grafo |
| `Arista` | `origen`, `destino`, `tipo`, `fuente` | |
| `Grafo` | `nodos[]`, `aristas[]` | Entre 5 y 12 nodos. Curado |
| `Caso` | `id`, `modo`, `entidad`, `proveedor?`, `municipio?`, `departamento?`, `valor?`, `objeto?`, `fecha?`, `nivel_atencion`, `senales[]`, `lectura?`, `grafo?`, `narracion?`, `disclaimer`, `generado_en?` | El objeto central. Todo gira alrededor de esto |
| `Artefacto` | `tipo`, `titulo`, `cuerpo_markdown`, `normas_citadas[]`, `destinatario?`, `caso_id?` | La capa de acción |

### Enums

- `nivel_atencion` y `Senal.nivel`: `bajo` · `medio` · `alto`
- `modo`: `emergencia` (lo encontró el monitor) · `vigilancia` (lo pidió una persona)
- `tipo` de actor y de candidato: `empresa` · `persona` · `entidad`
- `codigo` de señal: `S1` `S2` `S3` `S4` `S5` `S6` `S7` `S8` `S10` — S9 va al roadmap
- `veredicto`: `solida` · `generica` · `sin_relacion`
- `tipo` de artefacto: `paquete_evidencia` · `derecho_peticion` · `informe_veeduria` · `guia_denuncia`

---

## Los dos guardarraíles que viven en el tipo

No están en la documentación, están en el código, y hay pruebas que fallan si alguien los rompe.

**1. `Senal` no se puede construir sin `fuente`.** Si no hay fuente oficial con fecha de consulta, no
hay señal. El guardarraíl ético deja de depender de que alguien se acuerde a las tres de la mañana.

**2. `nivel_atencion` es un enum de tres valores.** No es un número, no es un porcentaje, no es un
score. Un "78 % de probabilidad de corrupción" es exactamente lo que este proyecto se niega a
publicar. Si aparece un float en ese campo, alguien rompió el producto.

Y uno que es convención pero cuenta igual: **si el lector de IA no puede citar el fragmento del
documento, no afirma.** Llena `no_concluye_por` y deja `cita_textual` vacío. El fixture
`lectura.json` muestra el caso a propósito, para que el frontend sepa pintarlo.

---

## Cómo lo verificas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

`api/tests/test_contrato.py` valida cada fixture contra los modelos y comprueba los guardarraíles.
`api/tests/test_app.py` comprueba que los nueve endpoints siguen registrados y que cada `501`
todavía dice de quién es. Si alguien renombra una ruta sin avisar, esto falla antes de la
integración y no durante.
