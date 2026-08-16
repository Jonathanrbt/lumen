/**
 * Pantalla 2 — la ficha del caso, en un solo scroll.
 *
 * Arriba municipio, valor, entidad y nivel de atención. En el centro las señales
 * como tarjetas. Abajo el subgrafo de actores.
 */
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router'
import { api } from '../lib/api'
import { fecha, pesos, pesosCortos } from '../lib/formato'
import { Boton, Disclaimer, Nivel } from '../componentes/Basicos'
import { EsqueletoCaso } from '../componentes/Esqueleto'
import { Grafo } from '../componentes/Grafo'
import { Lectura } from '../componentes/Lectura'
import { TarjetaSenal } from '../componentes/TarjetaSenal'
import type { Caso as TipoCaso } from '../lib/tipos'

export function PantallaCaso() {
  const { id = '' } = useParams()
  const { data: caso, isPending } = useQuery({
    queryKey: ['caso', id],
    queryFn: () => api.caso(id),
  })

  if (isPending) return <EsqueletoCaso />
  if (!caso) return <p className="text-[var(--color-texto-tenue)]">No se encontró el caso.</p>

  return <FichaCaso caso={caso} />
}

/** Se exporta suelta porque el chat pinta la misma ficha dentro de la conversación. */
export function FichaCaso({ caso, compacta = false }: { caso: TipoCaso; compacta?: boolean }) {
  return (
    <article className="space-y-6">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Nivel nivel={caso.nivel_atencion} />
          <span className="text-xs uppercase tracking-wide text-[var(--color-texto-tenue)]">
            Modo {caso.modo}
          </span>
        </div>

        <h1 className="text-2xl font-semibold leading-tight">
          {caso.municipio ?? caso.entidad}
          {caso.valor != null && (
            <span className="text-[var(--color-lumen)]"> · {pesosCortos(caso.valor)}</span>
          )}
        </h1>

        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <div>
            <dt className="text-xs text-[var(--color-texto-tenue)]">Entidad contratante</dt>
            <dd>{caso.entidad}</dd>
          </div>
          {caso.proveedor && (
            <div>
              <dt className="text-xs text-[var(--color-texto-tenue)]">Proveedor</dt>
              <dd>{caso.proveedor}</dd>
            </div>
          )}
          {caso.valor != null && (
            <div>
              <dt className="text-xs text-[var(--color-texto-tenue)]">Valor</dt>
              <dd>{pesos(caso.valor)}</dd>
            </div>
          )}
          {caso.fecha && (
            <div>
              <dt className="text-xs text-[var(--color-texto-tenue)]">Adjudicado</dt>
              <dd>{fecha(caso.fecha)}</dd>
            </div>
          )}
          {caso.objeto && (
            <div className="col-span-2">
              <dt className="text-xs text-[var(--color-texto-tenue)]">Objeto</dt>
              <dd>{caso.objeto}</dd>
            </div>
          )}
        </dl>

        <Disclaimer texto={caso.disclaimer} />
      </header>

      {caso.narracion && (
        <p className="border-l-2 border-[var(--color-lumen)] pl-4 leading-relaxed">
          {caso.narracion}
        </p>
      )}

      <section className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--color-texto-tenue)]">
          {caso.senales.length === 1
            ? '1 señal que merece revisión'
            : `${caso.senales.length} señales que merecen revisión`}
        </h2>
        {caso.senales.map((senal) => (
          <TarjetaSenal key={senal.codigo} senal={senal} />
        ))}
      </section>

      {caso.lectura && <Lectura lectura={caso.lectura} />}

      {caso.grafo && caso.grafo.nodos.length > 0 && <Grafo grafo={caso.grafo} />}

      {!compacta && (
        <footer className="flex flex-wrap gap-2 border-t border-[var(--color-borde)] pt-4">
          <Link to={`/app/caso/${caso.id}/artefacto`}>
            <Boton>Redactar derecho de petición</Boton>
          </Link>
          <Link to={`/app/caso/${caso.id}/alerta`}>
            <Boton variante="secundario">Ver la alerta que se envió</Boton>
          </Link>
        </footer>
      )}
    </article>
  )
}
