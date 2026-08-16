# Pitch hablado — Lumen

Para decir al frente, con alguien más manejando el demo. Los `[DEMO]` son señas de qué debe
estar en pantalla en ese momento — no se leen.

**Duración: ~2:30.** Los bloques están marcados con lo que se puede recortar si te dan menos
tiempo.

---

## 1. Hook (~20s) · pantalla en negro o el logo

> Colombia se está reconstruyendo después del sismo del 10 de agosto.
>
> Y para reconstruir rápido, la ley permite algo excepcional: contratar sin concurso.
>
> Eso está bien. El problema es lo que pasa después.
>
> **La revisión de esa plata llega un año después. Cuando ya se gastó.**

*(pausa)*

---

## 2. El problema (~30s) · [DEMO] la landing, sección del problema

> Colombia ya vivió esto. En Mocoa. En Providencia. Y en la UNGRD, donde la agencia encargada
> de gestionar el riesgo terminó siendo el caso de corrupción.
>
> El patrón se repite: la ventana de emergencia se abre, la plata entra rápido, y el control
> llega tarde.
>
> Hay gente que ya vigila esto: veedurías, juntas de acción comunal, periodistas locales. No
> les falta voluntad. **Les faltan las ocho horas que cuesta cruzar SECOP con el RUES, contrato
> por contrato.**
>
> Nosotros no les enseñamos a vigilar. Les quitamos el trabajo manual.

---

## 3. La solución (~80s) · [DEMO] corriendo en paralelo

> Lumen es un vigilante que corre solo.

**[DEMO] la alerta de Telegram**
> Revisa lo que se firma en las entidades afectadas, y cuando encuentra un patrón que vale la
> pena mirar, **le escribe a la veedora por Telegram.** Sin instalar nada, sin crear cuenta, sin
> aprender un dashboard.
>
> Aquí encontró que una gobernación firmó 97 contratos casi el mismo día, todos justo por debajo
> del monto que obliga a hacer concurso.

**[DEMO] abre el enlace → la ficha del caso**
> Ella abre el enlace y ve el hallazgo en español. Qué se firmó, cuánto costó, y **el enlace a
> la fuente oficial** para que lo compruebe ella misma. Cada dato con su fuente y su fecha de
> consulta.
>
> Puede ver quién está detrás — el grafo de actores. Y puede pedir la carta para preguntarle a
> la entidad: un derecho de petición redactado a partir de ese hallazgo específico, con los
> hechos numerados y la norma citada.

**[DEMO] el chat — se adjunta el PDF**
> Y esto es lo que ninguna base de datos hace.
>
> Cuando una entidad contrata por urgencia, la ley la obliga a justificarlo por escrito: que
> tenga relación con el desastre, que la necesidad haya surgido después, y que haya un estudio
> técnico que lo respalde.
>
> **Lumen lee ese documento.** Le hace esas tres preguntas, y responde citando el texto exacto
> que lo prueba.
>
> Y si el modelo se inventa una cita, **el código la descarta**: verificamos cada cita contra el
> texto real del PDF. Si no puede citar, no afirma — dice que no puede concluir.

---

## 4. Cierre (~20s)

> Hoy, seis días después del sismo, todavía no hay ni un solo contrato de reconstrucción
> publicado. Los revisamos: cuatrocientos treinta y cuatro procesos, ninguno de urgencia
> manifiesta.
>
> **Por eso Lumen ya está encendido. Para verlos el día que aparezcan, no un año después.**
>
> Funciona para cualquier declaratoria de desastre. La ventana del sismo dura doce meses; el
> problema, siempre.
>
> No acusamos. **Ayudamos a preguntar.**

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

**"¿Esto solo sirve para el sismo?"**
> No. El disparador es la declaratoria de desastre, no el terremoto. Y entre desastres, el mismo
> motor es la mesa de trabajo del veedor sobre contratación ordinaria. Corre desde el día uno.

**"¿De dónde salen los datos?"**
> Fuentes oficiales: el registro mercantil, el sistema de contratación pública, sanciones,
> estados financieros, insolvencia. Todo lo que mostramos trae el enlace a la fuente y la fecha
> en que se consultó.

---

# Si solo te dan 60 segundos

Di esto y nada más:

> Colombia se reconstruye después del sismo, y para ir rápido la ley permite contratar sin
> concurso. La revisión llega un año después, cuando la plata ya se gastó.
>
> Lumen vigila eso solo, y le avisa por Telegram a quien ya hace veeduría — con la evidencia y
> la fuente oficial.
>
> Y hace algo que ninguna base de datos hace: **lee el documento que justifica la urgencia y
> verifica, cita por cita, si de verdad se conecta con el desastre.** Si el modelo inventa una
> cita, el código la descarta.
>
> No acusamos. Ayudamos a preguntar.
