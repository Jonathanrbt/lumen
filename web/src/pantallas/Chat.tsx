/**
 * Pantalla 3 — el chat del Modo Vigilancia, y la puerta de la herramienta.
 *
 * No es una pantalla nueva: es un envoltorio distinto sobre la ficha del caso y
 * las mismas tarjetas de señal. Entrada libre, candidatos como tarjetas que
 * elige la persona, y respuesta narrada.
 *
 * Los mensajes viven en el historial de la sesión, no aquí, para que el panel
 * lateral pueda volver a abrirlos.
 */
import { useMutation } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router'
import { api } from '../lib/api'
import { useHistorial } from '../lib/historial'
import { Boton } from '../componentes/Basicos'
import { Anfora, Busto, Clepsidra, Rollo, Templo } from '../componentes/Iconos'
import { EsqueletoSenal } from '../componentes/Esqueleto'
import { Lectura } from '../componentes/Lectura'
import { Pensando } from '../componentes/Pensando'
import { FichaCaso } from './Caso'
import buhoVuelo from '../assets/buho-vuelo.png'
import marca from '../assets/lumen-marca.png'
import type { Candidato, Caso, ChatResponse, Lectura as LecturaTipo } from '../lib/tipos'

/**
 * La lechuza se posa en el borde de la caja: en el PNG ya recortado sus garras
 * caen al 58 % del alto y las alas siguen hasta abajo. Se ancla por las garras
 * —de ahí este factor— y las alas quedan colgando sobre la caja. El ancho lo
 * pone `--buho`, que cambia por breakpoint.
 */
const BUHO_GARRAS = (730 / 720) * (1 - 0.583)

/**
 * Por dónde empezar. Las cuatro tienen que **resolver de verdad**: hasta el
 * 16.ago tres de ellas ("mi pueblo", "los escombros en Quimbaya", "Mocoa 2017")
 * morían en "no encontré nada", porque nombran cosas que nadie verificó contra
 * Croma. Ahora apuntan a entradas del catálogo curado (`api/lumen/ia/catalogo.py`),
 * que son las que el equipo sí validó a mano.
 */
const ARRANQUE = [
  {
    Icono: Templo,
    titulo: 'Mi municipio',
    texto: '¿Cómo está contratando la Gobernación del Chocó?',
  },
  { Icono: Anfora, titulo: 'Una empresa', texto: '¿Quién es Conalvías?' },
  {
    Icono: Rollo,
    titulo: 'Zona del sismo',
    texto: 'Los contratos de la Alcaldía de Buenaventura',
  },
  { Icono: Clepsidra, titulo: 'Un caso conocido', texto: 'Odinsa y la Ruta del Sol' },
]

/** La lechuza dice quién habla, sin repetir su nombre en cada turno. */
const ICONO_CANDIDATO = { empresa: Anfora, entidad: Templo, persona: Busto }

export function PantallaChat() {
  const { activa, guardar } = useHistorial()
  const [texto, setTexto] = useState('')
  const finRef = useRef<HTMLDivElement>(null)

  const mensajes = activa?.mensajes ?? []

  const enviar = useMutation({
    mutationFn: ({ mensaje, ctx }: { mensaje: string; ctx?: Record<string, unknown> }) =>
      api.chat(mensaje, ctx),
  })

  const leer = useMutation({ mutationFn: (archivo: File) => api.justificacion(archivo) })

  const ocupado = enviar.isPending || leer.isPending

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensajes.length, ocupado])

  function preguntar(mensaje: string, ctx = activa?.contexto) {
    if (!mensaje.trim()) return
    const previos = activa?.mensajes ?? []
    const conPregunta = [...previos, { rol: 'usuario' as const, texto: mensaje }]
    setTexto('')

    // El primer mensaje bautiza la consulta en el panel lateral.
    guardar({
      titulo: previos.length ? activa?.titulo : mensaje,
      mensajes: conPregunta,
      contexto: ctx,
    })

    enviar.mutate(
      { mensaje, ctx },
      {
        onSuccess: (respuesta) =>
          guardar({
            mensajes: [...conPregunta, { rol: 'lumen', respuesta }],
            contexto: respuesta.caso ? { caso_id: respuesta.caso.id } : ctx,
          }),
      },
    )
  }

  /**
   * Una entidad pública se analiza por `entidad_id` y un proveedor por `nit`:
   * son dos caminos distintos dentro del motor (uno mira los procesos de la
   * entidad, el otro los contratos del proveedor). Mandar el NIT de una
   * alcaldía en el campo del proveedor devolvía un caso vacío.
   */
  function elegirCandidato(candidato: Candidato) {
    if (!candidato.nit) return
    const llave =
      candidato.tipo === 'entidad' ? { entidad_id: candidato.nit } : { nit: candidato.nit }
    preguntar(candidato.nombre, { ...llave, nombre: candidato.nombre })
  }

  /** Ruta alterna del Flujo B (§4.6, paso 7): el PDF entra directo al lector. */
  function subirJustificacion(archivo: File) {
    const previos = activa?.mensajes ?? []
    const conArchivo = [...previos, { rol: 'usuario' as const, texto: `📄 ${archivo.name}` }]

    guardar({
      titulo: previos.length ? activa?.titulo : archivo.name,
      mensajes: conArchivo,
      contexto: activa?.contexto,
    })

    leer.mutate(archivo, {
      onSuccess: (lectura) =>
        guardar({
          mensajes: [...conArchivo, { rol: 'lector', archivo: archivo.name, lectura }],
        }),
      // El lector no cae al fixture: enseñar la lectura de otro documento como
      // si fuera la del que la persona acaba de subir sería mentir.
      onError: (error: Error) =>
        guardar({
          mensajes: [...conArchivo, { rol: 'lector', archivo: archivo.name, error: error.message }],
        }),
    })
  }

  if (mensajes.length === 0 && !ocupado) {
    return (
      <Bienvenida
        texto={texto}
        setTexto={setTexto}
        onPreguntar={preguntar}
        onArchivo={subirJustificacion}
        ocupado={ocupado}
      />
    )
  }

  return (
    <div className="mx-auto flex min-h-[calc(100dvh-9rem)] max-w-2xl flex-col">
      <div className="flex-1 space-y-6">
        {mensajes.map((mensaje, i) => {
          if (mensaje.rol === 'usuario') {
            return (
              <p
                key={i}
                className="ml-auto max-w-[85%] bg-[var(--color-superficie-alta)] px-4 py-2 text-sm"
              >
                {mensaje.texto}
              </p>
            )
          }
          if (mensaje.rol === 'lector') {
            return <RespuestaLector key={i} mensaje={mensaje} />
          }
          return <RespuestaLumen key={i} respuesta={mensaje.respuesta} onCandidato={elegirCandidato} />
        })}

        {ocupado && (
          <ConAvatar>
            <Pensando
              etiqueta={
                leer.isPending
                  ? 'Leyendo la justificación y buscando cada cita en el documento…'
                  : 'Resolviendo la entidad y corriendo las señales…'
              }
            />
            <EsqueletoSenal />
          </ConAvatar>
        )}
        <div ref={finRef} />
      </div>

      <div className="sticky bottom-0 mt-6 bg-[var(--color-fondo)] py-3">
        <CajaEntrada
          texto={texto}
          setTexto={setTexto}
          onPreguntar={preguntar}
          onArchivo={subirJustificacion}
          ocupado={ocupado}
        />
      </div>
    </div>
  )
}

/** La lechuza a la izquierda de cada turno del agente, como en cualquier chat. */
function ConAvatar({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex gap-3">
      <img src={marca} alt="" aria-hidden className="mt-0.5 h-6 w-6 shrink-0 object-contain" />
      <div className="min-w-0 flex-1 space-y-4">{children}</div>
    </div>
  )
}

/** El estado vacío: la caja con la lechuza posada y por dónde empezar. */
function Bienvenida({
  texto,
  setTexto,
  onPreguntar,
  onArchivo,
  ocupado,
}: {
  texto: string
  setTexto: (t: string) => void
  onPreguntar: (t: string) => void
  onArchivo: (a: File) => void
  ocupado: boolean
}) {
  return (
    <div className="mx-auto max-w-2xl pb-10 pt-16 sm:pt-24">
      <h1 className="text-center font-serif text-2xl font-normal sm:text-[1.75rem]">
        ¿Qué quieres vigilar?
      </h1>

      <div className="relative mt-14">
        <img
          src={buhoVuelo}
          alt=""
          aria-hidden
          className="pointer-events-none absolute right-10 z-20 w-[var(--buho)] select-none [--buho:88px] sm:right-16 sm:[--buho:112px]"
          style={{ bottom: `calc(100% - var(--buho) * ${BUHO_GARRAS.toFixed(4)})` }}
        />
        <CajaEntrada
          grande
          texto={texto}
          setTexto={setTexto}
          onPreguntar={onPreguntar}
          onArchivo={onArchivo}
          ocupado={ocupado}
        />
      </div>

      <p className="mt-9 text-[0.6rem] uppercase tracking-[0.2em] text-[var(--color-texto-tenue)]">
        Por dónde empezar
      </p>

      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {ARRANQUE.map((tarjeta) => (
          <button
            key={tarjeta.titulo}
            onClick={() => onPreguntar(tarjeta.texto)}
            className="flex gap-3 border border-[var(--color-borde)] bg-[var(--color-superficie)] p-3.5 text-left transition-colors hover:border-[var(--color-lumen)]"
          >
            <span className="grid h-9 w-9 shrink-0 place-items-center border border-[var(--color-borde)] bg-[var(--color-fondo)] p-[7px] text-[var(--color-bronce)]">
              <tarjeta.Icono />
            </span>
            <span className="min-w-0">
              <span className="block font-serif text-[0.95rem]">{tarjeta.titulo}</span>
              <span className="mt-0.5 block text-xs leading-relaxed text-[var(--color-texto-tenue)]">
                {tarjeta.texto}
              </span>
            </span>
          </button>
        ))}
      </div>

      <p className="mt-8 text-center text-[0.7rem] text-[var(--color-texto-tenue)]">
        Una señal no es prueba de irregularidad. Es un motivo para preguntar.
      </p>
    </div>
  )
}

/** La caja de entrada. Grande en el estado vacío, compacta durante la conversación. */
function CajaEntrada({
  texto,
  setTexto,
  onPreguntar,
  onArchivo,
  ocupado,
  grande = false,
}: {
  texto: string
  setTexto: (t: string) => void
  onPreguntar: (t: string) => void
  onArchivo: (a: File) => void
  ocupado: boolean
  grande?: boolean
}) {
  const archivoRef = useRef<HTMLInputElement>(null)

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onPreguntar(texto)
      }}
      className={`border border-[var(--color-borde)] bg-[var(--color-fondo)] focus-within:border-[var(--color-lumen)] ${
        grande
          ? 'relative shadow-[0_14px_34px_-26px_oklch(0.3_0.05_264/0.5)]'
          : 'flex items-center gap-2 p-1.5'
      }`}
    >
      {/* En grande el hueco de la derecha lo ocupan las alas: el texto no entra ahí. */}
      <input
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Escribe una empresa, una alcaldía o lo que viste"
        aria-label="Tu pregunta"
        className={`w-full bg-transparent outline-none placeholder:text-[var(--color-texto-tenue)] ${
          grande ? 'pb-3 pl-4 pr-24 pt-4 text-sm sm:pr-32' : 'flex-1 px-3 py-2 text-sm'
        }`}
      />

      {/* El PDF de la justificación de urgencia: se salta la resolución y va
          directo al lector (§4.6, Flujo B paso 7). */}
      <input
        ref={archivoRef}
        type="file"
        accept="application/pdf,.pdf"
        className="hidden"
        onChange={(e) => {
          const archivo = e.target.files?.[0]
          if (archivo) onArchivo(archivo)
          e.target.value = ''
        }}
      />

      {grande ? (
        <div className="flex items-center justify-between gap-3 px-3 pb-3">
          <span className="text-[0.6rem] uppercase tracking-[0.16em] text-[var(--color-texto-tenue)]">
            <span aria-hidden className="mr-1.5 text-[var(--color-bronce)]">
              ✦
            </span>
            Ocho señales · fuente oficial
          </span>
          <div className="flex items-center gap-2">
            <BotonAdjuntar ocupado={ocupado} onClick={() => archivoRef.current?.click()} />
            <BotonEnviar ocupado={ocupado} vacio={!texto.trim()} />
          </div>
        </div>
      ) : (
        <>
          <BotonAdjuntar ocupado={ocupado} onClick={() => archivoRef.current?.click()} />
          <BotonEnviar ocupado={ocupado} vacio={!texto.trim()} />
        </>
      )}
    </form>
  )
}

/** Subir el documento que explica por qué era urgente. */
function BotonAdjuntar({ ocupado, onClick }: { ocupado: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={ocupado}
      title="Subir el documento que explica por qué era urgente (PDF)"
      aria-label="Subir el documento que explica por qué era urgente"
      className="grid h-8 w-8 shrink-0 place-items-center border border-[var(--color-borde)] text-[var(--color-texto-tenue)] transition hover:border-[var(--color-lumen)] hover:text-[var(--color-texto)] disabled:opacity-25"
    >
      <svg
        aria-hidden
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="h-4 w-4"
      >
        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
      </svg>
    </button>
  )
}

function BotonEnviar({ ocupado, vacio }: { ocupado: boolean; vacio: boolean }) {
  return (
    <button
      type="submit"
      disabled={ocupado || vacio}
      aria-label="Preguntar"
      className="grid h-8 w-8 shrink-0 place-items-center bg-[var(--color-lumen)] text-sm text-[var(--color-lumen-texto)] transition hover:opacity-90 disabled:opacity-25"
    >
      <span aria-hidden>↑</span>
    </button>
  )
}

/** El veredicto del lector sobre el PDF que subió la persona. */
function RespuestaLector({
  mensaje,
}: {
  mensaje: { archivo: string; lectura?: LecturaTipo; error?: string }
}) {
  return (
    <ConAvatar>
      {mensaje.lectura ? (
        <>
          <p className="leading-relaxed">
            Leí <span className="italic">{mensaje.archivo}</span> y busqué en el texto cada cosa
            que la ley exige. Esto es lo que dice el documento:
          </p>
          <Lectura lectura={mensaje.lectura} />
        </>
      ) : (
        <p className="leading-relaxed">
          No pude leer <span className="italic">{mensaje.archivo}</span>. {mensaje.error} — prefiero
          decírtelo a enseñarte la lectura de otro documento.
        </p>
      )}
    </ConAvatar>
  )
}

function RespuestaLumen({
  respuesta,
  onCandidato,
}: {
  respuesta: ChatResponse
  onCandidato: (c: Candidato) => void
}) {
  return (
    <ConAvatar>
      <p className="leading-relaxed">{respuesta.narracion}</p>

      {/* Si hay más de un candidato, elige la persona. Nunca se asume. */}
      {respuesta.candidatos?.map((candidato) => {
        const Icono = ICONO_CANDIDATO[candidato.tipo] ?? Busto
        return (
          <button
            key={`${candidato.nombre}-${candidato.nit}`}
            onClick={() => onCandidato(candidato)}
            className="flex w-full gap-3.5 border border-[var(--color-borde)] bg-[var(--color-superficie)] p-3.5 text-left transition hover:border-[var(--color-lumen)]"
          >
            <span className="grid h-9 w-9 shrink-0 place-items-center border border-[var(--color-borde)] bg-[var(--color-fondo)] p-[7px] text-[var(--color-bronce)]">
              <Icono />
            </span>
            <span className="min-w-0">
              <span className="block font-serif text-[0.95rem]">{candidato.nombre}</span>
              <span className="mt-0.5 block text-xs text-[var(--color-texto-tenue)]">
                {[candidato.tipo, candidato.ciudad, candidato.nit && `NIT ${candidato.nit}`]
                  .filter(Boolean)
                  .join(' · ')}
              </span>
              {candidato.actividad && (
                <span className="mt-1 block text-xs text-[var(--color-texto-tenue)]">
                  {candidato.actividad}
                </span>
              )}
            </span>
          </button>
        )
      })}

      {respuesta.caso && <CasoEnChat caso={respuesta.caso} />}

      {/*
        Con un caso en la mano, los siguientes pasos son botones que llevan a
        algún lado (los pinta `CasoEnChat`). Sin caso, son indicaciones — y
        tienen que leerse como tales.

        Hasta el 16.ago eran botones siempre, y al pulsarlos se reenviaba su
        propio texto como pregunta: "Ver la red de actores detrás de este
        contrato" viajaba a `/chat`, que lo trataba como el nombre de una
        empresa y respondía "no encontré ningún registro". El brief pide
        ofrecer el siguiente paso (§4.5.2 #4), no ofrecer un callejón.
      */}
      {!respuesta.caso && respuesta.siguientes_pasos.length > 0 && (
        <ul className="space-y-1 text-sm text-[var(--color-texto-tenue)]">
          {respuesta.siguientes_pasos.map((paso) => (
            <li key={paso}>· {paso}</li>
          ))}
        </ul>
      )}
    </ConAvatar>
  )
}

function CasoEnChat({ caso }: { caso: Caso }) {
  const tieneRed = (caso.grafo?.nodos.length ?? 0) > 0

  return (
    <div className="border border-[var(--color-borde)] p-4">
      <FichaCaso caso={caso} compacta />
      <div className="mt-4 flex flex-wrap gap-2 border-t border-[var(--color-borde)] pt-4">
        <Link to={`/app/caso/${caso.id}`}>
          <Boton variante="secundario">
            {tieneRed ? 'Ver la ficha y la red de actores' : 'Abrir la ficha completa'}
          </Boton>
        </Link>
        <Link to={`/app/caso/${caso.id}/artefacto?tipo=paquete_evidencia`}>
          <Boton variante="secundario">Generar el paquete de evidencia</Boton>
        </Link>
        {caso.nivel_atencion !== 'bajo' && (
          <Link to={`/app/caso/${caso.id}/artefacto`}>
            <Boton>Redactar la carta para la alcaldía</Boton>
          </Link>
        )}
      </div>
    </div>
  )
}
