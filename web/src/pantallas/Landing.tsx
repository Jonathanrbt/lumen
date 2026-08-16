/**
 * La landing: la puerta de entrada, en español e inglés.
 *
 * El producto está en español porque es para ciudadanía colombiana. Esta página
 * es bilingüe porque el jurado y los compradores (multilaterales, filantropía
 * cívica, medios) no lo son.
 */
import { Link } from 'react-router'
import { DISCLAIMER_LANDING, useIdioma } from '../lib/copy'
import { Orbe } from '../componentes/Orbe'

export function PantallaLanding() {
  const { idioma, cambiar, t } = useIdioma()

  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-10 border-b border-[var(--color-borde)] bg-[color-mix(in_oklch,var(--color-fondo)_85%,transparent)] backdrop-blur">
        <nav className="mx-auto flex max-w-5xl items-center justify-between px-5 py-3">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <span
              className="h-4 w-4 rounded-full"
              style={{
                background:
                  'radial-gradient(circle at 35% 30%, oklch(1 0 0 / 0.7), var(--color-lumen))',
              }}
            />
            Lumen
          </Link>

          <div className="flex items-center gap-3">
            <div className="flex rounded-full border border-[var(--color-borde)] text-xs">
              {(['es', 'en'] as const).map((codigo) => (
                <button
                  key={codigo}
                  onClick={() => cambiar(codigo)}
                  aria-pressed={idioma === codigo}
                  className={`rounded-full px-2.5 py-1 uppercase transition ${
                    idioma === codigo
                      ? 'bg-[var(--color-lumen)] text-[oklch(0.2_0.02_260)] font-semibold'
                      : 'text-[var(--color-texto-tenue)] hover:text-[var(--color-texto)]'
                  }`}
                >
                  {codigo}
                </button>
              ))}
            </div>
            <Link
              to="/app/vigilancia"
              className="rounded-lg bg-[var(--color-lumen)] px-3 py-1.5 text-sm font-medium text-[oklch(0.2_0.02_260)] hover:opacity-90"
            >
              {t.navEntrar}
            </Link>
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-5xl px-5">
        <section className="py-16 sm:py-24">
          <p className="inline-flex rounded-full border border-[var(--color-borde)] px-3 py-1 text-xs text-[var(--color-texto-tenue)]">
            {t.heroEtiqueta}
          </p>
          <h1 className="mt-6 max-w-3xl text-4xl font-semibold leading-[1.1] sm:text-6xl">
            {t.heroTitulo}
            <br />
            <span className="text-[var(--color-lumen)]">{t.heroTituloAcento}</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-[var(--color-texto-tenue)]">
            {t.heroBajada}
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              to="/app/vigilancia"
              className="rounded-lg bg-[var(--color-lumen)] px-5 py-3 font-medium text-[oklch(0.2_0.02_260)] hover:opacity-90"
            >
              {t.heroCta}
            </Link>
            <Link
              to="/app/emergencia"
              className="rounded-lg border border-[var(--color-borde)] px-5 py-3 font-medium hover:bg-[var(--color-superficie)]"
            >
              {t.heroCtaSecundaria}
            </Link>
            <span className="text-sm text-[var(--color-texto-tenue)]">{t.heroNota}</span>
          </div>
          <p className="mt-8 max-w-xl rounded-lg border border-[var(--color-borde)] bg-[var(--color-superficie)] px-3 py-2 text-xs text-[var(--color-texto-tenue)]">
            {DISCLAIMER_LANDING[idioma]}
          </p>
        </section>

        <section className="border-t border-[var(--color-borde)] py-14">
          <h2 className="max-w-2xl text-2xl font-semibold sm:text-3xl">{t.problemaTitulo}</h2>
          <p className="mt-3 max-w-2xl leading-relaxed text-[var(--color-texto-tenue)]">
            {t.problemaTexto}
          </p>
          <dl className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {t.cifras.map((cifra) => (
              <div
                key={cifra.etiqueta}
                className="rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-4"
              >
                <dt className="text-2xl font-semibold text-[var(--color-lumen)]">{cifra.dato}</dt>
                <dd className="mt-1 text-xs text-[var(--color-texto-tenue)]">{cifra.etiqueta}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section id="producto" className="border-t border-[var(--color-borde)] py-14">
          <h2 className="text-2xl font-semibold sm:text-3xl">{t.modosTitulo}</h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {[
              { titulo: t.modoEmergenciaTitulo, texto: t.modoEmergenciaTexto, a: '/app/emergencia' },
              { titulo: t.modoVigilanciaTitulo, texto: t.modoVigilanciaTexto, a: '/app/vigilancia' },
            ].map((modo) => (
              <Link
                key={modo.titulo}
                to={modo.a}
                className="rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-6 transition hover:border-[var(--color-lumen)]"
              >
                <h3 className="text-lg font-semibold">{modo.titulo}</h3>
                <p className="mt-2 text-sm leading-relaxed text-[var(--color-texto-tenue)]">
                  {modo.texto}
                </p>
              </Link>
            ))}
          </div>
        </section>

        <section id="senales" className="border-t border-[var(--color-borde)] py-14">
          <h2 className="text-2xl font-semibold sm:text-3xl">{t.senalesTitulo}</h2>
          <p className="mt-3 max-w-2xl leading-relaxed text-[var(--color-texto-tenue)]">
            {t.senalesBajada}
          </p>
          <ul className="mt-8 grid gap-3 sm:grid-cols-2">
            {t.senales.map((senal) => (
              <li
                key={senal.codigo}
                className="rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-4"
              >
                <div className="flex items-center gap-2">
                  <span className="rounded bg-[var(--color-superficie-alta)] px-1.5 py-0.5 font-mono text-xs text-[var(--color-texto-tenue)]">
                    {senal.codigo}
                  </span>
                  <h3 className="font-medium">{senal.nombre}</h3>
                </div>
                <p className="mt-2 text-sm text-[var(--color-texto-tenue)]">{senal.regla}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="border-t border-[var(--color-borde)] py-14">
          <div className="flex flex-col gap-8 sm:flex-row sm:items-start">
            <div className="shrink-0">
              <Orbe tamano="lg" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold sm:text-3xl">{t.iaTitulo}</h2>
              <p className="mt-3 max-w-2xl leading-relaxed text-[var(--color-texto-tenue)]">
                {t.iaTexto}
              </p>
              <p className="mt-4 border-l-2 border-[var(--color-lumen)] pl-4 text-sm">
                {t.iaNota}
              </p>
            </div>
          </div>
        </section>

        <section className="border-t border-[var(--color-borde)] py-14">
          <h2 className="text-2xl font-semibold sm:text-3xl">{t.eticaTitulo}</h2>
          <ul className="mt-6 space-y-3">
            {t.etica.map((linea) => (
              <li key={linea} className="flex gap-3 leading-relaxed">
                <span className="text-[var(--color-lumen)]" aria-hidden>
                  —
                </span>
                <span className="text-[var(--color-texto-tenue)]">{linea}</span>
              </li>
            ))}
          </ul>
        </section>

        <section id="fuentes" className="border-t border-[var(--color-borde)] py-14">
          <h2 className="text-2xl font-semibold sm:text-3xl">{t.fuentesTitulo}</h2>
          <p className="mt-3 max-w-2xl leading-relaxed text-[var(--color-texto-tenue)]">
            {t.fuentesTexto}
          </p>
        </section>

        <section className="border-t border-[var(--color-borde)] py-20 text-center">
          <h2 className="text-2xl font-semibold sm:text-3xl">{t.cierreTitulo}</h2>
          <Link
            to="/app/vigilancia"
            className="mt-6 inline-block rounded-lg bg-[var(--color-lumen)] px-6 py-3 font-medium text-[oklch(0.2_0.02_260)] hover:opacity-90"
          >
            {t.cierreCta}
          </Link>
        </section>
      </main>

      <footer className="border-t border-[var(--color-borde)] py-8">
        <div className="mx-auto max-w-5xl px-5 text-sm text-[var(--color-texto-tenue)]">
          <p className="font-medium text-[var(--color-texto)]">Lumen</p>
          <p className="mt-1">{t.piePitch}</p>
          <p className="mt-3 text-xs">{DISCLAIMER_LANDING[idioma]}</p>
        </div>
      </footer>
    </div>
  )
}
