/**
 * Iconografía clásica: templo, ánfora, rollo, clepsidra y busto.
 *
 * Dibujadas a mano sobre una retícula de 24 para que compartan grosor y
 * proporción con las grecas y no con una librería de iconos genérica.
 */
type Props = { className?: string }

function Trazo({ children, className = '' }: Props & { children: React.ReactNode }) {
  return (
    <svg
      aria-hidden
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.25"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`h-full w-full ${className}`}
    >
      {children}
    </svg>
  )
}

/** Entidad pública: la fachada con su frontón y sus columnas. */
export function Templo(props: Props) {
  return (
    <Trazo {...props}>
      <path d="M2.5 9.5 12 3.5 21.5 9.5" />
      <path d="M4 11H20" />
      <path d="M6.5 11.5v7M12 11.5v7M17.5 11.5v7" />
      <path d="M3.5 19.5h17" />
    </Trazo>
  )
}

/** Empresa: el ánfora del comercio. */
export function Anfora(props: Props) {
  return (
    <Trazo {...props}>
      <path d="M10 3h4" />
      <path d="M10.5 3.5C10.5 6 8 7 8 11c0 4 1.5 6 4 9.5 2.5-3.5 4-5.5 4-9.5 0-4-2.5-5-2.5-7.5" />
      <path d="M8.6 6.4C6.2 7 5.7 10 7.6 11" />
      <path d="M15.4 6.4C17.8 7 18.3 10 16.4 11" />
    </Trazo>
  )
}

/** Contrato: el rollo con su vuelta al pie. */
export function Rollo(props: Props) {
  return (
    <Trazo {...props}>
      <path d="M6 3h12v14H6z" />
      <path d="M6 17c0 2 1.6 3.5 3.6 3.5H18" />
      <path d="M9 7h6M9 10h6M9 13h4" />
    </Trazo>
  )
}

/** Emergencia pasada: la clepsidra, el tiempo que ya corrió. */
export function Clepsidra(props: Props) {
  return (
    <Trazo {...props}>
      <path d="M6 3h12M6 21h12" />
      <path d="M8 3c0 5 4 7.5 4 9s-4 4-4 9" />
      <path d="M16 3c0 5-4 7.5-4 9s4 4 4 9" />
    </Trazo>
  )
}

/** Persona: el busto sobre su plinto. */
export function Busto(props: Props) {
  return (
    <Trazo {...props}>
      <circle cx="12" cy="7.5" r="3.5" />
      <path d="M6 18c0-3.6 2.7-6.5 6-6.5s6 2.9 6 6.5" />
      <path d="M4.5 20.5h15" />
    </Trazo>
  )
}
