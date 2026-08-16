/**
 * Textos de la landing en español e inglés.
 *
 * Solo la landing es bilingüe: el producto es para ciudadanía colombiana y se
 * queda en español. El inglés existe porque el jurado y los compradores
 * (multilaterales, filantropía cívica) sí son internacionales.
 */
import { createContext, use, useState } from 'react'

export type Idioma = 'es' | 'en'

export const TEXTOS = {
  es: {
    navProducto: 'Cómo funciona',
    navSenales: 'Las señales',
    navFuentes: 'Fuentes',
    navEntrar: 'Ver la herramienta',

    heroSello: 'Decreto 1171',
    heroEtiqueta: 'Desastre nacional · 12 meses de contratación directa',
    heroTitulo: 'El control de la plata de la reconstrucción es posterior.',
    heroFilete: 'Vigilancia en tiempo real',
    heroTituloAcento: 'Nosotros lo hacemos hoy.',
    heroBajada:
      'Lumen revisa los contratos de emergencia apenas se publican, lee las justificaciones que la ley exige y avisa cuando algo merece una pregunta. Con la fuente oficial al lado de cada dato.',
    heroCta: 'Vigilar contratos',
    heroCtaSecundaria: 'Ver una alerta real',
    heroNota: 'Sin registro. Sin saber qué es SECOP. Gratis.',

    problemaEtiqueta: 'La ventana que se abrió',
    problemaTitulo: 'Miles de millones se mueven sin licitación durante doce meses',
    problemaTexto:
      'El artículo 46 de la Ley 1523 permite adjudicar de forma directa tras una declaratoria de desastre. La Contraloría revisa después. Para cuando el control llega, la plata ya se gastó.',
    cifras: [
      { dato: '448', etiqueta: 'municipios afectados' },
      { dato: '12 meses', etiqueta: 'de contratación directa' },
      { dato: 'US$450M', etiqueta: 'de crédito en gestión' },
      { dato: 'Posterior', etiqueta: 'es el control fiscal' },
    ],

    modosEtiqueta: 'Cómo funciona',
    modosTitulo: 'Un motor, dos modos',
    modosBajada:
      'El sismo es la ventana que está abierta hoy. La fuga de plata pública está abierta todos los días.',
    modoEmergenciaTitulo: 'Modo Emergencia',
    modoEmergenciaTexto:
      'Corre solo. Revisa lo que entra por el régimen excepcional, arma el caso y avisa por WhatsApp al veedor o al periodista del municipio, con el derecho de petición ya redactado.',
    modoEmergenciaCta: 'Ver una alerta',
    modoVigilanciaTitulo: 'Modo Vigilancia',
    modoVigilanciaTexto:
      'El mismo motor como agente conversacional. Escribe «¿la alcaldía de mi pueblo tiene algo raro?» y recibe la red de actores, las señales y el artefacto para actuar.',
    modoVigilanciaCta: 'Abrir el chat',

    demoEtiqueta: 'La herramienta',
    demoTitulo: 'Se abre, se pregunta y responde con la fuente al lado',
    demoTexto:
      'El mismo motor de las ocho señales, con el disparador invertido: escribe el nombre de tu alcaldía y Lumen resuelve la entidad, corre las reglas y te deja el derecho de petición redactado. Sin registro y sin saber qué es el SECOP.',
    demoCta: 'Abrir la herramienta',

    senalesEtiqueta: 'El motor',
    senalesTitulo: 'Ocho señales deterministas, no una corazonada',
    senalesBajada:
      'Cada señal guarda la regla en lenguaje claro, el dato exacto que la disparó y el enlace a la fuente oficial con su fecha de consulta.',
    senales: [
      { codigo: 'S1', nombre: 'Empresa recién creada que gana', regla: 'Menos de un año entre el registro y la adjudicación.' },
      { codigo: 'S2', nombre: 'Representante compartido', regla: 'La misma persona al frente de varias empresas que contratan con la misma entidad.' },
      { codigo: 'S3', nombre: 'Sancionado que sigue contratando', regla: 'Sanción vigente y contratos posteriores.' },
      { codigo: 'S4', nombre: 'Contrato desproporcionado', regla: 'El contrato vale más que los ingresos anuales que reporta la empresa.' },
      { codigo: 'S5', nombre: 'Insolvente contratando', regla: 'Proceso de insolvencia en curso y adjudicaciones activas.' },
      { codigo: 'S6', nombre: 'Fraccionamiento', regla: 'Contratos parecidos, misma entidad, fechas cercanas, todos bajo el umbral.' },
      { codigo: 'S7/S8', nombre: 'Concentración y directa recurrente', regla: 'Qué porcentaje del valor total se lleva un solo proveedor.' },
      { codigo: 'S10', nombre: 'Deudor moroso del Estado', regla: 'Le debe al Estado y el Estado le sigue adjudicando.' },
    ],

    iaEtiqueta: 'Inteligencia artificial',
    iaTitulo: 'Dónde está la IA, y por qué no es decoración',
    iaTexto:
      'La ley exige que toda contratación por urgencia manifiesta se relacione de forma directa y verificable con los hechos de la emergencia. Esa justificación es un PDF en texto libre. El modelo lo lee y evalúa si describe daños concretos o lenguaje de plantilla — y cita el fragmento que sustenta cada punto. Si no puede citar, no afirma.',
    iaNota: 'El motor de señales es determinista. La IA narra y contextualiza, no inventa reglas.',

    canalesEtiqueta: 'Por dónde sale',
    canalesTitulo: 'El motor no se queda en esta página',
    canalesBajada:
      'Un hallazgo que nadie ve no sirve de nada. Lo que Lumen encuentra sale por tres puertas, y las tres corren sobre las mismas ocho señales.',
    canalesPie: 'El monitor no espera a que alguien pregunte.',
    canales: [
      {
        titulo: 'El monitor, solo',
        texto:
          'Revisa cada pocos minutos lo que entra por el régimen de emergencia y arma el caso sin que nadie se lo pida.',
      },
      {
        titulo: 'Bot de Telegram',
        texto:
          'El aviso llega al veedor o al periodista del municipio con el derecho de petición redactado y la fuente enlazada.',
      },
      {
        titulo: 'Servidor MCP',
        texto:
          'Nueve herramientas abiertas para que un agente externo —Claude, Cursor— consulte el mismo motor desde donde ya trabaja.',
      },
    ],

    eticaEtiqueta: 'Guardarraíles',
    eticaTitulo: 'Lo que esta herramienta no hace',
    etica: [
      'No dice que alguien es corrupto. Prioriza dónde mirar.',
      'No publica un score ni un porcentaje de probabilidad de corrupción.',
      'No publica una señal sin su fuente oficial y su fecha de consulta.',
      'No republica bases de datos. Publica hallazgos enlazados a la fuente.',
    ],

    fuentesEtiqueta: 'Trazabilidad',
    fuentesTitulo: 'Todo sale de fuentes oficiales',
    fuentesTexto:
      'Cada señal muestra el dato que la disparó, la regla que aplicó y el enlace a la fuente con su fecha de consulta. No republicamos bases: publicamos hallazgos enlazados.',
    fuentesVia: 'Datos a través de Croma',

    cita: 'No acusamos. Ayudamos a preguntar.',

    cierreTitulo: '¿Quieres saber qué está contratando tu municipio?',
    cierreTexto:
      'Escribe el nombre de tu alcaldía y mira qué se está firmando esta semana, con la fuente oficial al lado de cada dato.',
    cierreCta: 'Empezar a vigilar',

    piePitch: 'Vigilancia ciudadana sobre la plata de la reconstrucción.',
    pieProducto: 'Producto',
    pieCanales: 'Canales de salida',
    pieMetodo: 'El método',
    pieProyecto: 'El proyecto',
    pieSenales: 'Las ocho señales',
    pieFuentes: 'Fuentes oficiales',
    pieEtica: 'Lo que no hace',
    pieHackathon: 'Hackathon CTW 2026',
    pieTrack: 'Track 01 · Tecnología para la transparencia',
    pieDerechos: '© 2026 Lumen',
  },

  en: {
    navProducto: 'How it works',
    navSenales: 'The signals',
    navFuentes: 'Sources',
    navEntrar: 'Open the tool',

    heroSello: 'Decree 1171',
    heroEtiqueta: 'National disaster · 12 months of no-bid contracting',
    heroTitulo: 'Oversight of reconstruction money comes after the fact.',
    heroFilete: 'Oversight in real time',
    heroTituloAcento: 'We do it today.',
    heroBajada:
      'Lumen reviews emergency contracts as soon as they are published, reads the legal justifications the law requires, and raises a flag when something deserves a question — with the official source next to every figure.',
    heroCta: 'Watch contracts',
    heroCtaSecundaria: 'See a real alert',
    heroNota: 'No sign-up. No procurement expertise needed. Free.',

    problemaEtiqueta: 'The window that opened',
    problemaTitulo: 'Billions move without bidding for twelve months',
    problemaTexto:
      'Article 46 of Law 1523 allows direct awards once a disaster is declared. The Comptroller reviews afterwards. By the time oversight arrives, the money is spent.',
    cifras: [
      { dato: '448', etiqueta: 'municipalities affected' },
      { dato: '12 months', etiqueta: 'of direct contracting' },
      { dato: 'US$450M', etiqueta: 'credit line in progress' },
      { dato: 'After the fact', etiqueta: 'is when audit happens' },
    ],

    modosEtiqueta: 'How it works',
    modosTitulo: 'One engine, two modes',
    modosBajada:
      'The earthquake is the window open today. The leak of public money is open every day.',
    modoEmergenciaTitulo: 'Emergency Mode',
    modoEmergenciaTexto:
      'Runs on its own. Scans what enters under the exceptional regime, builds the case and alerts the local watchdog or reporter over WhatsApp, with the freedom-of-information request already drafted.',
    modoEmergenciaCta: 'See an alert',
    modoVigilanciaTitulo: 'Watch Mode',
    modoVigilanciaTexto:
      'The same engine as a conversational agent. Type "is anything odd with my town hall?" and get the network of actors, the signals and the artifact to act on.',
    modoVigilanciaCta: 'Open the chat',

    demoEtiqueta: 'The tool',
    demoTitulo: 'Open it, ask, and it answers with the source beside every figure',
    demoTexto:
      'The same eight-signal engine with the trigger inverted: type the name of your town hall and Lumen resolves the entity, runs the rules and drafts the freedom-of-information request for you. No sign-up, no procurement expertise needed.',
    demoCta: 'Open the tool',

    senalesEtiqueta: 'The engine',
    senalesTitulo: 'Eight deterministic signals, not a hunch',
    senalesBajada:
      'Every signal carries its rule in plain language, the exact figure that triggered it, and a link to the official source with the date it was consulted.',
    senales: [
      { codigo: 'S1', nombre: 'Newly created company wins', regla: 'Less than a year between registration and award.' },
      { codigo: 'S2', nombre: 'Shared legal representative', regla: 'The same person heading several companies contracting with the same entity.' },
      { codigo: 'S3', nombre: 'Sanctioned and still contracting', regla: 'An active sanction plus later contracts.' },
      { codigo: 'S4', nombre: 'Disproportionate contract', regla: 'The contract is worth more than the company reports in annual revenue.' },
      { codigo: 'S5', nombre: 'Insolvent and contracting', regla: 'Insolvency proceedings under way alongside active awards.' },
      { codigo: 'S6', nombre: 'Contract splitting', regla: 'Similar contracts, same entity, close dates, all under the threshold.' },
      { codigo: 'S7/S8', nombre: 'Concentration and repeated direct awards', regla: 'How much of the total value goes to a single supplier.' },
      { codigo: 'S10', nombre: 'State debtor still contracting', regla: 'Owes the State, and the State keeps awarding.' },
    ],

    iaEtiqueta: 'Artificial intelligence',
    iaTitulo: 'Where the AI is, and why it is not decoration',
    iaTexto:
      'The law requires every emergency award to bear a direct, verifiable relationship to the events behind the emergency. That justification is a free-text PDF. The model reads it and judges whether it describes concrete damage or boilerplate language — quoting the passage behind each point. If it cannot quote, it does not assert.',
    iaNota: 'The signal engine is deterministic. The AI narrates and contextualizes; it does not invent rules.',

    canalesEtiqueta: 'Where it comes out',
    canalesTitulo: 'The engine does not stay on this page',
    canalesBajada:
      'A finding nobody sees is worth nothing. What Lumen finds comes out through three doors, and all three run on the same eight signals.',
    canalesPie: 'The monitor does not wait to be asked.',
    canales: [
      {
        titulo: 'The monitor, on its own',
        texto:
          'Every few minutes it checks what enters under the emergency regime and builds the case before anyone asks.',
      },
      {
        titulo: 'Telegram bot',
        texto:
          'The alert reaches the local watchdog or reporter with the freedom-of-information request drafted and the source linked.',
      },
      {
        titulo: 'MCP server',
        texto:
          'Nine tools open so an external agent — Claude, Cursor — can query the same engine from wherever it already works.',
      },
    ],

    eticaEtiqueta: 'Guardrails',
    eticaTitulo: 'What this tool does not do',
    etica: [
      'It never says someone is corrupt. It prioritizes where to look.',
      'It never publishes a score or a "probability of corruption".',
      'It never publishes a signal without its official source and consultation date.',
      'It never republishes databases. It publishes findings linked to the source.',
    ],

    fuentesEtiqueta: 'Traceability',
    fuentesTitulo: 'Everything comes from official sources',
    fuentesTexto:
      'Every signal shows the figure that triggered it, the rule it applied and the link to the source with its consultation date. We do not republish databases: we publish findings that link back.',
    fuentesVia: 'Data through Croma',

    cita: 'We do not accuse. We help you ask.',

    cierreTitulo: 'Want to know what your municipality is contracting?',
    cierreTexto:
      'Type the name of your town hall and see what is being signed this week, with the official source next to every figure.',
    cierreCta: 'Start watching',

    piePitch: 'Citizen oversight of reconstruction money.',
    pieProducto: 'Product',
    pieCanales: 'Where it comes out',
    pieMetodo: 'The method',
    pieProyecto: 'The project',
    pieSenales: 'The eight signals',
    pieFuentes: 'Official sources',
    pieEtica: 'What it does not do',
    pieHackathon: 'CTW 2026 Hackathon',
    pieTrack: 'Track 01 · Technology for transparency',
    pieDerechos: '© 2026 Lumen',
  },
} as const

/** Mismo texto del parche v3.1 que `lib/tipos.ts`, traducido para la landing. */
export const DISCLAIMER_LANDING = {
  es: 'Una señal no es prueba de irregularidad. Es un motivo para preguntar.',
  en: 'A signal is not proof of wrongdoing. It is a reason to ask.',
}

export const IdiomaContext = createContext<{
  idioma: Idioma
  cambiar: (i: Idioma) => void
}>({ idioma: 'es', cambiar: () => {} })

export function useIdioma() {
  const { idioma, cambiar } = use(IdiomaContext)
  return { idioma, cambiar, t: TEXTOS[idioma] }
}

export function useEstadoIdioma() {
  const [idioma, setIdioma] = useState<Idioma>(
    () => (localStorage.getItem('lumen-idioma') as Idioma) ?? 'es',
  )
  const cambiar = (i: Idioma) => {
    localStorage.setItem('lumen-idioma', i)
    document.documentElement.lang = i
    setIdioma(i)
  }
  return { idioma, cambiar }
}
