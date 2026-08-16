/**
 * Cliente de los nueve endpoints, con respaldo en los fixtures del repo.
 *
 * Sin `VITE_API_URL` la app corre entera contra `fixtures/`. Con la URL puesta
 * habla con la API real y solo cae al fixture si la red falla, para que un corte
 * a las 07:00 no deje la demo en blanco.
 *
 * **El respaldo se anuncia.** Hasta el 16.ago caía al fixture en silencio: un
 * 503 de la API se pintaba exactamente igual que un dato real y solo quedaba un
 * `console.warn` que nadie mira durante una grabación. Eso es justo lo que
 * `AGENTS.md` prohíbe ("parece que funciona"), así que ahora cada caída marca
 * `respaldo` y la interfaz lo dice en pantalla.
 */
import casoFixture from '../../../fixtures/caso.json'
import artefactoFixture from '../../../fixtures/artefacto.json'
import chatDesambiguacionFixture from '../../../fixtures/chat_desambiguacion.json'
import chatRespuestaFixture from '../../../fixtures/chat_respuesta.json'
import lecturaFixture from '../../../fixtures/lectura.json'
import type { Artefacto, Caso, ChatResponse, Lectura, TipoArtefacto } from './tipos'

const BASE = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? ''

/** Los fixtures traen `_nota` para quien los lee; no es parte del contrato. */
function sinNota<T>(fixture: unknown): T {
  const { _nota, ...resto } = fixture as Record<string, unknown>
  void _nota
  return resto as T
}

export const FIXTURES = {
  caso: sinNota<Caso>(casoFixture),
  artefacto: sinNota<Artefacto>(artefactoFixture),
  chatDesambiguacion: sinNota<ChatResponse>(chatDesambiguacionFixture),
  chatRespuesta: sinNota<ChatResponse>(chatRespuestaFixture),
  lectura: sinNota<Lectura>(lecturaFixture),
}

export const usandoFixtures = BASE === ''

/**
 * Estado del respaldo, en un almacén mínimo para `useSyncExternalStore`.
 *
 * No entra en react-query ni en un contexto: cualquier llamada de cualquier
 * pantalla puede activarlo, y quien lo pinta (el aviso del marco) no es quien
 * lo dispara.
 */
type EstadoRespaldo = { activo: boolean; motivo?: string }

let estadoRespaldo: EstadoRespaldo = { activo: usandoFixtures }
const oyentes = new Set<() => void>()

function marcarRespaldo(motivo: string) {
  if (estadoRespaldo.activo && estadoRespaldo.motivo === motivo) return
  estadoRespaldo = { activo: true, motivo }
  oyentes.forEach((avisar) => avisar())
}

export const respaldo = {
  suscribir(oyente: () => void) {
    oyentes.add(oyente)
    return () => oyentes.delete(oyente)
  },
  leer: () => estadoRespaldo,
}

/** Deja ver el orbe y los esqueletos cuando no hay backend detrás. */
const espera = (ms: number) => new Promise((r) => setTimeout(r, ms))

async function pedir<T>(ruta: string, opciones: RequestInit, resguardo: T): Promise<T> {
  if (!BASE) {
    await espera(900)
    return resguardo
  }
  try {
    const res = await fetch(`${BASE}${ruta}`, {
      headers: { 'Content-Type': 'application/json' },
      ...opciones,
    })
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    return (await res.json()) as T
  } catch (error) {
    console.warn(`[lumen] ${ruta} falló, se responde con el fixture`, error)
    marcarRespaldo(`${ruta}: ${error instanceof Error ? error.message : 'sin respuesta'}`)
    return resguardo
  }
}

/**
 * El lector de justificaciones no tiene respaldo silencioso.
 *
 * Es la feature estrella (§3.1) y su salida es un veredicto sobre un documento
 * concreto que la persona acaba de subir: servir el fixture ahí sería enseñar
 * la lectura de OTRO documento como si fuera la suya. Si falla, falla.
 */
export class LectorNoDisponible extends Error {}

export const api = {
  /** POST /chat — única ruta exclusiva del Modo Vigilancia. */
  chat(mensaje: string, contexto?: Record<string, unknown>) {
    // Sin backend, un mensaje ya desambiguado responde con el caso y el resto pregunta.
    const resuelto = contexto?.nit || contexto?.entidad_id || contexto?.contrato_id
    const resguardo = resuelto ? FIXTURES.chatRespuesta : FIXTURES.chatDesambiguacion
    return pedir<ChatResponse>(
      '/chat',
      { method: 'POST', body: JSON.stringify({ mensaje, contexto }) },
      resguardo,
    )
  },

  /** GET /caso/{id} */
  caso(id: string) {
    return pedir<Caso>(`/caso/${id}`, { method: 'GET' }, FIXTURES.caso)
  },

  /** POST /analizar */
  analizar(llaves: { nit?: string; entidad_id?: string; contrato_id?: string }) {
    return pedir<Caso>('/analizar', { method: 'POST', body: JSON.stringify(llaves) }, FIXTURES.caso)
  },

  /** POST /accion — convierte el hallazgo en algo que se puede enviar. */
  accion(caso_id: string, tipo: TipoArtefacto) {
    return pedir<Artefacto>(
      '/accion',
      { method: 'POST', body: JSON.stringify({ caso_id, tipo }) },
      FIXTURES.artefacto,
    )
  },

  /**
   * POST /justificacion — el lector de urgencia manifiesta, sobre el PDF que
   * sube la persona. Ruta alterna del Flujo B (§4.6, paso 7): se salta la
   * resolución de entidades y entra directo al lector.
   *
   * Multipart, así que no lleva `Content-Type` a mano: el navegador tiene que
   * poner el suyo con el `boundary`.
   */
  async justificacion(archivo: File): Promise<Lectura> {
    if (!BASE) {
      await espera(900)
      return FIXTURES.lectura
    }
    const cuerpo = new FormData()
    cuerpo.append('archivo', archivo)

    const res = await fetch(`${BASE}/justificacion`, { method: 'POST', body: cuerpo })
    if (!res.ok) {
      const detalle = await res.json().catch(() => null)
      throw new LectorNoDisponible(detalle?.detail ?? `${res.status} ${res.statusText}`)
    }
    return (await res.json()) as Lectura
  },

  /** GET /monitor/nuevos — los casos que armó el Modo Emergencia. */
  monitor(desde?: string) {
    const query = desde ? `?desde=${encodeURIComponent(desde)}` : ''
    return pedir<Caso[]>(`/monitor/nuevos${query}`, { method: 'GET' }, [FIXTURES.caso])
  },
}
