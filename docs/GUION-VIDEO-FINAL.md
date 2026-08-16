# Guion cronometrado — video final (60s, horizontal 16:9)

Todo en **1920×1080**. La demo se ve en PC.

**Leyenda de origen:** 🤖 lo genero yo con HyperFrames · 🎬 lo grabas tú · 🌎 el video de mapa que
generaste con IA

---

## Tabla de bloques

| # | Tiempo | Dur | Qué se ve | Narración (texto exacto) | Origen |
|---|---|---|---|---|---|
| 1 | 0:00–0:06 | 6s | Negro. Dos frases en serif, una tras otra: **"Llega la plata para reconstruir."** → **"¿Quién está mirando?"** | *(silencio — deja que el texto pese)* | 🤖 |
| 2 | 0:06–0:14 | 8s | Mapa de Colombia, zoom al Pacífico. Aparecen las 4 entidades con su cifra real | "Después de un desastre, el Estado contrata sin concurso, para ir rápido. La revisión llega un año después, cuando la plata ya se gastó." | 🌎 + 🤖 |
| 3 | 0:14–0:22 | 8s | Teléfono: llega la alerta de Telegram con el caso del Chocó | "Lumen vigila solo. Cuando encuentra algo que vale la pena mirar, le avisa a la veedora del municipio." | 🎬 |
| 4 | 0:22–0:32 | 10s | Abre el enlace → la ficha del caso real en la plataforma. Señal, cifra, fuente oficial, disclaimer | "Le muestra qué encontró, en español, con el dato y el enlace a la fuente oficial." | 🎬 |
| 5 | 0:32–0:50 | 18s | **El chat.** Se adjunta el PDF de la resolución → el lector responde con veredicto y las tres citas subrayadas | "Y lee el documento que justifica la urgencia. Verifica, una por una, si de verdad se conecta con el desastre — y cita el texto exacto que lo prueba." | 🎬 |
| 6 | 0:50–1:00 | 10s | Logo + "Funciona para cualquier declaratoria de desastre" + "No acusamos. Ayudamos a preguntar." | "Funciona para cualquier desastre. La ventana del sismo dura doce meses; el problema, siempre. No acusamos: ayudamos a preguntar." | 🤖 |

**Total: 60s exactos.**

---

## Por qué está repartido así

El bloque 5 (el lector de IA) es **el más largo del video, 18 segundos**, y no es capricho:
"Uso real de IA" son 25 puntos de la rúbrica, el criterio de mayor peso junto con impacto. Es lo
único que ninguna plataforma de datos abiertos hace — leer el documento legal y verificar cita
por cita.

Los bloques 3, 4 y 5 son grabación real de la app funcionando: ahí se juegan los 20 puntos de
"Demo funcional" y los 15 de "Ejecución técnica + UX".

---

## Lo que grabas tú — paso a paso

Graba **todo en la app de producción**, no en local: se ve mejor y prueba que está desplegada.
Ventana del navegador **maximizada, sin barra de marcadores, sin pestañas de más**.
En macOS: `Cmd+Shift+5` → "Grabar porción seleccionada" o pantalla completa. Guarda los archivos
en `video/edicion/02-grabaciones/`.

### 🎬 A — `telegram.mp4` (bloque 3, graba ~12s)
En el celular (Android): panel rápido → Grabadora de pantalla.
1. Deja en el chat **solo** el `/start` y la alerta del sismo (borra el "hola").
2. Empieza a grabar con el chat abierto.
3. Que se vea el mensaje completo sin prisa. Un scroll mínimo con el pulgar evita que se sienta
   una foto quieta.

### 🎬 B — `ficha.mp4` (bloque 4, graba ~14s)
```
https://lumen-a1y.pages.dev/app/caso/caso-0d6968f81dad
```
Baja despacio: nivel de atención → la señal en lenguaje ciudadano ("97 contratos parecidos…") →
la línea de fuente oficial → el disclaimer. **Que se vea el enlace a la fuente**: eso es lo que
hace que el jurado te crea.

### 🎬 C — `chat-lector.mp4` (bloque 5, graba ~25s) ← el más importante
```
https://lumen-a1y.pages.dev/app/vigilancia
```
1. Clic en el botón de adjuntar (📎).
2. Selecciona `video/produccion/justificacion-chocó.pdf` (está en esta misma rama).
3. **Deja correr la espera** — que se vea que está leyendo de verdad.
4. Cuando salga el veredicto, baja despacio por los tres puntos. **Detente en las citas
   textuales**: ese es el momento que vale los 25 puntos.

Si la generación tarda mucho, no la cortes: yo acelero esa parte en el montaje.

---

## Lo que genero yo

- **Bloque 1** (hook) y **bloque 6** (cierre): los rehago en horizontal 1920×1080.
- **Bloque 2**: me pasas tu video del mapa, lo pones en
  `video/edicion/02-grabaciones/mapa-colombia.mp4`, y yo le sobrepongo encima los nombres y las
  cifras reales, sincronizados con el zoom:

  | Entidad | Cifra real |
  |---|---|
  | Chocó | 97 contratos |
  | Valle del Cauca | 40 contratos |
  | Buenaventura | 25 contratos |
  | Cali | *(sin cifra — su barrido no disparó señal, y no se inventa una)* |

- **Subtítulos quemados** sobre todo el video.
- **Ensamblaje final** con ffmpeg: los 6 bloques + narración + música.

---

## Alternativa al mapa, si el video generado no convence

Tu idea de "fotos de cada departamento con su cifra" funciona igual de bien y es más honesta
visualmente: cuatro tarjetas a pantalla completa, una por entidad, cada una con el nombre y su
cifra real, entrando en cascada. Lo genero yo con HyperFrames en 10 minutos si decides eso. Dime
cuál prefieres cuando veas tu clip.

---

## Audio

**Narración:** los 5 parlamentos de la tabla, en orden. Si usas ElevenLabs, genera uno por
bloque (más fácil de encajar que una sola toma) y ponlos en `video/edicion/03-audio/` como
`voz-2.mp3`, `voz-3.mp3`, `voz-4.mp3`, `voz-5.mp3`, `voz-6.mp3`. El bloque 1 va en silencio.

**Música:** la cama de fondo en `video/edicion/03-audio/musica.mp3`. Yo la bajo de volumen bajo
la voz en el montaje.

**Tono:** tranquilo, sobrio. Hay 288 muertos y esto pasó hace seis días — nada de locución de
comercial.
