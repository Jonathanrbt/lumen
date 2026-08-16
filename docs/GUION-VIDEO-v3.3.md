# Guion del video — v3.3 (el que se graba)

Sucede a `GUION-VIDEO-v3.2.md`. Los cambios de esta versión salen de verificar el **código real**
de `origin/main` y de probar cada pieza en vivo, no de suponer.

**Contexto:** no hay pitch presencial. El jurado solo ve el video — tiene que venderse solo.

---

## Storyboard v3.3

| # | Tiempo | Qué se ve | Narración (voz humana) | Cómo se produce |
|---|---|---|---|---|
| 1 | 0:00–0:07 | Negro. Dos frases en serif: **"Llega la plata para reconstruir."** → **"¿Quién está mirando?"** | *(silencio)* | ✅ `video/produccion/intro.mp4` |
| 2 | 0:07–0:15 | Radar de zona afectada: Cali, Buenaventura, Valle del Cauca, Chocó con pulso. Texto: *"Los contratos se firman rápido. Sin concurso."* | "Después de un desastre, el Estado puede contratar sin concurso, para ir rápido. La revisión llega un año después, cuando la plata ya se gastó." | ✅ mismo `intro.mp4` |
| 3 | 0:15–0:26 | **Teléfono real. Llega el Telegram** con la alerta del sismo (Chocó, 97 contratos, $14.492 millones) | "Ella es veedora de su municipio. Lumen le avisa cuando se firma un contrato que vale la pena mirar." | 📹 Grabación de pantalla Android |
| 4 | 0:26–0:36 | Abre el enlace → la ficha del caso real. Señal en lenguaje simple, cifra, fuente oficial, disclaimer visible | "Le dice qué encontró, en español, con la prueba y el enlace a la fuente oficial." | 📹 Grabación de pantalla del navegador |
| 5 | 0:36–0:52 | **El chat.** Se adjunta el PDF de la resolución de urgencia (📎) → el lector responde con el veredicto y las tres citas textuales | "Y lee el documento que justifica la urgencia. Verifica, cita por cita, si de verdad tiene que ver con el desastre." | 📹 Grabación de pantalla del navegador |
| 6 | 0:52–1:00 | Logo + *"Funciona para cualquier declaratoria de desastre. La ventana del sismo dura 12 meses; el problema, siempre."* + **"No acusamos. Ayudamos a preguntar."** | "No acusamos. Ayudamos a preguntar." | ✅ `video/cierre/cierre.mp4` |

---

## Los tres cambios respecto al v3.2, y por qué

**1. El lector de justificaciones vive en el CHAT, no en la ficha.**
Verificado en el código de `origin/main` (commit `4af3e8e`, `web/src/pantallas/Chat.tsx`): el PDF
entra por un botón de adjuntar (📎) que se salta la resolución de entidad y llama directo a
`POST /justificacion`, pintando el veredicto como un mensaje del "lector" en la conversación
(`RespuestaLector`). En la ficha nunca aparece: `Caso.lectura` sale `None` del motor de señales.
El v3.2 lo ponía como "zoom dentro de la ficha" — eso no existe.

**2. El bloque de la carta se absorbe.**
El v3.2 le daba 9 segundos propios (0:38–0:47). Con el lector ocupando su lugar real en el chat,
y con 60 segundos totales, la carta se muestra si alcanza dentro del bloque 5; no se le reserva
tramo propio. El artefacto sigue existiendo y funcionando (`POST /accion`, probado).

**3. El lector pasa a ser el clímax, no un detalle.**
Es la feature que responde el criterio de mayor peso de la rúbrica ("Uso real de IA", 25 pts) —
análisis semántico de un documento no estructurado, con cada cita verificada en código contra el
texto real del PDF. Por eso ahora tiene 16 segundos (el bloque más largo del video) en vez de un
zoom de paso.

---

## Material listo para grabar

**El PDF:** `video/produccion/justificacion-chocó.pdf` — resolución de urgencia manifiesta con
formato oficial (membrete, considerandos, articulado, firma). Probado contra `/justificacion`
real: da **`veredicto=solida`** con las tres citas textuales extraídas del documento.
Es un documento **ilustrativo**, y lo dice en su pie de página: no se presenta como un acto
administrativo real de la Gobernación del Chocó fuera de esta demo.

**El caso real:** `caso-0d6968f81dad` — Gobernación del Chocó, señal S6 (97 contratos
fraccionados), $14.492.100.000. Dato real consultado en vivo, no inventado.

**Servidores locales** (no dependen del despliegue en Render):
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`
- Ficha: `http://127.0.0.1:5173/app/caso/caso-0d6968f81dad`
- Chat: `http://127.0.0.1:5173/app/vigilancia`

---

## Narración — voz humana

Se decidió voz humana sobre TTS. Son cuatro parlamentos; el 1 va en silencio:

> **(bloque 2, ~8s)**
> "Después de un desastre, el Estado puede contratar sin concurso, para ir rápido.
> La revisión llega un año después, cuando la plata ya se gastó."
>
> **(bloque 3, ~11s)**
> "Ella es veedora de su municipio. Lumen le avisa cuando se firma un contrato que vale la
> pena mirar."
>
> **(bloque 4, ~10s)**
> "Le dice qué encontró, en español, con la prueba y el enlace a la fuente oficial."
>
> **(bloque 5, ~16s)**
> "Y lee el documento que justifica la urgencia. Verifica, cita por cita, si de verdad tiene
> que ver con el desastre."
>
> **(bloque 6, ~8s)**
> "No acusamos. Ayudamos a preguntar."

Grabar cada bloque por separado (más fácil de encajar que una sola toma). Tono tranquilo, sin
locución de comercial — el brief pide sobriedad: hay 288 muertos y esto pasó hace cinco días.

---

## Reglas de producción (del v3.1, siguen vigentes)

- Grabar a tamaño de teléfono real y hacer zoom; el jurado ve el video pequeño.
- Subtítulos quemados — muchos jurados ven sin audio.
- Una tipografía, un color de acento, fondo oscuro, cero chrome de navegador.
- Cada texto en pantalla ≤ 7 palabras.
- **No se nombra a Croma ni a ningún competidor en el video.** Croma se declara en el README y
  en la landing; nombrar competidores en 60 segundos se ve defensivo.
