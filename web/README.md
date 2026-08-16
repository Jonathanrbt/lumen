# web/ — frontend de Lumen

SPA en Vite + React + TypeScript + Tailwind v4. Sin SSR y sin autenticación: los nueve
endpoints del contrato son públicos y no hay sesiones que proteger.

```bash
npm install
npm run dev            # http://localhost:5173
```

**Sin configurar nada corre contra los fixtures del monorepo.** Para hablar con la API:

```bash
cp .env.example .env   # y pon VITE_API_URL
```

Con `VITE_API_URL` puesta llama a la API real y solo cae al fixture si la red falla, para
que un corte no deje la demo en blanco.

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm test` | Pruebas de formateo de fecha y plata |
| `npm run build` | Build de producción en `dist/` |
| `npm run deploy` | Build y publicación en Cloudflare Pages |

## Las pantallas

| Ruta | Pantalla |
|---|---|
| `/` | Landing, en español e inglés |
| `/app/vigilancia` | Chat del Modo Vigilancia |
| `/app/emergencia` | La alerta de WhatsApp del Modo Emergencia |
| `/app/caso/:id` | Ficha del caso: señales, lectura y grafo |
| `/app/caso/:id/artefacto` | Derecho de petición, con copiar y descargar |

El chat no duplica la ficha: importa `FichaCaso` y `TarjetaSenal` y las pinta dentro de
la conversación.

## Las dos puntas, conectadas

| Sentido | Dónde vive | Valor |
|---|---|---|
| Front → back | `VITE_API_URL` en `web/.env` | `https://lumen-api-cwt3.onrender.com` |
| Back → front | `LUMEN_FRONTEND_URL` en Render | `https://lumen-a1y.pages.dev` |

`VITE_API_URL` se congela **en el build**, no en tiempo de ejecución: si cambia la URL de la
API hay que volver a construir y desplegar, no basta con editar una variable en un panel.

`LUMEN_FRONTEND_URL` no controla CORS (`LUMEN_CORS_ORIGINS` está en `*`, seguro porque la API
monta CORS con `allow_credentials=False`). Solo arma el enlace que viaja dentro del mensaje de
WhatsApp, y ese enlace apunta a `/app/caso/{id}` — con el prefijo `/app`, porque el catch-all
del router manda todo lo demás al landing sin ningún error visible.
