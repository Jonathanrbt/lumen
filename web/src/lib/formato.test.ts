/**
 * El formateo de fechas y de plata es donde una herramienta de transparencia
 * pierde credibilidad más rápido: una fecha corrida un día no cuadra con la
 * fuente oficial que va enlazada al lado.
 */
import { describe, expect, it } from 'vitest'
import { fecha, fechaHora, pesos, pesosCortos } from './formato'

describe('fecha', () => {
  it('no corre el día de calendario hacia atrás por la zona horaria', () => {
    // `Caso.fecha` viene sin hora: es un día, no un instante.
    expect(fecha('2026-08-14')).toContain('14')
    expect(fecha('2026-01-01')).toContain('1 de enero de 2026')
  })

  it('respeta el desfase de los instantes con hora', () => {
    expect(fechaHora('2026-08-15T17:20:00-05:00')).toContain('15')
  })

  it('devuelve un guion cuando no hay dato', () => {
    expect(fecha(null)).toBe('—')
    expect(fecha(undefined)).toBe('—')
  })
})

describe('pesos', () => {
  it('no inventa decimales', () => {
    expect(pesos(4_200_000_000)).not.toContain(',00')
  })

  it('resume los miles de millones para un titular', () => {
    expect(pesosCortos(4_200_000_000)).toBe('$4,2 mil millones')
    expect(pesosCortos(35_000_000)).toBe('$35 millones')
  })

  it('devuelve un guion cuando el contrato no trae valor', () => {
    expect(pesos(null)).toBe('—')
    expect(pesosCortos(null)).toBe('—')
  })
})
