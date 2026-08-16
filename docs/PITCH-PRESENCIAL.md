# Pitch hablado — Lumen

Para decir al frente **junto con el video**, no en vez del video.

**Regla:** el video ya cuenta qué hace el producto. Este guion **no lo repite** — cuenta lo que
el video no alcanza a decir: por qué está construido así, y por qué no se muere el lunes.

Lo único que se comparte con el video es el hook. Ese sí va tal cual.

**Duración: ~1:40** sin contar el video.

---

## 1. HOOK (~20s) — va tal cual, es lo más importante

> Colombia se está reconstruyendo después del sismo del 10 de agosto.
>
> Y para reconstruir rápido, la ley permite algo excepcional: contratar sin concurso.
>
> Eso está bien. El problema es lo que pasa después.
>
> **La revisión de esa plata llega un año después. Cuando ya se gastó.**

*(pausa — aquí entra el video)*

---

## 2. LO QUE EL VIDEO NO ALCANZA A CONTAR (~50s)

*(esto va después del video, o mientras el demo se recorre en silencio)*

> Lo que vieron son tres decisiones que tomamos a propósito, y que son la diferencia entre una
> herramienta y un dashboard más.

**Primera — nunca un puntaje.**
> Lumen jamás dice "78% de probabilidad de corrupción". Son tres estados con color, y ya. Un
> número da una falsa precisión que ningún dato público sostiene, y señala gente sin pruebas.
> Está forzado en el código: si alguien intenta meter un porcentaje ahí, el sistema no compila.

**Segunda — sin fuente no hay señal.**
> Ninguna señal se puede construir sin su enlace oficial y su fecha de consulta. No es una regla
> de estilo: es el tipo de dato. Si no hay fuente, la señal no existe.

**Tercera — si la IA no puede citar, no afirma.**
> Cuando el lector evalúa un documento, verificamos cada cita contra el texto real del PDF. Si el
> modelo se la inventó, la descartamos y ese punto queda como "no se pudo concluir". El veredicto
> más fuerte es imposible de dar si falta una sola cita verificada.
>
> **No le pedimos al modelo que se porte bien. Se lo impedimos en el código.**

---

## 3. POR QUÉ NO SE MUERE EL LUNES (~30s)

> Tres cosas que ya son ciertas hoy, no promesas:

> **Está corriendo.** Backend desplegado, frontend desplegado, base de datos real, y un bot que
> manda mensajes de verdad. No es un prototipo local.

> **No depende del sismo.** El disparador es la declaratoria de desastre, no el terremoto. Sirve
> igual para una emergencia sanitaria o de orden público. Y entre desastres, el mismo motor es la
> mesa de trabajo del veedor sobre contratación ordinaria — funciona desde el día uno.

> **No depende de Colombia.** Perú y México ya están disponibles en la capa de datos. Cambia la
> fuente, no el motor.

---

## 4. CIERRE (~15s)

> Una última cosa, y es la más incómoda.
>
> Hoy, seis días después del sismo, revisamos las cuatro entidades afectadas: **cuatrocientos
> treinta y cuatro procesos publicados, y ni uno solo por urgencia manifiesta.**
>
> Todavía no hay nada que auditar. Y esa es exactamente la razón de existir de esto.
>
> **Lumen ya está encendido, para verlos el día que aparezcan. No un año después.**
>
> No acusamos. Ayudamos a preguntar.

---

# Respuestas preparadas

**"¿Esto no es otra plataforma de datos abiertos?"**
> Esas te muestran el dato para que tú lo interpretes. Nosotros cruzamos varias fuentes, te
> avisamos sin que preguntes, y te entregamos la carta lista. Y ninguna lee el documento legal
> que justifica la urgencia — eso no está en ninguna base de datos, hay que leerlo.

**"¿La IA es el núcleo o es un wrapper?"**
> El lector de justificaciones. Análisis semántico de un documento no estructurado contra un
> estándar legal, con cada cita verificada en código. Ninguna regla SQL hace eso. Las ocho
> señales sí son deterministas — a propósito: no queremos un LLM decidiendo si alguien es
> sospechoso.

**"¿Van a generar falsos positivos?"**
> Sí, y por eso el lenguaje es "señal" y "motivo para preguntar", nunca "corrupto". Cada señal
> muestra su regla, su dato y su fuente para que un humano juzgue. Y el resultado es una carta
> para preguntar — un derecho de petición, que es exactamente lo que un ciudadano tiene derecho
> a hacer.

**"La Contraloría ya hace control preventivo."**
> Cierto, y hay que reconocerlo. Pero es institucional, cubre proyectos seleccionados, y no es
> un feed público: la veedora de Quibdó no recibe nada. No reemplazamos a la Contraloría — le
> damos a quien ya vigila la capacidad de preguntar más rápido.

**"¿Por qué Telegram y no una app?"**
> Porque nuestro usuario no se va a instalar una app. Suele ser una persona mayor que ya hace
> veeduría — la mamá, la tía, el jubilado del barrio. Le llega donde ya está, sin crear cuenta y
> sin aprender nada.

**"¿De dónde salen los datos?"**
> Fuentes oficiales: el registro mercantil, el sistema de contratación pública, sanciones,
> estados financieros, insolvencia. Todo lo que mostramos trae el enlace a la fuente y la fecha
> en que se consultó.

---

# Si te cortan el tiempo

Di el **hook** completo, y luego solo esto:

> Lo que acaban de ver tiene tres reglas en el código: nunca un puntaje de corrupción, ninguna
> señal sin su fuente oficial, y si la IA no puede citar el documento, no afirma.
>
> Está desplegado y corriendo hoy. Y hoy, seis días después del sismo, todavía no hay ni un
> contrato de reconstrucción publicado — por eso ya está encendido.
>
> No acusamos. Ayudamos a preguntar.
