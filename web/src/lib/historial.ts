/**
 * Las consultas de la sesión, que el panel lateral lista y el chat escribe.
 *
 * Vive en memoria: no hay tabla de conversaciones en el contrato de la API y
 * un veedor no crea cuenta para entrar. Al recargar se empieza limpio.
 */
import { createContext, use, useRef, useState } from 'react'
import type { ChatResponse, Lectura } from './tipos'

export type Mensaje =
  | { rol: 'usuario'; texto: string }
  | { rol: 'lumen'; respuesta: ChatResponse }
  /** La ruta alterna del Flujo B: alguien subió el PDF de una justificación. */
  | { rol: 'lector'; archivo: string; lectura?: Lectura; error?: string }

export type Consulta = {
  id: string
  titulo: string
  mensajes: Mensaje[]
  /** Lo que el backend ya resolvió, para no volver a preguntar quién es quién. */
  contexto?: Record<string, unknown>
}

type Historial = {
  consultas: Consulta[]
  activa?: Consulta
  abrir: (id: string) => void
  nueva: () => void
  guardar: (cambio: Partial<Omit<Consulta, 'id'>>) => void
}

export const HistorialContext = createContext<Historial>({
  consultas: [],
  abrir: () => {},
  nueva: () => {},
  guardar: () => {},
})

export const useHistorial = () => use(HistorialContext)

export function useEstadoHistorial(): Historial {
  const [consultas, setConsultas] = useState<Consulta[]>([])
  const [activaId, setActivaId] = useState<string>()
  /**
   * La respuesta del backend llega uno o dos segundos después de la pregunta y
   * trae capturado el id de entonces. La referencia lo mantiene al día sin
   * esperar al siguiente render, para que la respuesta caiga en la consulta que
   * la pidió y no abra una nueva.
   */
  const abierta = useRef<string>(undefined)

  function apuntar(id?: string) {
    abierta.current = id
    setActivaId(id)
  }

  /** Sin consulta abierta, el primer guardado la crea. */
  function guardar(cambio: Partial<Omit<Consulta, 'id'>>) {
    const id = abierta.current
    if (!id) {
      const nuevoId = crypto.randomUUID()
      apuntar(nuevoId)
      setConsultas((previas) => [
        { id: nuevoId, titulo: 'Consulta', mensajes: [], ...cambio },
        ...previas,
      ])
      return
    }
    setConsultas((previas) => previas.map((c) => (c.id === id ? { ...c, ...cambio } : c)))
  }

  return {
    consultas,
    activa: consultas.find((c) => c.id === activaId),
    abrir: apuntar,
    nueva: () => apuntar(undefined),
    guardar,
  }
}
