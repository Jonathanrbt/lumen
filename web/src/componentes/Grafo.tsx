/**
 * Subgrafo de actores, entre 5 y 12 nodos.
 *
 * La disposición inicial es radial y calculada, no una simulación de fuerzas:
 * así el encuadre sale idéntico en cada carga y el video se graba siempre igual.
 * De ahí en adelante los nodos se arrastran, el lienzo se mueve y hace zoom.
 *
 * Debajo van los vínculos como lista, que además es donde caben las fuentes de
 * cada arista. Si el reloj obliga a quitar el lienzo, la lista ya está en pie.
 */
import { useCallback, useMemo } from 'react'
import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  Position,
  ReactFlow,
  applyNodeChanges,
  useNodesState,
  type Edge,
  type Node,
  type NodeProps,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Anfora, Busto, Templo } from './Iconos'
import { fechaHora } from '../lib/formato'
import type { Actor, Grafo as TipoGrafo } from '../lib/tipos'

const PINTA = {
  entidad: { Icono: Templo, color: 'var(--color-lumen)' },
  empresa: { Icono: Anfora, color: 'var(--color-bronce)' },
  persona: { Icono: Busto, color: 'var(--color-texto)' },
}

const LIENZO = { ancho: 620, alto: 340 }
// React Flow encuadra al montar, antes de medir: sin esto el grafo sale descentrado.
const NODO = { width: 196, height: 58 }

/** El rótulo de la arista va corto: la frase entera está en la lista de abajo. */
const VINCULO: Record<string, string> = {
  contrato_a: 'contrata',
  representante_legal_de: 'representa',
}

type DatosNodo = { actor: Actor; centro: boolean }
type NodoActor = Node<DatosNodo, 'actor'>

/** El nodo: ficha compacta con su icono, el nombre y el rol en versalitas. */
function NodoActor({ data }: NodeProps<NodoActor>) {
  const { Icono, color } = PINTA[data.actor.tipo]

  return (
    <div
      className="flex w-[196px] items-center gap-2.5 border bg-[var(--color-fondo)] px-2.5 py-2 transition-shadow hover:shadow-md"
      style={{ borderColor: data.centro ? color : 'var(--color-borde)' }}
    >
      <Handle type="target" position={Position.Top} className="!h-1 !w-1 !border-0 !bg-transparent" />
      <span
        className="grid h-7 w-7 shrink-0 place-items-center border p-1"
        style={{ borderColor: 'var(--color-borde)', color }}
      >
        <Icono />
      </span>
      <span className="min-w-0">
        <span className="line-clamp-2 font-serif text-[0.8rem] leading-[1.2]">
          {data.actor.nombre}
        </span>
        {data.actor.rol && (
          <span className="mt-0.5 block truncate text-[0.55rem] uppercase tracking-[0.12em] text-[var(--color-texto-tenue)]">
            {data.actor.rol}
          </span>
        )}
      </span>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-1 !w-1 !border-0 !bg-transparent"
      />
    </div>
  )
}

const TIPOS_NODO = { actor: NodoActor }

/** Radial alrededor del actor con más vínculos, que es el que explica el dibujo. */
function repartir(grafo: TipoGrafo): { nodos: NodoActor[]; centroId: string } {
  const grados = new Map<string, number>()
  for (const a of grafo.aristas) {
    grados.set(a.origen, (grados.get(a.origen) ?? 0) + 1)
    grados.set(a.destino, (grados.get(a.destino) ?? 0) + 1)
  }
  const centro = grafo.nodos.reduce((mejor, n) =>
    (grados.get(n.id) ?? 0) > (grados.get(mejor.id) ?? 0) ? n : mejor,
  )

  const alrededor = grafo.nodos.filter((n) => n.id !== centro.id)
  const radio = Math.min(LIENZO.ancho, LIENZO.alto) / 2 - 24

  const nodos = grafo.nodos.map<NodoActor>((actor) => {
    if (actor.id === centro.id) {
      return {
        id: actor.id,
        type: 'actor',
        position: { x: LIENZO.ancho / 2 - 98, y: LIENZO.alto / 2 - 29 },
        ...NODO,
        data: { actor, centro: true },
      }
    }
    // El -90° evita que el primero quede a la derecha.
    const i = alrededor.indexOf(actor)
    const angulo = (i / alrededor.length) * 2 * Math.PI - Math.PI / 2
    return {
      id: actor.id,
      type: 'actor',
      position: {
        x: LIENZO.ancho / 2 - 98 + radio * 2 * Math.cos(angulo),
        y: LIENZO.alto / 2 - 29 + radio * 1.35 * Math.sin(angulo),
      },
      ...NODO,
      data: { actor, centro: false },
    }
  })

  return { nodos, centroId: centro.id }
}

export function Grafo({ grafo }: { grafo: TipoGrafo }) {
  const inicial = useMemo(() => repartir(grafo), [grafo])
  const [nodos, , alCambiarNodos] = useNodesState<NodoActor>(inicial.nodos)

  const aristas = useMemo<Edge[]>(
    () =>
      grafo.aristas.map((a, i) => ({
        id: `a${i}`,
        source: a.origen,
        target: a.destino,
        label: VINCULO[a.tipo] ?? a.tipo.replace(/_/g, ' '),
        animated: true,
        style: { stroke: 'var(--color-borde)', strokeWidth: 1.5 },
        labelStyle: {
          fill: 'var(--color-texto-tenue)',
          fontSize: 9,
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
        },
        labelBgStyle: { fill: 'var(--color-fondo)' },
        labelBgPadding: [4, 2] as [number, number],
      })),
    [grafo.aristas],
  )

  const porId = useMemo(() => new Map(grafo.nodos.map((n) => [n.id, n])), [grafo.nodos])

  // Solo arrastre: sin esto React Flow admitiría borrar y conectar a mano.
  const soloMover = useCallback(
    (cambios: Parameters<typeof applyNodeChanges>[0]) =>
      alCambiarNodos(cambios.filter((c) => c.type === 'position' || c.type === 'dimensions')),
    [alCambiarNodos],
  )

  if (grafo.nodos.length === 0) return null

  return (
    <section>
      <h3 className="text-[0.62rem] uppercase tracking-[0.18em] text-[var(--color-texto-tenue)]">
        Quién está detrás
      </h3>

      <div
        className="mt-2 h-[320px] border border-[var(--color-borde)] bg-[var(--color-superficie)]"
        role="img"
        aria-label={`Red de ${grafo.nodos.length} actores y ${grafo.aristas.length} vínculos`}
      >
        <ReactFlow
          nodes={nodos}
          edges={aristas}
          nodeTypes={TIPOS_NODO}
          onNodesChange={soloMover}
          fitView
          fitViewOptions={{ padding: 0.18 }}
          minZoom={0.4}
          maxZoom={1.6}
          nodesConnectable={false}
          edgesFocusable={false}
          proOptions={{ hideAttribution: true }}
          className="[&_.react-flow__controls-button]:border-[var(--color-borde)] [&_.react-flow__controls-button]:bg-[var(--color-fondo)] [&_.react-flow__controls-button]:fill-[var(--color-texto-tenue)]"
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={16}
            size={1}
            color="var(--color-borde)"
          />
          <Controls showInteractive={false} className="!shadow-none" />
        </ReactFlow>
      </div>

      <ul className="mt-3 space-y-2">
        {grafo.aristas.map((a, i) => (
          <li
            key={i}
            className="border border-[var(--color-borde)] bg-[var(--color-superficie)] px-3 py-2 text-sm"
          >
            <span className="font-medium">{porId.get(a.origen)?.nombre ?? a.origen}</span>{' '}
            <span className="text-[var(--color-texto-tenue)]">{a.tipo.replace(/_/g, ' ')}</span>{' '}
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
