/**
 * Espejo en TypeScript del contrato compartido.
 * Fuente de verdad: `api/lumen/contracts/modelos.py` y `docs/CONTRATO-API.md`.
 * Si el backend cambia un campo, se cambia aquí en el mismo bloque.
 */

export type NivelAtencion = 'bajo' | 'medio' | 'alto'
export type ModoCaso = 'emergencia' | 'vigilancia'
export type TipoActor = 'empresa' | 'persona' | 'entidad'
export type Veredicto = 'solida' | 'generica' | 'sin_relacion'
export type CodigoSenal = 'S1' | 'S2' | 'S3' | 'S4' | 'S5' | 'S6' | 'S7' | 'S8' | 'S10'
export type TipoArtefacto =
  | 'paquete_evidencia'
  | 'derecho_peticion'
  | 'informe_veeduria'
  | 'guia_denuncia'

/** Obligatoria dentro de toda señal y toda arista. Sin fuente no se publica nada. */
export interface Fuente {
  herramienta_croma: string
  url_oficial: string
  consultado_en: string
}

export interface Candidato {
  nombre: string
  nit?: string | null
  ciudad?: string | null
  actividad?: string | null
  tipo: TipoActor
}

export interface Senal {
  codigo: CodigoSenal
  nombre: string
  nivel: NivelAtencion
  regla_legible: string
  datos_usados: Record<string, unknown>
  fuente: Fuente
}

/** Si `cita_textual` viene vacía, `no_concluye_por` explica por qué. */
export interface PuntoLectura {
  pregunta: string
  hallazgo: string
  cita_textual?: string | null
  pagina?: number | null
  no_concluye_por?: string | null
}

export interface Lectura {
  veredicto: Veredicto
  puntos: PuntoLectura[]
  documento_url?: string | null
  analizado_en?: string | null
}

export interface Actor {
  id: string
  tipo: TipoActor
  nombre: string
  nit?: string | null
  rol?: string | null
}

export interface Arista {
  origen: string
  destino: string
  tipo: string
  fuente: Fuente
}

export interface Grafo {
  nodos: Actor[]
  aristas: Arista[]
}

export interface Caso {
  id: string
  modo: ModoCaso
  entidad: string
  proveedor?: string | null
  municipio?: string | null
  departamento?: string | null
  valor?: number | null
  objeto?: string | null
  fecha?: string | null
  nivel_atencion: NivelAtencion
  senales: Senal[]
  lectura?: Lectura | null
  grafo?: Grafo | null
  narracion?: string | null
  disclaimer: string
  generado_en?: string | null
}

export interface Artefacto {
  tipo: TipoArtefacto
  titulo: string
  cuerpo_markdown: string
  normas_citadas: string[]
  destinatario?: string | null
  caso_id?: string | null
}

export interface ChatResponse {
  narracion: string
  caso?: Caso | null
  candidatos?: Candidato[] | null
  siguientes_pasos: string[]
}

export interface AlertaResponse {
  estado: string
  detalle?: string | null
}

/** Texto del parche v3.1 — fuente única en `api/lumen/contracts/modelos.py`. */
export const DISCLAIMER = 'Una señal no es prueba de irregularidad. Es un motivo para preguntar.'
