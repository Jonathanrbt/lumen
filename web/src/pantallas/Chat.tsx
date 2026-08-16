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
import { Pensando } from '../componentes/Pensando'
import { FichaCaso } from './Caso'
import buhoVuelo from '../assets/buho-vuelo.png'
import marca from '../assets/lumen-marca.png'
import type { Candidato, Caso, ChatResponse } from '../lib/tipos'

/**
 * La lechuza se posa en el borde de la caja: en el PNG ya recortado sus garras
 * caen al 58 % del alto y las alas siguen hasta abajo. Se ancla por las garras
 * —de ahí este factor— y las alas quedan colgando sobre la caja. El ancho lo
 * pone `--buho`, que cambia por breakpoint.
 */
const BUHO_GARRAS = (730 / 720) * (1 - 0.583)

const ARRANQUE = [
  { Icono: Templo, titulo: 'Mi municipio', texto: '¿La alcaldía de mi pueblo tiene algo raro?' },
  { Icono: Anfora, titulo: 'Una empresa', texto: '¿Quién está detrás de este contratista?' },
  { Icono: Rollo, titulo: 'Un contrato', texto: 'El contrato de los escombros en Quimbaya' },
  { Icono: Clepsidra, titulo: 'Una emergencia pasada', texto: 'La reconstrucción de Mocoa, 2017' },
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

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensajes.length, enviar.isPending])

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

  function elegirCandidato(candidato: Candidato) {
    preguntar(candidato.nombre, { nit: candidato.nit, nombre: candidato.nombre })
  }

  if (mensajes.length === 0 && !enviar.isPending) {
    return (
      <Bienvenida
        texto={texto}
        setTexto={setTexto}
        onPreguntar={preguntar}
        ocupado={enviar.isPending}
      />
    )
  }

  return (
    <div className="mx-auto flex min-h-[calc(100dvh-9rem)] max-w-2xl flex-col">
      <div className="flex-1 space-y-6">
        {mensajes.map((mensaje, i) =>
          mensaje.rol === 'usuario' ? (
            <p
              key={i}
              className="ml-auto max-w-[85%] bg-[var(--color-superficie-alta)] px-4 py-2 text-sm"
            >
              {mensaje.texto}
            </p>
          ) : (
            <RespuestaLumen
              key={i}
              respuesta={mensaje.respuesta}
              onCandidato={elegirCandidato}
              onPaso={(paso) => preguntar(paso)}
            />
          ),
        )}

        {enviar.isPending && (
          <ConAvatar>
            <Pensando etiqueta="Resolviendo la entidad y corriendo las señales…" />
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
          ocupado={enviar.isPending}
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
  ocupado,
}: {
  texto: string
  setTexto: (t: string) => void
  onPreguntar: (t: string) => void
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
  ocupado,
  grande = false,
}: {
  texto: string
  setTexto: (t: string) => void
  onPreguntar: (t: string) => void
  ocupado: boolean
  grande?: boolean
}) {
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

      {grande ? (
        <div className="flex items-center justify-between gap-3 px-3 pb-3">
          <span className="text-[0.6rem] uppercase tracking-[0.16em] text-[var(--color-texto-tenue)]">
            <span aria-hidden className="mr-1.5 text-[var(--color-bronce)]">
              ✦
            </span>
            Ocho señales · fuente oficial
          </span>
          <BotonEnviar ocupado={ocupado} vacio={!texto.trim()} />
        </div>
      ) : (
        <BotonEnviar ocupado={ocupado} vacio={!texto.trim()} />
      )}
    </form>
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

function RespuestaLumen({
  respuesta,
  onCandidato,
  onPaso,
}: {
  respuesta: ChatResponse
  onCandidato: (c: Candidato) => void
  onPaso: (paso: string) => void
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

      {respuesta.siguientes_pasos.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {respuesta.siguientes_pasos.map((paso) => (
            <button
              key={paso}
              onClick={() => onPaso(paso)}
              className="border border-[var(--color-borde)] px-3 py-1.5 text-xs text-[var(--color-texto-tenue)] transition hover:border-[var(--color-lumen)] hover:text-[var(--color-texto)]"
            >
              {paso}
            </button>
          ))}
        </div>
      )}
    </ConAvatar>
  )
}

function CasoEnChat({ caso }: { caso: Caso }) {
  return (
    <div className="border border-[var(--color-borde)] p-4">
      <FichaCaso caso={caso} compacta />
      <div className="mt-4 flex flex-wrap gap-2 border-t border-[var(--color-borde)] pt-4">
        <Link to={`/app/caso/${caso.id}`}>
          <Boton variante="secundario">Abrir la ficha completa</Boton>
        </Link>
        <Link to={`/app/caso/${caso.id}/artefacto`}>
          <Boton>Redactar derecho de petición</Boton>
        </Link>
      </div>
    </div>
  )
}
