/**
 * Pantalla 1 — la alerta de WhatsApp del Modo Emergencia.
 *
 * El texto se arma aquí a partir del caso: `POST /alerta` devuelve si se envió,
 * no la copia del mensaje. Máximo cinco líneas y en lenguaje ciudadano — «el
 * 61 % del valor se concentró en 2 empresas», nunca «índice Herfindahl 0,61».
 */
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router'
import { api } from '../lib/api'
import { pesosCortos } from '../lib/formato'
import { Disclaimer, Nivel } from '../componentes/Basicos'
import { Barra, EsqueletoSenal } from '../componentes/Esqueleto'
import type { Caso } from '../lib/tipos'

/** Cinco líneas: qué pasó, cuánto, qué se vio, qué hacer. */
function redactarAlerta(caso: Caso): string[] {
  const lineas = [
    `⚠️ ${caso.municipio ?? caso.entidad}: contrato de ${pesosCortos(caso.valor)} adjudicado sin licitación.`,
  ]
  if (caso.objeto) lineas.push(`Para: ${caso.objeto.toLowerCase()}.`)
  for (const senal of caso.senales.slice(0, 2)) lineas.push(senal.regla_legible)
  lineas.push('Te dejamos la evidencia y un derecho de petición listo para enviar 👇')
  return lineas.slice(0, 5)
}

export function PantallaAlerta() {
  const { id } = useParams()
  const { data: casos, isPending } = useQuery({
    queryKey: ['alertas', id],
    queryFn: async () => (id ? [await api.caso(id)] : await api.monitor()),
  })

  if (isPending) {
    return (
      <div className="space-y-4" aria-busy="true">
        <Barra ancho="w-48" alto="h-6" />
        <EsqueletoSenal />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-wide text-[var(--color-texto-tenue)]">
          Modo Emergencia
        </p>
        <h1 className="mt-1 text-2xl font-semibold leading-tight">
          {id ? 'Así llegó la alerta' : 'Lo que encontró el monitor'}
        </h1>
        <p className="mt-2 text-sm text-[var(--color-texto-tenue)]">
          El monitor revisa lo que entra por el régimen de emergencia y avisa al veedor, al
          periodista o al líder comunal del municipio.
        </p>
      </header>

      {casos?.map((caso) => (
        <BurbujaWhatsApp key={caso.id} caso={caso} />
      ))}

      <Disclaimer />
    </div>
  )
}

function BurbujaWhatsApp({ caso }: { caso: Caso }) {
  const lineas = redactarAlerta(caso)

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Nivel nivel={caso.nivel_atencion} compacto />
        <span className="text-xs text-[var(--color-texto-tenue)]">
          para el veedor de {caso.municipio ?? caso.entidad}
        </span>
      </div>

      {/* Pinta el mensaje tal como se recibe: es lo que se graba en el video. */}
      <div className="rounded-2xl rounded-tl-sm border border-[var(--color-borde)] bg-[oklch(0.28_0.03_150)] p-4 shadow-lg">
        <p className="mb-2 text-xs font-semibold text-[var(--color-lumen)]">Lumen</p>
        <div className="space-y-2 text-sm leading-relaxed">
          {lineas.map((linea, i) => (
            <p key={i}>{linea}</p>
          ))}
        </div>
        <Link
          to={`/app/caso/${caso.id}`}
          className="mt-3 block rounded-lg bg-[var(--color-superficie)] px-3 py-2 text-center text-sm font-medium text-[var(--color-lumen)] hover:opacity-90"
        >
          Ver el caso completo
        </Link>
      </div>
    </div>
  )
}
