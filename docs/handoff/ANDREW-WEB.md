# Handoff — Andrew · UI/UX

**Soy dueño de:** `web/`, entera. **Y de las decisiones de tecnología del frontend.**
Framework, bundler, estilos, librería de grafo, hosting: lo elijo yo. La carpeta se entregó vacía a
propósito. Ningún backend entra aquí ni me sugiere librerías.

**Mis hitos:** 22:00 las 4 pantallas navegables contra fixtures · 02:00 integradas contra la API
real.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

---

## 19:20 — Qué me cambió el v3.1

Lo corrigió una mentora en gestión de riesgo de desastres que además es veedora, y me cambia para
quién diseño. No cambia las cuatro pantallas ni mi stack.

### Ya no diseño para "cualquier ciudadano". Diseño para el veedor

> *"Una persona cualquiera ni sabrá qué decirle a la herramienta o cómo usarla. Enfóquenlo en las
> personas que de por sí ya se dedican a revisar todo eso, para facilitarles las cosas."*

Es la persona que ya hace veeduría: juntas de acción comunal, periodistas locales, concejales de
oposición, líderes comunitarios, docentes y jubilados que le siguen la pista a la obra del pueblo.

**Y el dato que cambia el diseño de verdad: suele ser una persona mayor.** Es la mamá, la tía, el
jubilado del barrio. No es un joven con Python.

Lo que eso significa para la interfaz, y no es cosmética:

- **Tipografía grande y contraste alto.** No diseñes para tu vista de 25 años.
- **Áreas táctiles generosas.** Se va a usar desde un teléfono, con el pulgar.
- **Un camino, no un menú.** Ella no va a explorar la herramienta: llega desde un enlace de
  WhatsApp, con una pregunta concreta.
- **Cero jerga en pantalla.** Ninguna sigla suelta.

No es que no sepa vigilar: sabe más que nosotros. Lo que no tiene son las ocho horas que cuesta
cruzar SECOP con el RUES contrato por contrato. **Le quitamos el trabajo manual, no la enseñamos.**

### El copy de las tarjetas ya está escrito, y es fuente única

Las nueve frases de señal están en **[`docs/COPY-SENALES.md`](../COPY-SENALES.md)**. Vienen del
backend en el campo `regla_legible`, así que **no las reescribas en el frontend**: si tú maquillas el
texto y B1 cambia el suyo, quedan dos versiones. Si alguna frase no te cabe o no se lee bien, dilo y
la cambiamos en el origen.

Las reglas que sí son tuyas al pintarlas: máximo 20 palabras por frase, cifras en pesos redondeados,
y **el enlace a la fuente oficial debajo de cada frase en letra pequeña, siempre**. Eso no se
simplifica nunca: es lo que hace que el hallazgo sea verificable.

### Tres cambios concretos de texto

| Antes | Ahora |
|---|---|
| Disclaimer: *"Herramienta de priorización ciudadana. Una señal no es prueba de irregularidad."* | *"Una señal no es prueba de irregularidad. **Es un motivo para preguntar.**"* |
| Botón: "Generar derecho de petición" | **"Carta para la alcaldía"** — y si quieres, con el término legal pequeño al lado |
| "Nivel de atención: alto" | Puedes decir **"Vale la pena mirar esto"**. Sigue siendo el enum de tres estados con color, nunca un número |

Los fixtures ya están actualizados con estos textos, así que lo que maquetes contra ellos ya es el
copy bueno.

**El test antes de dar una pantalla por buena: si tu mamá no la entiende, se rehace.**

---

## Lo único que necesito del backend, y ya está en el repo

**El contrato de la API:** [`docs/CONTRATO-API.md`](../CONTRATO-API.md), con los nueve endpoints, sus
entradas y sus salidas.

**Un JSON de ejemplo por endpoint** en [`fixtures/`](../../fixtures/). **Construye contra esto desde
el minuto uno y no esperes a nadie.** Los fixtures son válidos contra los modelos del backend: si
tu pantalla funciona con el fixture, funciona con la API real.

**La URL base de la API** llega cuando Cristian despliegue en Render, antes de las 19:00. Hasta
entonces, `http://127.0.0.1:8000` si quieres levantarlo local, o los fixtures directamente.

**Avísale a Cristian el dominio donde despliegues** en cuanto lo sepas, para que lo meta en CORS. Si
esto se descubre a las 02:00, se pierden treinta minutos justo en la integración.

Si algo del contrato no te sirve para construir la pantalla, **dilo ahora**, en el bloque de
arranque. Cambiarlo a las 17:45 es gratis; a las 23:00 cuesta dos horas.

---

## Las cuatro pantallas. Nada más

1. **La alerta de WhatsApp.** Copy en lenguaje ciudadano, máximo 5 líneas. *"El 61 % del valor se
   concentró en 2 empresas"*, nunca *"índice Herfindahl 0,61"*.
2. **La ficha del caso.** Arriba municipio, valor, entidad y nivel de atención. En el centro las
   señales como tarjetas, cada una con su regla legible, su dato y su enlace oficial con fecha de
   consulta. Abajo el subgrafo de actores. **Un solo scroll.**
3. **El chat del Modo Vigilancia.** Entrada libre, los candidatos de desambiguación como tarjetas
   clicables, y la respuesta narrada usando **las mismas tarjetas de señal de la pantalla 2**. No es
   una pantalla nueva: es un envoltorio distinto sobre los mismos componentes.
4. **La carta.** El derecho de petición generándose, con botón de copiar y de descargar. En pantalla
   se llama *"la carta para preguntarle a la alcaldía"*; dentro del documento sí van las normas
   citadas.

## Reglas de diseño que no se negocian

- **El nivel de atención son tres estados con color**, nunca un score numérico. Si aparece un
  porcentaje de "probabilidad de corrupción" en una pantalla, rompimos el producto.
- **Disclaimer visible en cada resultado**, no en el pie de página:
  *"Una señal no es prueba de irregularidad. Es un motivo para preguntar."*
- **Cada dato con enlace a la fuente oficial y su fecha de consulta.** Eso no es solo ética: es lo
  que hace que el jurado te crea.
- **El grafo, curado y pequeño**, entre 5 y 12 nodos. Un hairball es peor que no mostrar grafo.
- Nada de copy que suene a IA.

## Y esto define el diseño más que cualquier otra cosa

**El jurado ve un video de 60 segundos, pequeño, probablemente sin audio.** Se graba a tamaño de
teléfono real y con zoom. Un dashboard a todo lo ancho es ilegible ahí. **Diseña para que se lea en
una pantalla de teléfono, no para que luzca en tu monitor.**

Si el reloj aprieta, el orden de sacrificio es: el grafo visual se sustituye por una lista de
vínculos antes que cualquier otra cosa de la interfaz.

---

## Bitácora

### 17:30 — Punto de partida

`web/` vacía. Contrato y fixtures disponibles. Sin decisiones de stack tomadas por nadie más que yo.
