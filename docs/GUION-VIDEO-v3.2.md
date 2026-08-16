# Guion del video — v3.2 (propuesta)

**Esto es una propuesta de Freddy, no una decisión tomada.** Parte del storyboard v3.1 de
`brief-final-claude.md` §8 (el que diseñó Jonatin con el feedback de la mentora) y lo actualiza
con dos cosas que cambiaron esta madrugada — no rediseña nada que ya funcionaba. Quien grabe
(Jonatin al despertar, o quien tome la posta) lo revisa y decide.

**Contexto que cambió el plan: no hay pitch presencial.** El jurado solo ve el video subido — no
hay Q&A en vivo, y es poco probable que revisen el código. Esto sube la apuesta del video: tiene
que venderse solo, sin que nadie lo defienda después.

---

## Qué cambia respecto al v3.1, y por qué

**1. Bloque 0:15–0:26 — el canal es Telegram, no WhatsApp.**
Twilio (2026) exige plantillas aprobadas para cuentas trial, que la cuenta del equipo no tiene —
confirmado contra la API real, no un supuesto. Telegram manda el mensaje real sin esa fricción.
El copy de las 5 líneas no cambia (sigue siendo el de `COPY-SENALES.md`), solo la app que se ve
en pantalla.

**2. Bloque 0:47–0:55 — el chat ya NO hay que cortarlo.**
El storyboard v3.1 tenía el Modo Vigilancia en la lista de hard-cuts por si no daba tiempo.
`/chat` está probado de punta a punta con Croma y Cursor reales (desambiguación → análisis →
narración). Lo único que falta es que la pantalla exista (`web/`, Andrew) — el backend ya
responde.

**Todo lo demás del v3.1 se mantiene igual a propósito:** el gancho de los primeros 7 segundos ya
pasó el test de "si tu mamá no lo entiende, se regraba", y no hay razón para tocar algo que ya
está validado.

---

## Storyboard v3.2

| Tiempo | Qué se ve | Qué se oye |
|---|---|---|
| 0:00–0:07 | Negro. Texto grande, en dos tiempos: **"Llega la plata para reconstruir."** → **"¿Quién está mirando?"** | Silencio, o un solo golpe de sonido |
| 0:07–0:15 | Mapa de los municipios afectados. Texto en pantalla: *"Los contratos se firman rápido. Sin concurso."* | "Después de un desastre, el Estado puede contratar sin concurso, para ir rápido. La revisión llega un año después, cuando la plata ya se gastó." |
| 0:15–0:26 | **Un teléfono. Llega el Telegram.** Se lee la alerta completa, sin prisa | "Ella es veedora de su municipio. Lumen le avisa cuando se firma un contrato que vale la pena mirar." |
| 0:26–0:38 | Abre el enlace → la ficha. Señales en lenguaje simple, una debajo de otra. **Zoom al lector de IA:** *"El documento que justifica la urgencia no menciona ningún daño del terremoto."* | "Le dice qué encontró, en español, con la prueba y el enlace a la fuente oficial." |
| 0:38–0:47 | Botón → la carta redactándose sola | "Y le redacta la carta para preguntarle a la alcaldía. Ella la firma y la manda." |
| 0:47–0:55 | Chat: se escribe *"¿la alcaldía de mi pueblo tiene algo raro?"* y salen las señales con su fuente | "Cuando pase el terremoto, Lumen sigue. Porque la plata pública se vigila todos los días." |
| 0:55–1:00 | Logo + frase en texto | "No acusamos. Ayudamos a preguntar." |

---

## Por qué este guion ya vende la diferenciación sin necesitar Q&A

Como no hay pitch para defenderlo después, la venta tiene que ir cosida en la propia narración.
Ya lo está, si se respeta el guion tal cual:

- **"Le avisa" (0:15), no "ella busca"** → dice push sin decir la palabra. Ninguna plataforma de
  datos abiertos hace esto.
- **"con la prueba y el enlace a la fuente oficial" (0:26)** → verificable, no una afirmación
  suelta.
- **"le redacta la carta... ella la firma y la manda" (0:38)** → acción, no solo dato. Nadie más
  llega hasta aquí.
- **"Lumen sigue... la plata pública se vigila todos los días" (0:47–0:55)** → no es una
  herramienta de un solo evento (el sismo), es una que corre siempre. Responde de una a
  "¿esto solo sirve para el sismo?" sin decirlo explícito.

No hace falta agregar una frase de "somos distintos porque...". Si se nota que se está
defendiendo, se nota inseguro. El guion ya lo hace mostrando, no explicando.

---

## Lo que falta para poder grabar esto tal cual

1. **`web/` tiene que existir.** Los bloques 0:26–0:55 necesitan las pantallas 2, 3 y 4 reales
   (ficha, chat, carta) — hoy `web/` está vacío. Sin esto no hay nada que grabar en esos 29
   segundos, sin importar qué tan bueno esté el guion.
2. **Alguien graba.** Jonatin es el dueño original del bloque de video; si sigue sin estar
   disponible, el equipo necesita decidir quién toma la cámara — esto no se resuelve solo.
3. **El chat_id/bot de Telegram que sale en el video** tiene que ser el mismo que ya está unido
   (`5833175479`, ver `docs/handoff/FREDDY-B2.md`), o el mensaje no llega en vivo durante la
   grabación.

Mientras 1 y 2 no estén resueltos, esto queda como guion listo para usar apenas se pueda grabar
— no bloquea nada más del equipo.
