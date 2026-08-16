/** Piezas compartidas por la landing, la ficha, el chat y la alerta. */
import { Link } from 'react-router'
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
      className={`inline-flex items-center gap-2 border font-medium ${
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
    <p className="border border-[var(--color-borde)] bg-[var(--color-superficie)] px-3 py-2 text-xs leading-relaxed text-[var(--color-texto-tenue)]">
      {texto}
    </p>
  )
}

/** Antetítulo en versalitas con su filete, delante de un titular. */
export function Rubrica({
  children,
  centrada = false,
}: {
  children: React.ReactNode
  centrada?: boolean
}) {
  return (
    <p
      className={`flex items-center gap-3 text-[0.66rem] font-medium uppercase tracking-[0.28em] text-[var(--color-lumen)] ${
        centrada ? 'justify-center' : ''
      }`}
    >
      <span className="h-px w-7 bg-current opacity-50" />
      {children}
    </p>
  )
}

const VARIANTE = {
  principal: 'bg-[var(--color-lumen)] text-[var(--color-lumen-texto)] hover:opacity-90',
  secundario:
    'border border-[var(--color-borde)] text-[var(--color-texto)] hover:bg-[var(--color-superficie-alta)]',
  // Para posarse encima de una imagen sin taparla.
  velado:
    'border border-[var(--color-borde)] bg-[color-mix(in_oklch,var(--color-fondo)_72%,transparent)] text-[var(--color-texto)] backdrop-blur-sm hover:bg-[var(--color-fondo)]',
}

/* Versalitas espaciadas: la misma voz que las rúbricas de sección. */
const TAMANO = {
  md: 'px-5 py-2.5 text-[0.7rem] uppercase tracking-[0.14em]',
  lg: 'px-7 py-3.5 text-[0.78rem] uppercase tracking-[0.14em]',
}

/**
 * Con `a` se pinta como enlace de navegación; sin él, como botón.
 * Esquina viva: el rectángulo va con la arquitectura del resto.
 */
export function Boton({
  children,
  a,
  onClick,
  variante = 'principal',
  tamano = 'md',
  type = 'button',
  disabled,
}: {
  children: React.ReactNode
  a?: string
  onClick?: () => void
  variante?: keyof typeof VARIANTE
  tamano?: keyof typeof TAMANO
  type?: 'button' | 'submit'
  disabled?: boolean
}) {
  const estilos = `inline-flex items-center justify-center gap-2 rounded-none font-medium transition disabled:opacity-40 ${
    TAMANO[tamano]
  } ${VARIANTE[variante]}`

  if (a) {
    return (
      <Link to={a} className={estilos}>
        {children}
      </Link>
    )
  }

  return (
    <button type={type} onClick={onClick} disabled={disabled} className={estilos}>
      {children}
    </button>
  )
}
