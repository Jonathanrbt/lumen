/**
 * Orbe pensante: lo que se ve mientras el agente resuelve, analiza y narra.
 *
 * Es CSS puro — gradientes cónicos girando bajo un desenfoque — porque una
 * librería de shaders pesa más que toda la pantalla del chat y esto se graba
 * en un video de 60 segundos a tamaño de teléfono.
 */

type Props = {
  tamano?: 'sm' | 'md' | 'lg'
  etiqueta?: string
}

const TAMANOS = {
  sm: 'h-8 w-8',
  md: 'h-16 w-16',
  lg: 'h-28 w-28',
}

export function Orbe({ tamano = 'md', etiqueta }: Props) {
  return (
    <div className="flex items-center gap-3" role="status" aria-live="polite">
      <div className={`relative ${TAMANOS[tamano]} shrink-0`}>
        {/* Halo exterior: respira. */}
        <div
          className="absolute inset-0 rounded-full blur-xl opacity-70"
          style={{
            background:
              'radial-gradient(circle at 50% 50%, var(--color-lumen), transparent 70%)',
            animation: 'orbe-respira 2.8s ease-in-out infinite',
          }}
        />
        {/* Núcleo: gradiente cónico girando. */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background:
              'conic-gradient(from 0deg, var(--color-lumen), oklch(0.7 0.16 30), oklch(0.75 0.13 200), var(--color-lumen))',
            animation: 'orbe-giro 3.2s linear infinite',
            filter: 'blur(2px)',
          }}
        />
        {/* Brillo especular, para que se lea como esfera y no como disco. */}
        <div
          className="absolute inset-0 rounded-full mix-blend-screen"
          style={{
            background:
              'radial-gradient(circle at 35% 30%, oklch(1 0 0 / 0.55), transparent 45%)',
          }}
        />
        {/* Hueco central: le da profundidad al anillo. */}
        <div
          className="absolute rounded-full inset-[22%]"
          style={{
            background: 'var(--color-fondo)',
            animation: 'orbe-respira 2.8s ease-in-out infinite reverse',
          }}
        />
      </div>
      {etiqueta && (
        <span className="text-sm text-[var(--color-texto-tenue)]">{etiqueta}</span>
      )}
      <span className="sr-only">Procesando</span>
    </div>
  )
}
