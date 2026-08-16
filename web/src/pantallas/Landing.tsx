/**
 * La landing: la puerta de entrada, en español e inglés.
 *
 * El producto está en español porque es para ciudadanía colombiana. Esta página
 * es bilingüe porque el jurado y los compradores (multilaterales, filantropía
 * cívica, medios) no lo son.
 *
 * Corre en tema claro sobre la pintura del hero; el resto de la app sigue en
 * oscuro.
 */
import { useEffect } from 'react'
import { Link } from 'react-router'
import { DISCLAIMER_LANDING, useIdioma } from '../lib/copy'
import { Boton, Rubrica } from '../componentes/Basicos'
import { Greca } from '../componentes/Greca'
import { Marca } from '../componentes/Marca'
import fondoHero from '../assets/hero-fondo.jpg'
import buhoAscii from '../assets/buho-ascii.png'
import demoVigilancia from '../assets/demo-vigilancia.png'

const CROMA = 'https://usecroma.com'
const NUMERAL = ['I', 'II', 'III', 'IV']

const MARMOL = (porcentaje: number) =>
  `color-mix(in oklch, var(--color-fondo) ${porcentaje}%, transparent)`

export function PantallaLanding() {
  const { idioma, cambiar, t } = useIdioma()

  useEffect(() => {
    document.documentElement.classList.add('tema-claro')
    return () => document.documentElement.classList.remove('tema-claro')
  }, [])

  const modos = [
    {
      titulo: t.modoEmergenciaTitulo,
      texto: t.modoEmergenciaTexto,
      cta: t.modoEmergenciaCta,
      a: '/app/emergencia',
    },
    {
      titulo: t.modoVigilanciaTitulo,
      texto: t.modoVigilanciaTexto,
      cta: t.modoVigilanciaCta,
      a: '/app/vigilancia',
    },
  ]

  return (
    <div className="min-h-dvh bg-[var(--color-fondo)] text-[var(--color-texto)]">
      <Barra t={t} idioma={idioma} cambiar={cambiar} />

      <main>
        <section className="bg-[var(--color-fondo)]">
          {/*
            La pintura va entera y sin velo. En escritorio se pone detrás del
            titular, que se posa sobre el cielo y el templo —lo claro— y ahí la
            tinta se lee sin tapar nada. En móvil la franja es muy estrecha para
            escribir encima, así que el cuadro va arriba y el texto debajo.
          */}
          <div className="relative">
            <div className="relative aspect-[16/9] max-h-[54svh] w-full sm:absolute sm:inset-0 sm:h-full sm:max-h-none">
              <img
                src={fondoHero}
                alt=""
                aria-hidden
                className="h-full w-full object-cover object-[50%_46%]"
              />
            </div>

            <div className="relative mx-auto w-full max-w-6xl px-6 pt-8 sm:flex sm:min-h-[54svh] sm:flex-col sm:justify-start sm:pt-[7%]">
              <p className="inline-flex flex-wrap items-center gap-2.5 self-start border border-[var(--color-borde)] bg-[color-mix(in_oklch,var(--color-fondo)_78%,transparent)] py-1 pl-1 pr-4 text-xs backdrop-blur-sm">
                <span className="bg-[var(--color-lumen)] px-2.5 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--color-lumen-texto)]">
                  {t.heroSello}
                </span>
                <span className="text-[var(--color-texto-tenue)]">{t.heroEtiqueta}</span>
              </p>

              <h1 className="mt-6 max-w-[19ch] font-serif text-[clamp(2.1rem,4.4vw,3.5rem)] font-normal leading-[1.08] tracking-[-0.01em]">
                {t.heroTitulo}
              </h1>
            </div>
          </div>

          <div className="mx-auto w-full max-w-6xl px-6 pb-16 pt-12 sm:pb-24 sm:pt-16">
            <div className="flex items-center gap-4 sm:pl-[5%]">
              <span className="h-px w-10 bg-[var(--color-bronce)] opacity-70 sm:w-16" />
              <span className="text-[0.66rem] uppercase tracking-[0.3em] text-[var(--color-lumen)]">
                {t.heroFilete}
              </span>
              <span className="h-px flex-1 bg-[var(--color-borde)]" />
            </div>

            <p className="mt-6 font-serif text-[clamp(2.1rem,4.4vw,3.5rem)] leading-[1.08] tracking-[-0.01em] sm:pl-[5%]">
              {t.heroTituloAcento}
            </p>

            <div className="mt-11 flex flex-col gap-8 sm:mt-14 sm:flex-row sm:items-end sm:justify-between">
              <div className="max-w-md">
                <p className="text-sm leading-relaxed text-[var(--color-texto-tenue)]">
                  {t.heroBajada}
                </p>
                <p className="mt-4 text-xs font-medium text-[var(--color-texto)]">{t.heroNota}</p>
              </div>
              <div className="flex shrink-0 flex-wrap gap-3">
                <Boton a="/app/vigilancia" tamano="lg">
                  {t.heroCta}
                </Boton>
                <Boton a="/app/emergencia" variante="velado" tamano="lg">
                  {t.heroCtaSecundaria}
                </Boton>
              </div>
            </div>

            <p className="mt-10 flex items-center gap-4 border-t border-[var(--color-borde)] pt-5 text-xs text-[var(--color-texto-tenue)]">
              <span className="h-px w-7 shrink-0 bg-[var(--color-bronce)]" />
              {DISCLAIMER_LANDING[idioma]}
            </p>
          </div>
        </section>

        <section id="problema" className="mx-auto max-w-6xl px-6 py-24 sm:py-32">
          <Rubrica>{t.problemaEtiqueta}</Rubrica>
          <h2 className="mt-6 max-w-3xl font-serif text-[clamp(1.75rem,3.2vw,2.6rem)] font-normal leading-[1.15]">
            {t.problemaTitulo}
          </h2>
          <p className="mt-6 max-w-2xl leading-relaxed text-[var(--color-texto-tenue)]">
            {t.problemaTexto}
          </p>

          <dl className="mt-14 grid grid-cols-2 gap-px border border-[var(--color-borde)] bg-[var(--color-borde)] sm:grid-cols-4">
            {t.cifras.map((cifra) => (
              <div key={cifra.etiqueta} className="bg-[var(--color-fondo)] px-5 py-7 sm:px-6 sm:py-8">
                <dt className="font-serif text-2xl text-[var(--color-lumen)] sm:text-[2.5rem]">
                  {cifra.dato}
                </dt>
                <dd className="mt-3 text-[0.7rem] uppercase leading-relaxed tracking-[0.12em] text-[var(--color-texto-tenue)]">
                  {cifra.etiqueta}
                </dd>
              </div>
            ))}
          </dl>
        </section>

        <section id="modos" className="mx-auto max-w-6xl px-6 pb-24 sm:pb-32">
          <div className="text-center">
            <Rubrica centrada>{t.modosEtiqueta}</Rubrica>
            <h2 className="mt-6 font-serif text-[clamp(1.75rem,3.2vw,2.6rem)] font-normal leading-[1.15]">
              {t.modosTitulo}
            </h2>
            <p className="mx-auto mt-5 max-w-xl font-serif text-lg italic leading-relaxed text-[var(--color-texto-tenue)]">
              {t.modosBajada}
            </p>
          </div>

          <div className="mt-14 grid gap-px border border-[var(--color-borde)] bg-[var(--color-borde)] sm:grid-cols-2">
            {modos.map((modo, i) => (
              <Link
                key={modo.titulo}
                to={modo.a}
                className="group flex flex-col bg-[var(--color-fondo)] p-8 transition-colors hover:bg-[var(--color-superficie)] sm:p-10"
              >
                <span className="font-serif text-3xl text-[var(--color-bronce)]">{NUMERAL[i]}</span>
                <h3 className="mt-7 font-serif text-2xl">{modo.titulo}</h3>
                <p className="mt-4 flex-1 text-sm leading-relaxed text-[var(--color-texto-tenue)]">
                  {modo.texto}
                </p>
                <span className="mt-9 flex items-center justify-between border-t border-[var(--color-borde)] pt-5 text-[0.68rem] uppercase tracking-[0.2em] text-[var(--color-lumen)]">
                  {modo.cta}
                  <span aria-hidden className="transition-transform group-hover:translate-x-1">
                    →
                  </span>
                </span>
              </Link>
            ))}
          </div>
        </section>

        {/*
          La herramienta se enseña, no se describe: la captura se funde hacia
          abajo en el mismo mármol de la página, sin marco de navegador.
        */}
        <section className="overflow-hidden border-t border-[var(--color-borde)] bg-[var(--color-superficie)]">
          <div className="mx-auto max-w-3xl px-6 pt-24 text-center sm:pt-32">
            <Rubrica centrada>{t.demoEtiqueta}</Rubrica>
            <h2 className="mt-6 font-serif text-[clamp(1.75rem,3.2vw,2.6rem)] font-normal leading-[1.15]">
              {t.demoTitulo}
            </h2>
            <p className="mx-auto mt-6 max-w-xl leading-relaxed text-[var(--color-texto-tenue)]">
              {t.demoTexto}
            </p>
            <div className="mt-9 flex justify-center">
              <Boton a="/app/vigilancia" tamano="lg">
                {t.demoCta}
              </Boton>
            </div>
          </div>

          <div className="relative mx-auto mt-16 max-w-5xl px-6">
            <img
              src={demoVigilancia}
              alt=""
              aria-hidden
              className="w-full border border-[var(--color-borde)] shadow-[0_40px_90px_-60px_oklch(0.3_0.05_264/0.55)]"
            />
            <div
              className="absolute inset-x-0 bottom-0 h-2/5"
              style={{
                background: `linear-gradient(to bottom, transparent, ${MARMOL(70)} 45%, var(--color-superficie) 100%)`,
              }}
            />
          </div>
        </section>

        <section
          id="senales"
          className="border-y border-[var(--color-borde)] bg-[var(--color-superficie)]"
        >
          <div className="mx-auto max-w-6xl px-6 py-24 sm:py-32">
            <Rubrica>{t.senalesEtiqueta}</Rubrica>
            <h2 className="mt-6 max-w-3xl font-serif text-[clamp(1.75rem,3.2vw,2.6rem)] font-normal leading-[1.15]">
              {t.senalesTitulo}
            </h2>
            <p className="mt-6 max-w-2xl leading-relaxed text-[var(--color-texto-tenue)]">
              {t.senalesBajada}
            </p>

            <ul className="mt-14 grid gap-px border border-[var(--color-borde)] bg-[var(--color-borde)] sm:grid-cols-2">
              {t.senales.map((senal) => (
                <li key={senal.codigo} className="bg-[var(--color-fondo)] p-7">
                  <div className="flex items-baseline gap-4">
                    <span className="w-12 shrink-0 font-serif text-sm tracking-widest text-[var(--color-lumen)]">
                      {senal.codigo}
                    </span>
                    <h3 className="font-serif text-lg">{senal.nombre}</h3>
                  </div>
                  <p className="mt-3 text-sm leading-relaxed text-[var(--color-texto-tenue)] sm:pl-16">
                    {senal.regla}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="border-y border-[var(--color-borde)] bg-[var(--color-superficie)]">
          <div className="mx-auto max-w-6xl px-6 py-24 sm:py-32">
            <div className="grid items-center gap-12 sm:grid-cols-[minmax(0,17rem)_1fr] sm:gap-16">
              {/* El ASCII viene con fondo blanco opaco: multiply lo funde en el mármol. */}
              <img
                src={buhoAscii}
                alt=""
                aria-hidden
                className="w-60 justify-self-center mix-blend-multiply sm:w-full"
              />
              <div>
                <Rubrica>{t.iaEtiqueta}</Rubrica>
                <h2 className="mt-6 max-w-2xl font-serif text-[clamp(1.75rem,3.2vw,2.6rem)] font-normal leading-[1.15]">
                  {t.iaTitulo}
                </h2>
                <p className="mt-6 max-w-2xl leading-relaxed text-[var(--color-texto-tenue)]">
                  {t.iaTexto}
                </p>
                <p className="mt-9 max-w-2xl border-l-2 border-[var(--color-lumen)] pl-5 font-serif text-lg italic leading-relaxed">
                  {t.iaNota}
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="etica" className="mx-auto max-w-6xl px-6 py-24 sm:py-32">
          <Rubrica>{t.eticaEtiqueta}</Rubrica>
          <h2 className="mt-6 font-serif text-[clamp(1.75rem,3.2vw,2.6rem)] font-normal leading-[1.15]">
            {t.eticaTitulo}
          </h2>

          <ol className="mt-14 grid gap-px border border-[var(--color-borde)] bg-[var(--color-borde)] sm:grid-cols-2">
            {t.etica.map((linea, i) => (
              <li key={linea} className="flex gap-6 bg-[var(--color-fondo)] p-8">
                <span className="w-7 shrink-0 font-serif text-xl leading-none text-[var(--color-bronce)]">
                  {NUMERAL[i]}
                </span>
                <p className="leading-relaxed text-[var(--color-texto-tenue)]">{linea}</p>
              </li>
            ))}
          </ol>
        </section>

        <section
          id="fuentes"
          className="border-y border-[var(--color-borde)] bg-[var(--color-superficie)]"
        >
          <div className="mx-auto max-w-6xl px-6 py-20 sm:py-24">
            <Rubrica>{t.fuentesEtiqueta}</Rubrica>
            <h2 className="mt-6 font-serif text-[clamp(1.6rem,2.8vw,2.25rem)] font-normal leading-[1.15]">
              {t.fuentesTitulo}
            </h2>

            <ul className="mt-10 flex flex-wrap items-center gap-x-9 gap-y-4 font-serif text-lg text-[var(--color-texto-tenue)]">
              {t.fuentesLista.map((fuente) => (
                <li key={fuente}>{fuente}</li>
              ))}
            </ul>

            <p className="mt-10 max-w-2xl text-sm leading-relaxed text-[var(--color-texto-tenue)]">
              {t.fuentesTexto}{' '}
              <a
                href={CROMA}
                target="_blank"
                rel="noreferrer noopener"
                className="text-[var(--color-lumen)] underline decoration-dotted underline-offset-4"
              >
                {t.fuentesVia}
              </a>
              .
            </p>
          </div>
        </section>

        <section className="mx-auto max-w-3xl px-6 py-24 text-center sm:py-32">
          <Greca className="mx-auto w-[168px] text-[var(--color-bronce)] opacity-80" />
          <blockquote className="mt-11 font-serif text-[clamp(1.9rem,4vw,3rem)] italic leading-[1.25]">
            «{t.cita}»
          </blockquote>
          <p className="mt-8 text-sm text-[var(--color-texto-tenue)]">
            {DISCLAIMER_LANDING[idioma]}
          </p>
          <Greca className="mx-auto mt-11 w-[168px] rotate-180 text-[var(--color-bronce)] opacity-80" />
        </section>

        <section className="mx-auto max-w-3xl px-6 pb-28 text-center sm:pb-36">
          <h2 className="font-serif text-[clamp(2rem,4.2vw,3.1rem)] font-normal leading-[1.12]">
            {t.cierreTitulo}
          </h2>
          <p className="mx-auto mt-6 max-w-xl leading-relaxed text-[var(--color-texto-tenue)]">
            {t.cierreTexto}
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-3">
            <Boton a="/app/vigilancia" tamano="lg">
              {t.cierreCta}
            </Boton>
            <Boton a="/app/emergencia" variante="secundario" tamano="lg">
              {t.heroCtaSecundaria}
            </Boton>
          </div>
          <p className="mt-6 text-xs text-[var(--color-texto-tenue)]">{t.heroNota}</p>
        </section>
      </main>

      <footer className="tema-oscuro bg-[var(--color-fondo)] text-[var(--color-texto)]">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <Marca tamano="md" />
              <p className="mt-4 max-w-xs text-sm leading-relaxed text-[var(--color-texto-tenue)]">
                {t.piePitch}
              </p>
            </div>

            <ColumnaPie titulo={t.pieProducto}>
              <EnlacePie a="/app/emergencia">{t.modoEmergenciaTitulo}</EnlacePie>
              <EnlacePie a="/app/vigilancia">{t.modoVigilanciaTitulo}</EnlacePie>
            </ColumnaPie>

            <ColumnaPie titulo={t.pieMetodo}>
              <EnlacePie ancla="#senales">{t.pieSenales}</EnlacePie>
              <EnlacePie ancla="#fuentes">{t.pieFuentes}</EnlacePie>
              <EnlacePie ancla="#etica">{t.pieEtica}</EnlacePie>
            </ColumnaPie>

            <ColumnaPie titulo={t.pieProyecto}>
              <li className="text-[var(--color-texto-tenue)]">{t.pieHackathon}</li>
              <li className="text-[var(--color-texto-tenue)]">{t.pieTrack}</li>
              <li>
                <a
                  href={CROMA}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="text-[var(--color-texto-tenue)] transition-colors hover:text-[var(--color-lumen)]"
                >
                  {t.fuentesVia}
                </a>
              </li>
            </ColumnaPie>
          </div>

          <div className="mt-16 flex flex-col gap-3 border-t border-[var(--color-borde)] pt-7 text-xs text-[var(--color-texto-tenue)] sm:flex-row sm:items-center sm:justify-between">
            <p>{t.pieDerechos}</p>
            <p>{DISCLAIMER_LANDING[idioma]}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

type Textos = ReturnType<typeof useIdioma>['t']

/** Sólida siempre: sobre la pintura los enlaces no se leían. */
function Barra({
  t,
  idioma,
  cambiar,
}: {
  t: Textos
  idioma: 'es' | 'en'
  cambiar: (i: 'es' | 'en') => void
}) {
  return (
    <header
      className="sticky top-0 z-30 border-b border-[var(--color-borde)] bg-[var(--color-fondo)]"
    >
      <nav className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
        <Link to="/" aria-label="Lumen">
          <Marca tamano="sm" />
        </Link>

        <div className="hidden items-center gap-9 text-sm lg:flex">
          <a href="#modos" className="text-[var(--color-texto)]/80 transition-colors hover:text-[var(--color-texto)]">
            {t.navProducto}
          </a>
          <a href="#senales" className="text-[var(--color-texto)]/80 transition-colors hover:text-[var(--color-texto)]">
            {t.navSenales}
          </a>
          <a href="#fuentes" className="text-[var(--color-texto)]/80 transition-colors hover:text-[var(--color-texto)]">
            {t.navFuentes}
          </a>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex border border-[var(--color-borde)] text-[0.7rem]">
            {(['es', 'en'] as const).map((codigo) => (
              <button
                key={codigo}
                onClick={() => cambiar(codigo)}
                aria-pressed={idioma === codigo}
                className={`px-2.5 py-1.5 uppercase tracking-[0.12em] transition ${
                  idioma === codigo
                    ? 'bg-[var(--color-lumen)] font-semibold text-[var(--color-lumen-texto)]'
                    : 'text-[var(--color-texto-tenue)] hover:text-[var(--color-texto)]'
                }`}
              >
                {codigo}
              </button>
            ))}
          </div>
          <Boton a="/app/vigilancia">
            {t.navEntrar}
          </Boton>
        </div>
      </nav>
    </header>
  )
}

function ColumnaPie({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-[0.66rem] font-medium uppercase tracking-[0.28em] text-[var(--color-lumen)]">
        {titulo}
      </h3>
      <ul className="mt-5 space-y-3 text-sm">{children}</ul>
    </div>
  )
}

function EnlacePie({
  a,
  ancla,
  children,
}: {
  a?: string
  ancla?: string
  children: React.ReactNode
}) {
  const clases = 'text-[var(--color-texto-tenue)] transition-colors hover:text-[var(--color-lumen)]'
  return (
    <li>
      {a ? (
        <Link to={a} className={clases}>
          {children}
        </Link>
      ) : (
        <a href={ancla} className={clases}>
          {children}
        </a>
      )}
    </li>
  )
}
