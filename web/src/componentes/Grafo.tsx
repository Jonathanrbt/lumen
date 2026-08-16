/**
 * Subgrafo de actores, entre 5 y 12 nodos.
 *
 * Disposición radial calculada, sin simulación de fuerzas: con esta cantidad de
 * nodos una física da saltos entre cuadros y el encuadre cambia en cada carga.
 * Radial es determinista, se lee en un teléfono y se graba igual siempre.
 *
 * Debajo van los vínculos como lista, que además es donde caben las fuentes de
 * cada arista. Si el reloj obliga a quitar el SVG, la lista ya está en pie.
 */
import { fechaHora } from '../lib/formato'
import type { Actor, Grafo as TipoGrafo } from '../lib/tipos'

const COLOR_TIPO = {
  entidad: 'var(--color-lumen)',
  empresa: 'oklch(0.75 0.13 200)',
  persona: 'oklch(0.78 0.12 320)',
}

const ANCHO = 400
const ALTO = 300

function posiciones(nodos: Actor[], centroId: string) {
  const mapa = new Map<string, { x: number; y: number }>()
  const alrededor = nodos.filter((n) => n.id !== centroId)
  mapa.set(centroId, { x: ANCHO / 2, y: ALTO / 2 })

  const radio = Math.min(ANCHO, ALTO) / 2 - 52
  alrededor.forEach((nodo, i) => {
    // Arranca arriba y reparte parejo; el -90° evita que el primero quede a la derecha.
    const angulo = (i / alrededor.length) * 2 * Math.PI - Math.PI / 2
    mapa.set(nodo.id, {
      x: ANCHO / 2 + radio * Math.cos(angulo),
      y: ALTO / 2 + radio * Math.sin(angulo),
    })
  })
  return mapa
}

export function Grafo({ grafo }: { grafo: TipoGrafo }) {
  if (grafo.nodos.length === 0) return null

  // El centro es el nodo con más vínculos: es el que explica el dibujo.
  const grados = new Map<string, number>()
  for (const a of grafo.aristas) {
    grados.set(a.origen, (grados.get(a.origen) ?? 0) + 1)
    grados.set(a.destino, (grados.get(a.destino) ?? 0) + 1)
  }
  const centro = grafo.nodos.reduce((mejor, n) =>
    (grados.get(n.id) ?? 0) > (grados.get(mejor.id) ?? 0) ? n : mejor,
  )
  const pos = posiciones(grafo.nodos, centro.id)
  const porId = new Map(grafo.nodos.map((n) => [n.id, n]))

  return (
    <section>
      <h3 className="text-sm font-semibold uppercase tracking-wide text-[var(--color-texto-tenue)]">
        Quién está detrás
      </h3>

      <svg
        viewBox={`0 0 ${ANCHO} ${ALTO}`}
        className="mt-2 w-full border border-[var(--color-borde)] bg-[var(--color-superficie)]"
        role="img"
        aria-label={`Red de ${grafo.nodos.length} actores y ${grafo.aristas.length} vínculos`}
      >
        {grafo.aristas.map((a, i) => {
          const o = pos.get(a.origen)
          const d = pos.get(a.destino)
          if (!o || !d) return null
          return (
            <line
              key={i}
              x1={o.x}
              y1={o.y}
              x2={d.x}
              y2={d.y}
              stroke="var(--color-borde)"
              strokeWidth={1.5}
            />
          )
        })}

        {grafo.nodos.map((nodo) => {
          const p = pos.get(nodo.id)
          if (!p) return null
          const esCentro = nodo.id === centro.id
          const color = COLOR_TIPO[nodo.tipo]
          return (
            <g key={nodo.id}>
              <circle
                cx={p.x}
                cy={p.y}
                r={esCentro ? 13 : 9}
                fill={color}
                fillOpacity={0.22}
                stroke={color}
                strokeWidth={1.5}
              />
              <text
                x={p.x}
                y={p.y + (p.y > ALTO / 2 ? 26 : -18)}
                textAnchor="middle"
                className="fill-[var(--color-texto)] text-[10px]"
              >
                {/* Nombres largos parten la línea; el SVG no envuelve solo. */}
                {nodo.nombre.length > 26 ? `${nodo.nombre.slice(0, 24)}…` : nodo.nombre}
              </text>
              {nodo.rol && (
                <text
                  x={p.x}
                  y={p.y + (p.y > ALTO / 2 ? 37 : -8)}
                  textAnchor="middle"
                  className="fill-[var(--color-texto-tenue)] text-[9px]"
                >
                  {nodo.rol}
                </text>
              )}
            </g>
          )
        })}
      </svg>

      <ul className="mt-3 space-y-2">
        {grafo.aristas.map((a, i) => (
          <li
            key={i}
            className="border border-[var(--color-borde)] bg-[var(--color-superficie)] px-3 py-2 text-sm"
          >
            <span className="font-medium">{porId.get(a.origen)?.nombre ?? a.origen}</span>{' '}
            <span className="text-[var(--color-texto-tenue)]">
              {a.tipo.replace(/_/g, ' ')}
            </span>{' '}
            <span className="font-medium">{porId.get(a.destino)?.nombre ?? a.destino}</span>
            <a
              href={a.fuente.url_oficial}
              target="_blank"
              rel="noreferrer noopener"
              className="mt-1 block text-xs text-[var(--color-texto-tenue)] underline decoration-dotted underline-offset-2 hover:text-[var(--color-lumen)]"
            >
              Fuente oficial · consultado el {fechaHora(a.fuente.consultado_en)}
            </a>
          </li>
        ))}
      </ul>
    </section>
  )
}
