/**
 * Cliente de los nueve endpoints, con respaldo en los fixtures del repo.
 *
 * Sin `VITE_API_URL` la app corre entera contra `fixtures/`. Con la URL puesta
 * habla con la API real y solo cae al fixture si la red falla, para que un corte
 * a las 07:00 no deje la demo en blanco.
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

/** Deja ver el orbe y los esqueletos cuando no hay backend detrás. */
const espera = (ms: number) => new Promise((r) => setTimeout(r, ms))

async function pedir<T>(ruta: string, opciones: RequestInit, respaldo: T): Promise<T> {
  if (!BASE) {
    await espera(900)
    return respaldo
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
    return respaldo
  }
}

export const api = {
  /** POST /chat — única ruta exclusiva del Modo Vigilancia. */
  chat(mensaje: string, contexto?: Record<string, unknown>) {
    // Sin backend, un mensaje con NIT ya viene desambiguado y el resto pregunta.
    const respaldo = contexto?.nit
      ? FIXTURES.chatRespuesta
      : FIXTURES.chatDesambiguacion
    return pedir<ChatResponse>(
      '/chat',
      { method: 'POST', body: JSON.stringify({ mensaje, contexto }) },
      respaldo,
    )
  },

  /** GET /caso/{id} */
  caso(id: string) {
    return pedir<Caso>(`/caso/${id}`, { method: 'GET' }, FIXTURES.caso)
  },

  /** POST /analizar */
  analizar(llaves: { nit?: string; entidad_id?: string; contrato_id?: string }) {
    return pedir<Caso>(
      '/analizar',
      { method: 'POST', body: JSON.stringify(llaves) },
      FIXTURES.caso,
    )
  },

  /** POST /accion — convierte el hallazgo en algo que se puede enviar. */
  accion(caso_id: string, tipo: TipoArtefacto) {
    return pedir<Artefacto>(
      '/accion',
      { method: 'POST', body: JSON.stringify({ caso_id, tipo }) },
      FIXTURES.artefacto,
    )
  },

  /** GET /monitor/nuevos — los casos que armó el Modo Emergencia. */
  monitor(desde?: string) {
    const query = desde ? `?desde=${encodeURIComponent(desde)}` : ''
    return pedir<Caso[]>(`/monitor/nuevos${query}`, { method: 'GET' }, [FIXTURES.caso])
  },
}
