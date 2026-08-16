/** Piezas compartidas por la ficha, el chat y la alerta. */
import { fechaHora } from '../lib/formato'
import { DISCLAIMER, type Fuente as TipoFuente, type NivelAtencion } from '../lib/tipos'

const NIVEL = {
  bajo: { texto: 'Atención baja', color: 'var(--color-bajo)' },
  medio: { texto: 'Atención media', color: 'var(--color-medio)' },
  alto: { texto: 'Atención alta', color: 'var(--color-alto)' },
}

/**
 * Tres estados con color. Nunca un score.
 * Un "78 % de probabilidad de corrupción" es justo lo que este producto se niega
 * a publicar, así que aquí no hay ningún número que pintar.
 */
export function Nivel({ nivel, compacto = false }: { nivel: NivelAtencion; compacto?: boolean }) {
  const { texto, color } = NIVEL[nivel]
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border font-medium ${
        compacto ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
      }`}
      style={{ color, borderColor: color, backgroundColor: `color-mix(in oklch, ${color} 12%, transparent)` }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {texto}
    </span>
  )
}

/**
 * El enlace a la fuente oficial con su fecha de consulta.
 * Va pegado al dato, no en un pie de página: es lo que hace verificable la señal.
 */
export function Fuente({ fuente }: { fuente: TipoFuente }) {
  return (
    <a
      href={fuente.url_oficial}
      target="_blank"
      rel="noreferrer noopener"
      className="group inline-flex flex-wrap items-center gap-x-1.5 text-xs text-[var(--color-texto-tenue)] hover:text-[var(--color-lumen)]"
    >
      <span className="underline decoration-dotted underline-offset-2">Fuente oficial</span>
      <span aria-hidden>·</span>
      <code className="rounded bg-[var(--color-superficie-alta)] px-1 py-0.5">
        {fuente.herramienta_croma}
      </code>
      <span aria-hidden>·</span>
      <span>consultado el {fechaHora(fuente.consultado_en)}</span>
    </a>
  )
}

/** Visible en cada resultado, no en el pie de página. */
export function Disclaimer({ texto = DISCLAIMER }: { texto?: string }) {
  return (
    <p className="rounded-lg border border-[var(--color-borde)] bg-[var(--color-superficie)] px-3 py-2 text-xs leading-relaxed text-[var(--color-texto-tenue)]">
      {texto}
    </p>
  )
}

export function Boton({
  children,
  onClick,
  variante = 'principal',
  type = 'button',
  disabled,
}: {
  children: React.ReactNode
  onClick?: () => void
  variante?: 'principal' | 'secundario'
  type?: 'button' | 'submit'
  disabled?: boolean
}) {
  const estilos =
    variante === 'principal'
      ? 'bg-[var(--color-lumen)] text-[oklch(0.2_0.02_260)] hover:opacity-90'
      : 'border border-[var(--color-borde)] text-[var(--color-texto)] hover:bg-[var(--color-superficie-alta)]'
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-40 ${estilos}`}
    >
      {children}
    </button>
  )
}
