/**
 * La tarjeta de señal. El componente central del producto.
 *
 * La usan la ficha del caso, el chat y la alerta: el chat no es una pantalla
 * nueva, es otro envoltorio sobre esto mismo.
 */
import { Fuente, Nivel } from './Basicos'
import type { Senal } from '../lib/tipos'

/** `dias_transcurridos` no se le enseña a nadie tal cual. */
function humanizar(clave: string): string {
  return clave.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase())
}

function valorLegible(valor: unknown): string {
  if (valor == null) return '—'
  if (typeof valor === 'number') return valor.toLocaleString('es-CO')
  return String(valor)
}

export function TarjetaSenal({ senal }: { senal: Senal }) {
  return (
    <article className="rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-4">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="rounded bg-[var(--color-superficie-alta)] px-1.5 py-0.5 font-mono text-xs text-[var(--color-texto-tenue)]">
            {senal.codigo}
          </span>
          <h3 className="font-semibold">{senal.nombre}</h3>
        </div>
        <Nivel nivel={senal.nivel} compacto />
      </header>

      {/* La regla contada como la entendería un ciudadano, no la expresión. */}
      <p className="mt-3 leading-relaxed">{senal.regla_legible}</p>

      {Object.keys(senal.datos_usados).length > 0 && (
        <dl className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[var(--color-texto-tenue)]">
          {Object.entries(senal.datos_usados).map(([clave, valor]) => (
            <div key={clave} className="flex gap-1">
              <dt>{humanizar(clave)}:</dt>
              <dd className="font-medium text-[var(--color-texto)]">{valorLegible(valor)}</dd>
            </div>
          ))}
        </dl>
      )}

      <footer className="mt-3 border-t border-[var(--color-borde)] pt-3">
        <Fuente fuente={senal.fuente} />
      </footer>
    </article>
  )
}
