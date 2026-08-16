import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { BrowserRouter, Link, NavLink, Navigate, Outlet, Route, Routes } from 'react-router'
import { IdiomaContext, useEstadoIdioma } from './lib/copy'
import { HistorialContext, useEstadoHistorial, useHistorial } from './lib/historial'
import { usandoFixtures } from './lib/api'
import { Marca } from './componentes/Marca'
import { PantallaLanding } from './pantallas/Landing'
import { PantallaChat } from './pantallas/Chat'
import { PantallaCaso } from './pantallas/Caso'
import { PantallaArtefacto } from './pantallas/Artefacto'
import { PantallaAlerta } from './pantallas/Alerta'

const cliente = new QueryClient({
  // Analizar un caso cuesta llamadas a Croma y a dos modelos: no se repite sola.
  defaultOptions: { queries: { refetchOnWindowFocus: false, staleTime: 5 * 60_000 } },
})

export default function App() {
  const idioma = useEstadoIdioma()
  const historial = useEstadoHistorial()

  return (
    <QueryClientProvider client={cliente}>
      <IdiomaContext value={idioma}>
        <HistorialContext value={historial}>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<PantallaLanding />} />
              <Route path="/app" element={<Marco />}>
                <Route index element={<Navigate to="/app/vigilancia" replace />} />
                <Route path="vigilancia" element={<PantallaChat />} />
                <Route path="emergencia" element={<PantallaAlerta />} />
                <Route path="caso/:id" element={<PantallaCaso />} />
                <Route path="caso/:id/artefacto" element={<PantallaArtefacto />} />
                <Route path="caso/:id/alerta" element={<PantallaAlerta />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </HistorialContext>
      </IdiomaContext>
    </QueryClientProvider>
  )
}

/**
 * El marco de la herramienta: panel de consultas a la izquierda, los dos modos
 * como pestañas arriba y el trabajo en el centro.
 *
 * La columna de trabajo se queda estrecha a propósito: el jurado ve un video de
 * 60 segundos grabado a tamaño real, y un dashboard a todo lo ancho es ilegible.
 */
function Marco() {
  const [panelAbierto, setPanelAbierto] = useState(true)

  useEffect(() => {
    document.documentElement.classList.add('tema-claro')
    return () => document.documentElement.classList.remove('tema-claro')
  }, [])

  return (
    <div className="flex min-h-dvh bg-[var(--color-superficie)]">
      {panelAbierto && <Panel onPlegar={() => setPanelAbierto(false)} />}

      <div className="flex min-w-0 flex-1 flex-col bg-[var(--color-fondo)] md:my-3 md:mr-3 md:border md:border-[var(--color-borde)]">
        <header className="flex items-center gap-4 border-b border-[var(--color-borde)] px-4 py-2.5">
          {panelAbierto ? (
            <Link to="/" aria-label="Lumen" className="md:hidden">
              <Marca tamano="sm" />
            </Link>
          ) : (
            <BotonPanel abierto={false} onClick={() => setPanelAbierto(true)} />
          )}

          <nav className="mx-auto flex gap-0.5 border border-[var(--color-borde)] bg-[var(--color-superficie)] p-0.5">
            <Pestana a="/app/vigilancia">Vigilancia</Pestana>
            <Pestana a="/app/emergencia">Emergencia</Pestana>
          </nav>
        </header>

        <main className="flex-1 px-4 py-6 sm:px-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

/** Panel lateral: abrir una consulta nueva y volver a las de esta sesión. */
function Panel({ onPlegar }: { onPlegar: () => void }) {
  const { consultas, activa, abrir, nueva } = useHistorial()

  return (
    <aside className="sticky top-0 hidden h-dvh w-60 shrink-0 flex-col overflow-y-auto px-3 py-4 md:flex">
      <div className="flex items-center justify-between pb-5 pl-2">
        <Link to="/" aria-label="Lumen">
          <Marca tamano="sm" />
        </Link>
        <BotonPanel abierto onClick={onPlegar} />
      </div>

      <button
        onClick={nueva}
        className="flex items-center gap-2.5 px-2 py-1.5 text-sm text-[var(--color-texto)] transition-colors hover:text-[var(--color-lumen)]"
      >
        <span aria-hidden className="text-[var(--color-lumen)]">
          +
        </span>
        Nueva consulta
      </button>

      <p className="mt-6 px-2 text-[0.6rem] uppercase tracking-[0.2em] text-[var(--color-texto-tenue)]">
        Recientes
      </p>

      {consultas.length === 0 ? (
        <p className="mt-3 px-2 text-xs leading-relaxed text-[var(--color-texto-tenue)]">
          Lo que preguntes en esta sesión queda listado aquí.
        </p>
      ) : (
        <ul className="mt-2 space-y-px overflow-y-auto">
          {consultas.map((consulta) => (
            <li key={consulta.id}>
              <button
                onClick={() => abrir(consulta.id)}
                className={`block w-full truncate px-2 py-1.5 text-left text-sm transition-colors ${
                  consulta.id === activa?.id
                    ? 'bg-[var(--color-superficie-alta)] text-[var(--color-texto)]'
                    : 'text-[var(--color-texto-tenue)] hover:text-[var(--color-texto)]'
                }`}
              >
                {consulta.titulo}
              </button>
            </li>
          ))}
        </ul>
      )}

      {usandoFixtures && (
        <p className="mt-auto border-t border-[var(--color-borde)] px-2 pt-3 text-[0.68rem] leading-relaxed text-[var(--color-texto-tenue)]">
          Datos de ejemplo · define <code>VITE_API_URL</code> para la API real
        </p>
      )}
    </aside>
  )
}

/** Pliega y despliega el panel, para dejar la conversación sola. */
function BotonPanel({ abierto, onClick }: { abierto: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      aria-label={abierto ? 'Esconder el panel' : 'Mostrar el panel'}
      className="grid h-7 w-7 shrink-0 place-items-center text-[var(--color-texto-tenue)] transition-colors hover:text-[var(--color-texto)]"
    >
      <svg
        aria-hidden
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="h-[18px] w-[18px]"
      >
        <rect x="3" y="4" width="18" height="16" rx="1" />
        <path d="M9.5 4v16" />
        {!abierto && <path d="M13.5 9.5 16 12l-2.5 2.5" />}
      </svg>
    </button>
  )
}

function Pestana({ a, children }: { a: string; children: React.ReactNode }) {
  return (
    <NavLink
      to={a}
      className={({ isActive }) =>
        `px-4 py-1.5 text-[0.7rem] uppercase tracking-[0.14em] transition ${
          isActive
            ? 'bg-[var(--color-fondo)] font-semibold text-[var(--color-texto)] shadow-sm'
            : 'text-[var(--color-texto-tenue)] hover:text-[var(--color-texto)]'
        }`
      }
    >
      {children}
    </NavLink>
  )
}
