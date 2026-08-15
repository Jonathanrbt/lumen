# fixtures/

Un JSON de ejemplo por endpoint. **Existen para que nadie espere a nadie.**

Andrew construye el frontend contra esto desde el minuto uno, sin esperar a que el backend esté
listo. B1, B2 y B3 trabajan en paralelo sabiendo exactamente qué tienen que devolver.

## Los valores son ilustrativos. La estructura es real

Ningún dato de estos archivos puede aparecer en el video ni en la demo. Son maniquíes para maquetar.
Lo que se grabe sale del motor corriendo contra Croma, con fuentes oficiales y fechas de consulta
reales. Eso no es un detalle de estilo: **"cero mock" es una regla del proyecto** y un falso dato en
el video nos cuesta la credibilidad delante del jurado.

La estructura sí es de fiar: `api/tests/test_contrato.py` valida cada fixture contra los modelos
Pydantic. Si un fixture miente, la prueba falla.

## Qué hay aquí

| Archivo | Endpoint | Qué muestra |
|---|---|---|
| `caso.json` | `POST /analizar`, `GET /caso/{id}` | El objeto central, completo: señales, lectura, grafo y narración |
| `candidatos.json` | `POST /resolver` | Los candidatos para desambiguar |
| `lectura.json` | `POST /justificacion` | El veredicto del lector. **Mira el tercer punto:** cuando el modelo no puede citar, no afirma |
| `artefacto.json` | `POST /accion` | El derecho de petición, en markdown |
| `chat_desambiguacion.json` | `POST /chat` | Cuando hay varios candidatos y elige la persona |
| `chat_respuesta.json` | `POST /chat` | Cuando ya hay análisis. El `caso` es el mismo objeto de `caso.json` |
| `alerta.json` | `POST /alerta` | Resultado del envío |
| `casos_demo.json` | — | **Respaldo de grabación.** Lo genera Cristian con los 6 casos reales precomputados |

`monitor/nuevos` devuelve una lista de casos: la estructura de cada elemento es la de `caso.json`.

## El respaldo de grabación

`casos_demo.json` todavía no existe: lo genera Cristian (B3) precomputando los 6 casos del catálogo
curado. Con `LUMEN_USAR_DUMP_LOCAL=true` la API responde desde ahí sin tocar Supabase ni Croma.

Existe por una razón concreta: si a las 07:00 de la mañana se cae la red del campus mientras
grabamos, la demo sigue viva. No es la arquitectura, es un paracaídas.

## Si el contrato cambia

Lo anuncias en el chat del equipo **antes** de pushear, actualizas el fixture y lo anotas en tu
handoff. Un cambio silencioso de esquema a las 23:00 cuesta dos horas de depuración a las 23:30.
