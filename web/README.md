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

## Al desplegar

Avisarle a Cristian (B3) el dominio para que entre en `LUMEN_CORS_ORIGINS` en Render.
