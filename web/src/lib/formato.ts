/** Formateo para lectura ciudadana: pesos sin decimales y fechas en palabras. */

const PESOS = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

/**
 * Las fechas del contrato que no traen hora (`Caso.fecha`) son días de
 * calendario, no instantes: se formatean en UTC porque `new Date('2026-08-14')`
 * es medianoche UTC y en Colombia se pintaría como el 13.
 */
const FECHA = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'UTC',
})

const FECHA_LOCAL = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

const SOLO_FECHA = /^\d{4}-\d{2}-\d{2}$/

const FECHA_HORA = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

export function pesos(valor?: number | null): string {
  if (valor == null) return '—'
  return PESOS.format(valor)
}

/** "4.200 millones" se lee mejor que "$4.200.000.000" en un titular. */
export function pesosCortos(valor?: number | null): string {
  if (valor == null) return '—'
  if (valor >= 1_000_000_000) return `$${(valor / 1_000_000_000).toLocaleString('es-CO', { maximumFractionDigits: 1 })} mil millones`
  if (valor >= 1_000_000) return `$${(valor / 1_000_000).toLocaleString('es-CO', { maximumFractionDigits: 0 })} millones`
  return PESOS.format(valor)
}

export function fecha(iso?: string | null): string {
  if (!iso) return '—'
  const formato = SOLO_FECHA.test(iso) ? FECHA : FECHA_LOCAL
  return formato.format(new Date(iso))
}

export function fechaHora(iso?: string | null): string {
  if (!iso) return '—'
  return FECHA_HORA.format(new Date(iso))
}
