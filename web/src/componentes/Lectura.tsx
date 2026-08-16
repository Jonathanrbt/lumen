/**
 * El lector de justificaciones de urgencia manifiesta. La feature estrella.
 *
 * Cada punto se pinta de dos maneras distintas a propósito: con cita textual
 * cuando el modelo pudo sustentarlo, y como "no concluye" cuando no pudo. Si el
 * modelo no cita, no afirma — y aquí se ve que no afirmó.
 */
import { fecha } from '../lib/formato'
import type { Lectura as TipoLectura, Veredicto } from '../lib/tipos'

const VEREDICTO: Record<Veredicto, { texto: string; detalle: string; color: string }> = {
  solida: {
    texto: 'Justificación sólida',
    detalle: 'El documento relaciona el contrato con daños concretos de la emergencia.',
    color: 'var(--color-bajo)',
  },
  generica: {
    texto: 'Justificación genérica',
    detalle: 'El documento usa lenguaje de plantilla y no señala daños concretos.',
    color: 'var(--color-medio)',
  },
  sin_relacion: {
    texto: 'Sin relación con la emergencia',
    detalle: 'El objeto contratado no se conecta con los hechos que motivaron la urgencia.',
    color: 'var(--color-alto)',
  },
}

export function Lectura({ lectura }: { lectura: TipoLectura }) {
  const v = VEREDICTO[lectura.veredicto]

  return (
    <section className="rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-4">
      <header>
        <p className="text-xs uppercase tracking-wide text-[var(--color-texto-tenue)]">
          Lectura de la justificación de urgencia
        </p>
        <h3 className="mt-1 text-lg font-semibold" style={{ color: v.color }}>
          {v.texto}
        </h3>
        <p className="mt-1 text-sm text-[var(--color-texto-tenue)]">{v.detalle}</p>
      </header>

      <ol className="mt-4 space-y-4">
        {lectura.puntos.map((punto, i) => (
          <li key={i} className="border-l-2 border-[var(--color-borde)] pl-3">
            <p className="text-sm font-medium">{punto.pregunta}</p>
            <p className="mt-1 text-sm text-[var(--color-texto-tenue)]">{punto.hallazgo}</p>

            {punto.cita_textual ? (
              <blockquote className="mt-2 rounded bg-[var(--color-superficie-alta)] px-3 py-2 text-sm italic">
                «{punto.cita_textual}»
                {punto.pagina != null && (
                  <cite className="ml-1 not-italic text-xs text-[var(--color-texto-tenue)]">
                    — página {punto.pagina}
                  </cite>
                )}
              </blockquote>
            ) : (
              <p className="mt-2 rounded border border-dashed border-[var(--color-borde)] px-3 py-2 text-xs text-[var(--color-texto-tenue)]">
                <strong className="text-[var(--color-texto)]">No concluye.</strong>{' '}
                {punto.no_concluye_por}
              </p>
            )}
          </li>
        ))}
      </ol>

      {(lectura.documento_url || lectura.analizado_en) && (
        <footer className="mt-4 flex flex-wrap items-center gap-x-2 gap-y-1 border-t border-[var(--color-borde)] pt-3 text-xs text-[var(--color-texto-tenue)]">
          {lectura.documento_url && (
            <a
              href={lectura.documento_url}
              target="_blank"
              rel="noreferrer noopener"
              className="underline decoration-dotted underline-offset-2 hover:text-[var(--color-lumen)]"
            >
              Documento analizado
            </a>
          )}
          {lectura.analizado_en && <span>· analizado el {fecha(lectura.analizado_en)}</span>}
        </footer>
      )}
    </section>
  )
}
