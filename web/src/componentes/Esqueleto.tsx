/**
 * Esqueletos de carga: la caja con la forma del contenido que va a llegar.
 *
 * No es adorno. Analizar un caso toca Croma y dos modelos de lenguaje, así que
 * la espera es real y visible; una pantalla en blanco durante ese rato parece
 * una aplicación rota.
 */

export function Barra({ ancho = 'w-full', alto = 'h-4' }: { ancho?: string; alto?: string }) {
  return <div className={`esqueleto rounded ${ancho} ${alto}`} />
}

/** Con la misma silueta que TarjetaSenal: título, regla, dato y fuente. */
export function EsqueletoSenal() {
  return (
    <div className="rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-4">
      <div className="flex items-center gap-2">
        <Barra ancho="w-12" alto="h-5" />
        <Barra ancho="w-40" alto="h-5" />
      </div>
      <div className="mt-3 space-y-2">
        <Barra />
        <Barra ancho="w-4/5" />
      </div>
      <div className="mt-4">
        <Barra ancho="w-56" alto="h-3" />
      </div>
    </div>
  )
}

export function EsqueletoCaso() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Cargando el caso">
      <div className="space-y-3">
        <Barra ancho="w-32" alto="h-6" />
        <Barra ancho="w-3/4" alto="h-8" />
        <Barra ancho="w-1/2" />
      </div>
      <div className="space-y-3">
        <EsqueletoSenal />
        <EsqueletoSenal />
      </div>
    </div>
  )
}

export function EsqueletoArtefacto() {
  return (
    <div className="space-y-3" aria-busy="true" aria-label="Redactando el documento">
      <Barra ancho="w-2/3" alto="h-6" />
      <Barra />
      <Barra />
      <Barra ancho="w-5/6" />
      <div className="h-2" />
      <Barra ancho="w-1/3" alto="h-5" />
      <Barra />
      <Barra ancho="w-4/5" />
    </div>
  )
}
