/**
 * Pantalla 4 — el artefacto.
 *
 * La capa de acción: sin esto una alerta es solo una alerta. Se genera, se copia
 * y se descarga listo para radicar.
 */
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router'
import Markdown from 'react-markdown'
import { api } from '../lib/api'
import { Boton, Disclaimer } from '../componentes/Basicos'
import { EsqueletoArtefacto } from '../componentes/Esqueleto'
import { Pensando } from '../componentes/Pensando'
import type { TipoArtefacto } from '../lib/tipos'

/** Clases del markdown del documento: es una carta legal, no un blog. */
const PROSA = [
  'text-sm leading-relaxed',
  '[&_p]:mb-3',
  '[&_strong]:font-semibold [&_strong]:text-[var(--color-texto)]',
  '[&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-1',
  '[&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-5',
  '[&_em]:italic',
].join(' ')

/**
 * Los cuatro artefactos de la capa de acción (§7). La carta es el que sale en
 * el video, así que es el que se sirve sin pedir nada; los otros llegan por
 * `?tipo=`, que es lo que usan los botones del chat y de la ficha.
 */
const ARTEFACTOS: Record<string, { tipo: TipoArtefacto; etiqueta: string; nombre: string }> = {
  derecho_peticion: {
    tipo: 'derecho_peticion',
    etiqueta: 'Redactando la carta para la alcaldía con los hechos del caso…',
    nombre: 'carta-para-la-alcaldia',
  },
  paquete_evidencia: {
    tipo: 'paquete_evidencia',
    etiqueta: 'Armando el paquete de evidencia con su fuente oficial…',
    nombre: 'paquete-de-evidencia',
  },
  informe_veeduria: {
    tipo: 'informe_veeduria',
    etiqueta: 'Redactando el informe de veeduría…',
    nombre: 'informe-de-veeduria',
  },
  guia_denuncia: {
    tipo: 'guia_denuncia',
    etiqueta: 'Buscando el canal formal que corresponde…',
    nombre: 'guia-de-denuncia',
  },
}

export function PantallaArtefacto() {
  const { id = '' } = useParams()
  const [parametros] = useSearchParams()
  const [copiado, setCopiado] = useState(false)

  const cual = ARTEFACTOS[parametros.get('tipo') ?? ''] ?? ARTEFACTOS.derecho_peticion

  const { data: artefacto, isPending } = useQuery({
    queryKey: ['artefacto', id, cual.tipo],
    queryFn: () => api.accion(id, cual.tipo),
  })

  async function copiar() {
    if (!artefacto) return
    await navigator.clipboard.writeText(artefacto.cuerpo_markdown)
    setCopiado(true)
    setTimeout(() => setCopiado(false), 2000)
  }

  function descargar() {
    if (!artefacto) return
    const blob = new Blob([artefacto.cuerpo_markdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const enlace = document.createElement('a')
    enlace.href = url
    enlace.download = `${cual.nombre}-${id}.md`
    enlace.click()
    URL.revokeObjectURL(url)
  }

  if (isPending) {
    return (
      <div className="space-y-6">
        <Pensando estado="composing" etiqueta={cual.etiqueta} />
        <EsqueletoArtefacto />
      </div>
    )
  }

  if (!artefacto) return <p>No se pudo generar el documento.</p>

  return (
    <article className="space-y-4">
      <header className="space-y-2">
        <Link
          to={`/app/caso/${id}`}
          className="text-xs text-[var(--color-texto-tenue)] hover:text-[var(--color-lumen)]"
        >
          ← Volver al caso
        </Link>
        <h1 className="text-xl font-semibold leading-tight">{artefacto.titulo}</h1>
        {artefacto.destinatario && (
          <p className="text-sm text-[var(--color-texto-tenue)]">
            Dirigido a {artefacto.destinatario}
          </p>
        )}
      </header>

      <div className="flex flex-wrap gap-2">
        <Boton onClick={copiar}>{copiado ? 'Copiado ✓' : 'Copiar'}</Boton>
        <Boton variante="secundario" onClick={descargar}>
          Descargar
        </Boton>
      </div>

      <div className="border border-[var(--color-borde)] bg-[var(--color-superficie)] p-4">
        <div className={PROSA}>
          <Markdown>{artefacto.cuerpo_markdown}</Markdown>
        </div>
      </div>

      {artefacto.normas_citadas.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--color-texto-tenue)]">
            Normas citadas
          </h2>
          <ul className="mt-2 space-y-1 text-sm text-[var(--color-texto-tenue)]">
            {artefacto.normas_citadas.map((norma) => (
              <li key={norma}>· {norma}</li>
            ))}
          </ul>
        </section>
      )}

      <Disclaimer />
    </article>
  )
}
