/**
 * Pantalla 3 — el chat del Modo Vigilancia.
 *
 * No es una pantalla nueva: es un envoltorio distinto sobre la ficha del caso y
 * las mismas tarjetas de señal. Entrada libre, candidatos como tarjetas que
 * elige la persona, y respuesta narrada.
 */
import { useMutation } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router'
import { api } from '../lib/api'
import { Boton } from '../componentes/Basicos'
import { EsqueletoSenal } from '../componentes/Esqueleto'
import { Orbe } from '../componentes/Orbe'
import { FichaCaso } from './Caso'
import type { Candidato, Caso, ChatResponse } from '../lib/tipos'

type Mensaje =
  | { rol: 'usuario'; texto: string }
  | { rol: 'lumen'; respuesta: ChatResponse }

const EJEMPLOS = [
  '¿La alcaldía de mi pueblo tiene algo raro?',
  'Constructora de ejemplo',
  'El contrato de los escombros en Quimbaya',
]

export function PantallaChat() {
  const [mensajes, setMensajes] = useState<Mensaje[]>([])
  const [texto, setTexto] = useState('')
  // Candidato ya elegido, caso en curso: lo que el backend necesita para no volver a preguntar.
  const [contexto, setContexto] = useState<Record<string, unknown> | undefined>()
  const finRef = useRef<HTMLDivElement>(null)

  const enviar = useMutation({
    mutationFn: ({ mensaje, ctx }: { mensaje: string; ctx?: Record<string, unknown> }) =>
      api.chat(mensaje, ctx),
    onSuccess: (respuesta) => {
      setMensajes((m) => [...m, { rol: 'lumen', respuesta }])
      if (respuesta.caso) setContexto({ caso_id: respuesta.caso.id })
    },
  })

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensajes, enviar.isPending])

  function preguntar(mensaje: string, ctx = contexto) {
    if (!mensaje.trim()) return
    setMensajes((m) => [...m, { rol: 'usuario', texto: mensaje }])
    setTexto('')
    enviar.mutate({ mensaje, ctx })
  }

  function elegirCandidato(candidato: Candidato) {
    const ctx = { nit: candidato.nit, nombre: candidato.nombre }
    setContexto(ctx)
    preguntar(candidato.nombre, ctx)
  }

  return (
    <div className="flex min-h-[calc(100dvh-8rem)] flex-col">
      <div className="flex-1 space-y-6">
        {mensajes.length === 0 && !enviar.isPending && <Bienvenida onEjemplo={preguntar} />}

        {mensajes.map((mensaje, i) =>
          mensaje.rol === 'usuario' ? (
            <p
              key={i}
              className="ml-auto max-w-[85%] rounded-2xl rounded-br-sm bg-[var(--color-superficie-alta)] px-4 py-2 text-sm"
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

        {enviar.isPending && <Pensando />}
        <div ref={finRef} />
      </div>

      <form
        className="sticky bottom-0 mt-6 flex gap-2 bg-[var(--color-fondo)] py-3"
        onSubmit={(e) => {
          e.preventDefault()
          preguntar(texto)
        }}
      >
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escribe el nombre de una empresa, una alcaldía o lo que viste"
          aria-label="Tu pregunta"
          className="flex-1 rounded-lg border border-[var(--color-borde)] bg-[var(--color-superficie)] px-4 py-3 text-sm outline-none placeholder:text-[var(--color-texto-tenue)] focus:border-[var(--color-lumen)]"
        />
        <Boton type="submit" disabled={enviar.isPending || !texto.trim()}>
          Preguntar
        </Boton>
      </form>
    </div>
  )
}

function Bienvenida({ onEjemplo }: { onEjemplo: (texto: string) => void }) {
  return (
    <div className="pt-6">
      <Orbe tamano="lg" />
      <h1 className="mt-6 text-2xl font-semibold leading-tight">
        ¿Qué está contratando tu municipio?
      </h1>
      <p className="mt-2 text-[var(--color-texto-tenue)]">
        Escríbelo como lo dirías en voz alta. No hace falta un NIT ni saber qué es el SECOP.
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        {EJEMPLOS.map((ejemplo) => (
          <button
            key={ejemplo}
            onClick={() => onEjemplo(ejemplo)}
            className="rounded-full border border-[var(--color-borde)] px-3 py-1.5 text-sm text-[var(--color-texto-tenue)] transition hover:border-[var(--color-lumen)] hover:text-[var(--color-texto)]"
          >
            {ejemplo}
          </button>
        ))}
      </div>
    </div>
  )
}

/** El orbe mientras el agente resuelve, más el esqueleto de lo que va a llegar. */
function Pensando() {
  return (
    <div className="space-y-4">
      <Orbe etiqueta="Resolviendo la entidad y corriendo las señales…" />
      <EsqueletoSenal />
    </div>
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
    <div className="space-y-4">
      <p className="leading-relaxed">{respuesta.narracion}</p>

      {/* Si hay más de un candidato, elige la persona. Nunca se asume. */}
      {respuesta.candidatos?.map((candidato) => (
        <button
          key={`${candidato.nombre}-${candidato.nit}`}
          onClick={() => onCandidato(candidato)}
          className="block w-full rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-3 text-left transition hover:border-[var(--color-lumen)]"
        >
          <p className="font-medium">{candidato.nombre}</p>
          <p className="mt-0.5 text-xs text-[var(--color-texto-tenue)]">
            {[candidato.tipo, candidato.ciudad, candidato.nit && `NIT ${candidato.nit}`]
              .filter(Boolean)
              .join(' · ')}
          </p>
          {candidato.actividad && (
            <p className="mt-1 text-xs text-[var(--color-texto-tenue)]">{candidato.actividad}</p>
          )}
        </button>
      ))}

      {respuesta.caso && <CasoEnChat caso={respuesta.caso} />}

      {respuesta.siguientes_pasos.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {respuesta.siguientes_pasos.map((paso) => (
            <button
              key={paso}
              onClick={() => onPaso(paso)}
              className="rounded-full border border-[var(--color-borde)] px-3 py-1.5 text-xs text-[var(--color-texto-tenue)] transition hover:border-[var(--color-lumen)] hover:text-[var(--color-texto)]"
            >
              {paso}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function CasoEnChat({ caso }: { caso: Caso }) {
  return (
    <div className="rounded-xl border border-[var(--color-borde)] p-4">
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
