/**
 * Pantalla 4 — el artefacto.
 *
 * La capa de acción: sin esto una alerta es solo una alerta. Se genera, se copia
 * y se descarga listo para radicar.
 */
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router'
import Markdown from 'react-markdown'
import { api } from '../lib/api'
import { Boton, Disclaimer } from '../componentes/Basicos'
import { EsqueletoArtefacto } from '../componentes/Esqueleto'
import { Orbe } from '../componentes/Orbe'

/** Clases del markdown del documento: es una carta legal, no un blog. */
const PROSA = [
  'text-sm leading-relaxed',
  '[&_p]:mb-3',
  '[&_strong]:font-semibold [&_strong]:text-[var(--color-texto)]',
  '[&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-1',
  '[&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-5',
  '[&_em]:italic',
].join(' ')

export function PantallaArtefacto() {
  const { id = '' } = useParams()
  const [copiado, setCopiado] = useState(false)

  const { data: artefacto, isPending } = useQuery({
    queryKey: ['artefacto', id],
    queryFn: () => api.accion(id, 'derecho_peticion'),
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
    enlace.download = `derecho-peticion-${id}.md`
    enlace.click()
    URL.revokeObjectURL(url)
  }

  if (isPending) {
    return (
      <div className="space-y-6">
        <Orbe etiqueta="Redactando el derecho de petición con los hechos del caso…" />
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

      <div className="rounded-xl border border-[var(--color-borde)] bg-[var(--color-superficie)] p-4">
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
