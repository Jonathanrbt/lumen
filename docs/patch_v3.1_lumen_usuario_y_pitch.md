> **Supersedido.** El documento vivo es [`brief-final-claude.md`](brief-final-claude.md). Este archivo se conserva como archivo del parche v3.1.

# LUMEN — Parche v3.1

**Qué es esto:** tres reemplazos sobre el brief v3, a partir del feedback de la mentora en gestión de riesgo de desastres (15.ago, ~17:00). No cambia el alcance, el stack, los roles ni el cronograma. **Cambia para quién es y cómo se cuenta.**

**Qué NO toca:** §5 (stack), §10 (roles), §11 (cronograma), §16 (guardarraíles). Todo eso sigue igual.

---

## PARCHE 1 — Reemplaza la definición de usuario (§1, §2, §4.5)

### El feedback textual

> "Está bien, hasta yo lo usaría. Pero hay que enfocarlo en personas que se dediquen a la veeduría, como yo misma. Obviamente es de acceso público, pero **una persona cualquiera ni sabrá qué decirle a la herramienta o cómo usarla**. Enfóquenlo en las personas que de por sí ya se dedican a revisar todo eso, para facilitarles las cosas."

### La corrección

El v3 justificaba el Modo Vigilancia diciendo que sirve "al ciudadano que no sabe qué es SECOP". **Ese usuario no existe como usuario activo.** No va a abrir una herramienta de contratación pública un martes.

**Usuario primario: el veedor.** La persona que ya hace esto. Veedurías ciudadanas, juntas de acción comunal, periodistas locales, concejales de oposición, líderes comunitarios, docentes y jubilados que le siguen la pista a la obra del pueblo.

**No le enseñamos a vigilar. Le quitamos el trabajo manual.** Hoy, verificar un solo contrato le cuesta a esa persona horas de navegar SECOP, RUES y sanciones por separado. Lumen se lo entrega resuelto en segundos, con la evidencia y la carta lista.

**El dato que cambia el diseño:** el veedor suele ser una persona mayor, no un joven con Python. Es la mamá, la tía, el jubilado del barrio — que están **más pendientes** de estas cosas que la mayoría de los jóvenes.

**Consecuencia directa, y hay que decirla en el pitch:** por eso el canal es WhatsApp. No es un truco de distribución. Es la única interfaz que nuestro usuario real ya usa todos los días, sin instalar nada, sin crear cuenta, sin aprender un dashboard.

### Reemplazo de las frases de dolor (§2)

> *Emergencia:* "Soy veedora de mi municipio. Va a llegar plata para reconstruir y yo me entero de los contratos cuando ya se firmaron — si me entero."
> *Vigilancia:* "Sé qué quiero revisar. Lo que no tengo son las ocho horas que me cuesta cruzar SECOP con el RUES y las sanciones, contrato por contrato."

### Reemplazo de la justificación del Modo Vigilancia (§4.5)

**Antes (incorrecto):** "es lo que hace que la herramienta sirva al ciudadano que no sabe qué es SECOP."

**Ahora:** el Modo Vigilancia es **la mesa de trabajo del veedor**. El push le trae lo que no sabía que existía; el pull le sirve para lo que ya está investigando por su cuenta — la obra del colegio, la empresa que vio en la valla, el contratista que le suena. Es el mismo motor con el disparador invertido.

**El acceso sigue siendo público y gratuito.** Enfocar el producto en el veedor no cierra la puerta a nadie: define para quién se diseña la experiencia. Un producto para todos no es usable por nadie.

---

## PARCHE 2 — Reemplaza el storyboard completo (§8)

### El feedback textual

> "Que el pitch y la solución se presenten de forma más estética, más vendible. No mencionar tantas leyes ni esas cosas, sino algo más aterrizado. **Preséntenlo como si se lo estuvieras mostrando a tu abuela o a tu mamá.**"

### La regla

**Las leyes no se borran: se mudan.** El Decreto 1171, el artículo 46, el Acuerdo PCSJA26-12569 y las cifras de la UNGRD siguen íntegros en el README y en §15 (objeciones), donde le dan credibilidad ante un jurado que pregunta. **Fuera del video.**

Test antes de grabar: si tu mamá no entiende los primeros siete segundos, se regraba.

### Storyboard v3.1

| Tiempo | Qué se ve | Qué se oye |
|---|---|---|
| 0:00–0:07 | Negro. Texto grande, en dos tiempos: **"Llega la plata para reconstruir."** → **"¿Quién está mirando?"** | Silencio, o un solo golpe de sonido |
| 0:07–0:15 | Mapa de los municipios afectados. Texto en pantalla: *"Los contratos se firman rápido. Sin concurso."* | "Después de un desastre, el Estado puede contratar sin concurso, para ir rápido. La revisión llega un año después, cuando la plata ya se gastó." |
| 0:15–0:26 | **Un teléfono. Llega el WhatsApp.** Se lee la alerta completa, sin prisa | "Ella es veedora de su municipio. Lumen le avisa cuando se firma un contrato que vale la pena mirar." |
| 0:26–0:38 | Abre el enlace → la ficha. Señales en lenguaje simple, una debajo de otra. **Zoom al lector de IA:** *"El documento que justifica la urgencia no menciona ningún daño del terremoto."* | "Le dice qué encontró, en español, con la prueba y el enlace a la fuente oficial." |
| 0:38–0:47 | Botón → la carta redactándose sola | "Y le redacta la carta para preguntarle a la alcaldía. Ella la firma y la manda." |
| 0:47–0:55 | Chat: se escribe *"¿la alcaldía de mi pueblo tiene algo raro?"* y salen las señales con su fuente | "Cuando pase el terremoto, Lumen sigue. Porque la plata pública se vigila todos los días." |
| 0:55–1:00 | Logo + frase en texto | "No acusamos. Ayudamos a preguntar." |

### Qué cambió y por qué

| Antes (v3) | Ahora (v3.1) | Razón |
|---|---|---|
| "US$450.000.000. Sin licitación. Control posterior." | "Llega la plata para reconstruir. ¿Quién está mirando?" | La cifra impresiona a un economista. La pregunta le llega a cualquiera |
| "El 11 de agosto Colombia habilitó contratación directa por 12 meses" | "El Estado puede contratar sin concurso, para ir rápido" | Misma información, sin fecha ni decreto |
| "La ley exige que la justificación tenga relación verificable con el sismo" | "El documento que justifica la urgencia no menciona ningún daño del terremoto" | Se muestra el hallazgo en vez de explicar la norma. Más corto y más fuerte |
| "Derecho de petición" | "La carta para preguntarle a la alcaldía" | Nadie fuera del derecho sabe qué es un derecho de petición. En la UI puede decir ambas |
| Usuario sin rostro | "Ella es veedora de su municipio" | Un producto con usuario se recuerda; una plataforma no |

**Se conserva sin cambios:** las reglas de producción (grabar a tamaño de teléfono y hacer zoom, una tipografía, subtítulos quemados, respaldo grabado temprano) y los tiempos de cada bloque.

---

## PARCHE 3 — Nuevo: traducción de las 8 señales a lenguaje ciudadano

**Esto es UI, no es copy bonito.** Es lo que separa una herramienta que un veedor de 60 años usa de un dashboard que abandona en treinta segundos. Va en las tarjetas de la ficha (§9, pantalla 2), en el mensaje de WhatsApp y en el video.

| # | Lo que dice el sistema hoy | Lo que debe decir |
|---|---|---|
| S1 | Proveedor constituido < 365 días antes de la adjudicación | **"Esta empresa se creó hace 2 meses y ya ganó un contrato de $X."** |
| S2 | Representante legal compartido entre proveedores de la misma entidad | **"Estas dos empresas tienen el mismo representante. Se presentaron al mismo proceso."** |
| S3 | Proveedor con sanción vigente y contratos posteriores | **"Esta empresa tiene una sanción vigente y le siguieron adjudicando contratos."** |
| S4 | Valor del contrato > ingresos anuales reportados | **"Esta empresa nunca ha reportado ingresos de este tamaño. El contrato es más grande que toda su facturación de un año."** |
| S5 | Proceso de insolvencia activo con adjudicaciones vigentes | **"Esta empresa está en proceso de insolvencia. Si quiebra, la obra queda a medias."** |
| S6 | Fraccionamiento: contratos de objeto similar bajo umbral | **"Se firmaron 3 contratos parecidos, casi el mismo día, cada uno justo por debajo del monto que obliga a hacer concurso."** |
| S7/S8 | Índice de concentración por proveedor | **"Dos empresas se llevaron el 61% de toda la plata de esta entidad."** |
| S10 | Registro en BDME con contratos activos | **"Esta empresa le debe plata al Estado, y el Estado le sigue adjudicando contratos."** |
| Lector IA | Veredicto: sin relación aparente con el hecho generador | **"El documento que explica por qué era urgente no menciona ningún daño del terremoto."** |

**Reglas de copy:**
- Frases de máximo 20 palabras. Sujeto, verbo, cifra.
- Cero siglas sin explicar: nunca "BDME", "RUES", "SECOP" solos en una tarjeta visible.
- La cifra siempre en pesos redondeados, nunca en notación técnica ni en porcentajes de índice.
- El enlace a la fuente oficial va debajo de cada frase, en letra pequeña, siempre. Eso no se simplifica: es lo que hace que el hallazgo sea verificable.
- **El disclaimer no cambia de registro:** *"Una señal no es prueba de irregularidad. Es un motivo para preguntar."*

---

## Nota de reconocimiento

La mentora validó el problema y corrigió el usuario. Si aporta algo más antes del cierre, vale la pena agradecerle en el README (con su permiso y su nombre si lo autoriza). Un proyecto de veeduría que reconoce a la veedora que lo corrigió dice algo sobre cómo trabaja el equipo — y el jurado lo lee.

---

## Guard adicional al cronograma (§11)

A las 22:00 Jonatin pasa a ser dueño del video. El hito crítico es a las 23:00. **Designar ahora, por nombre, quién es dueño del hito de las 23:00** — no a las 23:05. Es la única hora del reloj sin dueño explícito.
