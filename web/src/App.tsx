import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Link, NavLink, Navigate, Outlet, Route, Routes } from 'react-router'
import { IdiomaContext, useEstadoIdioma } from './lib/copy'
import { usandoFixtures } from './lib/api'
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

  return (
    <QueryClientProvider client={cliente}>
      <IdiomaContext value={idioma}>
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
      </IdiomaContext>
    </QueryClientProvider>
  )
}

/**
 * El marco de la aplicación. Ancho de teléfono a propósito: el jurado ve un video
 * de 60 segundos grabado a tamaño real, y un dashboard a todo lo ancho es
 * ilegible ahí.
 */
function Marco() {
  return (
    <div className="mx-auto flex min-h-dvh max-w-2xl flex-col px-5">
      <header className="sticky top-0 z-10 -mx-5 border-b border-[var(--color-borde)] bg-[color-mix(in_oklch,var(--color-fondo)_85%,transparent)] px-5 py-3 backdrop-blur">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-sm font-semibold">
            <span
              className="h-3.5 w-3.5 rounded-full"
              style={{
                background:
                  'radial-gradient(circle at 35% 30%, oklch(1 0 0 / 0.7), var(--color-lumen))',
              }}
            />
            Lumen
          </Link>
          <nav className="flex gap-1 text-sm">
            <Pestana a="/app/vigilancia">Vigilancia</Pestana>
            <Pestana a="/app/emergencia">Emergencia</Pestana>
          </nav>
        </div>
        {usandoFixtures && (
          <p className="mt-2 text-[11px] text-[var(--color-texto-tenue)]">
            Datos de ejemplo · define <code>VITE_API_URL</code> para hablar con la API real
          </p>
        )}
      </header>

      <main className="flex-1 py-6">
        <Outlet />
      </main>
    </div>
  )
}

function Pestana({ a, children }: { a: string; children: React.ReactNode }) {
  return (
    <NavLink
      to={a}
      className={({ isActive }) =>
        `rounded-lg px-3 py-1.5 transition ${
          isActive
            ? 'bg-[var(--color-superficie-alta)] font-medium'
            : 'text-[var(--color-texto-tenue)] hover:text-[var(--color-texto)]'
        }`
      }
    >
      {children}
    </NavLink>
  )
}
