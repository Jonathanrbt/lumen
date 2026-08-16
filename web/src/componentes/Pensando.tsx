/**
 * Lo que se ve mientras el agente resuelve, analiza o redacta.
 *
 * El orbe de `thinking-orbs` es monocromo y de puntos: toma la tinta del tema
 * y no mete un color más en una paleta que ya tiene dos.
 */
import { ThinkingOrb } from 'thinking-orbs'

type Estado = 'searching' | 'solving' | 'composing'

export function Pensando({
  etiqueta,
  estado = 'searching',
}: {
  etiqueta: string
  estado?: Estado
}) {
  return (
    <p
      className="flex items-center gap-3 text-sm text-[var(--color-texto-tenue)]"
      role="status"
      aria-live="polite"
    >
      <ThinkingOrb state={estado} size={20} theme="light" aria-label={etiqueta} />
      {etiqueta}
    </p>
  )
}
