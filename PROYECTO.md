# PROYECTO.md — Lumen

**Hackathon CTW 2026 · Track 01: Tecnología para la Transparencia**
Sede: Universidad del Rosario, Claustro, Bogotá · Deadline: **domingo 16.ago 09:00**, sin prórroga.

> **Documento fuente:** [`docs/brief-final-claude.md`](docs/brief-final-claude.md) — une el v3, el
> parche v3.1 y las decisiones del equipo. Los archivos `brief_v3_lumen_ctw2026.md` y
> `patch_v3.1_lumen_usuario_y_pitch.md` quedan como histórico.
>
> Este archivo es el resumen operativo: qué construimos, qué está congelado y qué está fuera. Si hay
> contradicción, **manda este**, porque recoge el corte vivo. Si este contradice al brief final, hay
> que arreglar este.

---

## Para quién es (v3.1 — esto cambió)

**Usuario primario: el veedor.** La persona que ya hace esto. Veedurías ciudadanas, juntas de acción
comunal, periodistas locales, concejales de oposición, líderes comunitarios, docentes y jubilados
que le siguen la pista a la obra del pueblo.

El v3 decía que el producto servía "al ciudadano que no sabe qué es SECOP". **Ese usuario no existe
como usuario activo:** no va a abrir una herramienta de contratación pública un martes. Lo corrigió
una mentora en gestión de riesgo de desastres, que además es veedora:

> *"Una persona cualquiera ni sabrá qué decirle a la herramienta o cómo usarla. Enfóquenlo en las
> personas que de por sí ya se dedican a revisar todo eso, para facilitarles las cosas."*

**No le enseñamos a vigilar. Le quitamos el trabajo manual.** Hoy, verificar un solo contrato le
cuesta a esa persona horas de navegar SECOP, RUES y sanciones por separado. Lumen se lo entrega
resuelto en segundos, con la evidencia y la carta lista.

**El dato que cambia el diseño:** el veedor suele ser una persona mayor, no un joven con Python. Es
la mamá, la tía, el jubilado del barrio — que están más pendientes de estas cosas que la mayoría de
los jóvenes.

**Y de ahí sale la justificación de WhatsApp, que hay que decir en el pitch:** no es un truco de
distribución. Es la única interfaz que nuestro usuario real ya usa todos los días, sin instalar
nada, sin crear cuenta y sin aprender un dashboard.

**El acceso sigue siendo público y gratuito.** Enfocar el producto en el veedor no le cierra la
puerta a nadie: define para quién se diseña la experiencia. Un producto para todos no es usable por
nadie.

---

## Qué es Lumen

Un sistema de vigilancia sobre la plata pública, encendido sobre la reconstrucción del terremoto del
10 de agosto de 2026. **Un motor, dos modos.**

**Modo Emergencia (push — el hook).** Corre solo. Revisa los contratos nuevos que entran por el
régimen excepcional de emergencia, lee las justificaciones que la ley exige, detecta patrones que
merecen revisión y le avisa por WhatsApp a la veedora del municipio afectado — con la evidencia y
con la carta lista para enviar.

**Modo Vigilancia (pull — el que lo hace durar).** El mismo motor con el disparador invertido: **es
la mesa de trabajo del veedor.** El push le trae lo que no sabía que existía; el pull le sirve para
lo que ya está investigando por su cuenta — la obra del colegio, la empresa que vio en la valla, el
contratista que le suena. Escribe en lenguaje natural y recibe la red de actores, las señales con su
evidencia y el artefacto para actuar.

**Pitch:** *"El control de la plata de la reconstrucción es posterior. Nosotros lo hacemos hoy."*

**Frase de seguridad, se repite siempre y sale en el video:**
> *"No acusamos. Ayudamos a preguntar."*

**El dolor, una frase por modo (v3.1):**
> *Emergencia:* "Soy veedora de mi municipio. Va a llegar plata para reconstruir y yo me entero de
> los contratos cuando ya se firmaron — si me entero."
> *Vigilancia:* "Sé qué quiero revisar. Lo que no tengo son las ocho horas que me cuesta cruzar
> SECOP con el RUES y las sanciones, contrato por contrato."

---

## Cómo se gana (rúbrica oficial del deck, sobre 100)

| Criterio | Puntos | Qué lo defiende en nuestro caso |
|---|---|---|
| **Impacto público** | 25 | 448 municipios, 12 meses de contratación directa, control posterior. El problema es real y está pasando ahora |
| **Uso real de IA** | 25 | El lector de justificaciones de urgencia manifiesta: análisis semántico de documento libre contra un estándar legal. Ninguna regla SQL lo hace |
| **Demo funcional** | 20 | El video de 60 s con el flujo end-to-end corriendo de verdad |
| **Viabilidad + escala** | 15 | Compradores nombrados (multilaterales, filantropía cívica, medios) + agnóstico al desastre |
| **Ejecución técnica + UX** | 15 | Código legible, arquitectura declarada, fuentes citadas, UI clara |

Premio: USD 4.000 al primer puesto. Entrega: video de máximo 1 minuto + código al repositorio
oficial. **No hay pitch en vivo.**

**Consecuencia práctica:** el video no es el último entregable, es el vehículo de 70 de los 100
puntos. Impacto, IA y demo solo se ven ahí. Si algo no cabe en 60 segundos, no se construye hoy.

---

## Lo que está DENTRO del corte

- Motor de **8 señales** deterministas (S1–S8, S10) sobre datos de Croma, cada una con su regla
  legible, su dato y su fuente oficial con fecha de consulta.
- **Lector IA de justificaciones** de urgencia manifiesta, con veredicto de tres niveles y cita
  textual. Es la feature estrella.
- **Resolución de entidades** desde lenguaje natural, con desambiguación por candidatos.
- **Narración en lenguaje ciudadano** de los hallazgos, con los textos únicos de
  [`docs/COPY-SENALES.md`](docs/COPY-SENALES.md).
- **La carta para preguntarle a la alcaldía** (un derecho de petición), generada a partir del
  hallazgo específico. En la interfaz se llama carta; el documento sí cita la norma.
- **Paquete de evidencia** (sale casi gratis: los datos ya están calculados).
- **Grafo de actores** curado, de 5 a 12 nodos.
- **Monitor** que despierta, filtra novedad y arma casos.
- **Alerta de WhatsApp** — sujeta a que resolvamos Twilio.
- **Catálogo curado de 6 casos** validados a mano: Metro de Bogotá, Ruta del Sol, Centros Poblados,
  UNGRD 2024, Mocoa 2017, Providencia post-Iota 2020.
- Las cuatro pantallas del frontend: alerta, ficha del caso, chat y artefacto.

## Lo que está FUERA (congelado, no se reabre)

- **S9, adiciones significativas.** Depende de que el dato de modificaciones exista. Va al roadmap.
- **MCP server propio.** Es el diferenciador que más nos emociona y el que menos se ve en 60
  segundos. Va al README y al roadmap. **No se toca** hasta que el flujo end-to-end corra y exista
  el primer corte del video.
- **Informe de veeduría y guía de denuncia.** Solo si sobra reloj. Son el hard-cut #1.
- **Nómina, sueldos, antecedentes penales, salud, estado de cédula.** Fuera del alcance aunque
  Croma los exponga. Multiplica el riesgo y no aporta.
- **Slides, deck o pitch aparte.** El evento no los pide y no los vamos a hacer.
- **Plan B de datos con Socrata.** Croma es fuente única y ya está verificada.

## Orden exacto de hard-cuts si el reloj aprieta

1. Informe de veeduría y guía de denuncia
2. Grafo de actores visual → se sustituye por lista de vínculos
3. Twilio → se muestra la plataforma en vez del WhatsApp real
4. Modo Vigilancia en el video → se queda en la plataforma y el README

> **⚠️ El puesto 3 ya no es un corte barato, y así se resolvió (19:30).** El Parche 1 convierte
> WhatsApp en *"la única interfaz que nuestro usuario real ya usa todos los días"* y el storyboard le
> dedica 11 de los 60 segundos. Cortarlo destriparía el argumento central, así que Twilio **sube a
> prioridad 1 del bloque de Cristian de las 20:45**, con cuenta creada ya y timebox duro de 60
> minutos.
>
> **Corte a las 21:45.** Si a esa hora no llegó un mensaje real a un teléfono real, se aplica el
> corte y hay una consecuencia que no se descubre a las dos de la mañana: **el bloque 0:15–0:26 del
> storyboard hay que reescribirlo**, porque la alerta se vería como notificación dentro de la
> plataforma. Eso cae en las manos de Jonatin justo cuando arranca el video, a las 22:00. Y sigue
> valiendo la regla de siempre: **no se mockea un WhatsApp falso.**

---

## Decisiones tomadas hoy que corrigen el brief

| # | Decisión | Reemplaza a |
|---|---|---|
| 1 | **El equipo son 4 personas y Jonatin es B1.** El brief §10 listaba 5 filas para 4 personas | §10 del brief |
| 2 | **Todo el stack del frontend lo decide Andrew.** React, Vite, Tailwind, Cloudflare Pages: nada de eso está impuesto. `web/` se entrega vacía y él elige | §5 del brief (fila Frontend) |
| 3 | **Croma es un servidor MCP remoto**, no una API REST. Verificado en vivo: stateless, un POST JSON-RPC basta. El backend en Render puede llamarlo | §5 del brief (no lo especificaba) |
| 4 | **El despliegue se monta hoy temprano**, no a las 03:30 | §11 del brief |
| 5 | **Twilio sube a prioridad 1 de B3** a las 20:45, con timebox de 60 min y corte a las 21:45. Ya no es un hard-cut barato: es la tesis del producto | §5 del brief y hard-cut #3 |
| 6 | **HeyGen descartado.** Bonus menor, no compensa el tiempo | §8 del brief |
| 7 | **Usuario primario = el veedor**, no "el ciudadano que no sabe qué es SECOP" | Parche 1 del v3.1 |
| 8 | **Storyboard nuevo del video:** sin leyes, sin cifras de dólares, con protagonista | Parche 2 del v3.1 |
| 9 | **Las 8 señales se dicen en lenguaje ciudadano.** Textos únicos en [`docs/COPY-SENALES.md`](docs/COPY-SENALES.md) | Parche 3 del v3.1 |

---

## Guardarraíles (no negociables, valen puntos y valen reputación)

1. **Señales, no acusaciones.** Nunca "X es corrupto". Siempre "patrón que merece revisión".
2. **Disclaimer visible en cada resultado**, no en un footer:
   *"Una señal no es prueba de irregularidad. Es un motivo para preguntar."*
3. **Solo fuentes oficiales**, siempre enlazadas, con fecha de consulta.
4. **`Senal` no se puede construir sin `fuente`.** El guardarraíl vive en el tipo, no en la
   documentación, para que no dependa de que alguien se acuerde.
5. **`nivel_atencion` es un enum de tres valores**, nunca un número ni un porcentaje ni un score.
   Si aparece un float en ese campo, alguien rompió el producto.
6. **El lector de IA nunca afirma sin citar.** Si no puede citar el fragmento, dice que no concluye.
7. **No exponer datos sensibles de personas.** El análisis es sobre empresas y contratos. Las
   personas aparecen solo en su rol público de representante legal y solo con registro mercantil.
8. **Tono sobrio.** Hay 288 muertos y esto pasó hace cinco días. Nada de estética de thriller.
9. **Declarar Croma abiertamente** en el video, en el README y en cualquier respuesta al jurado.
10. **Respetar los términos de Croma.** No republicamos bases: publicamos hallazgos con enlace a la
    fuente.

---

## Riesgo número uno, y hay que verificarlo hoy

**Los contratos del sismo casi no existen todavía en SECOP: llevamos cinco días.** Si la demo
depende de encontrar un contrato sospechoso del sismo, el video sale vacío.

Se resuelve en tres capas, y las tres van en el video:

1. **Lo que ya existe.** Un barrido de lo poco que haya entrado desde el 11 de agosto. Aunque salga
   limpio sirve: demuestra que el monitor está vivo desde el día uno.
2. **El análogo histórico.** Correr el motor sobre contratación de emergencia pasada (Mocoa 2017,
   Providencia post-Iota 2020, UNGRD 2024) y mostrar que detecta los patrones que después
   resultaron ser escándalos. *"Esto es lo que habríamos visto en tiempo real, en vez de en la
   Contraloría cuatro años después."*
3. **El lector de justificaciones sobre documentos reales** de urgencia manifiesta que ya se están
   publicando, como el Acuerdo PCSJA26-12569 de la Rama Judicial.

**Dueño de la verificación: Jonatin (B1). Hora límite: 20:00 de hoy.** Si la capa 2 no da, hay que
saberlo esta noche, no a las cuatro de la mañana.
