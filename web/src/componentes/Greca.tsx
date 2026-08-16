/**
 * Greca: el meandro griego, como filete entre secciones de la landing.
 *
 * El patrón repite cada 28 px, así que los anchos múltiplos de 28 cierran el
 * dibujo. Toma el color de `currentColor`.
 */
import { useId } from 'react'

export function Greca({ className = '' }: { className?: string }) {
  const id = useId()

  return (
    <svg aria-hidden className={`h-4 ${className}`}>
      <defs>
        <pattern id={id} width="28" height="16" patternUnits="userSpaceOnUse">
          <path
            d="M0 15H28M6 15V4H22V11H12"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.25"
          />
        </pattern>
      </defs>
      <rect width="100%" height="16" fill={`url(#${id})`} />
    </svg>
  )
}
