# Handoff — Cristian · B3 Plataforma

**Soy dueño de:** `api/lumen/plataforma/`, `api/lumen/routers/plataforma.py`, `api/lumen/main.py`,
`api/lumen/config.py`, `supabase/`, `scripts/`, `render.yaml`.
**Mis endpoints:** `GET /caso/{caso_id}`, `GET /monitor/nuevos`, `POST /alerta`.
**Mi hito:** 23:00 — el flujo completo corre de extremo a extremo, aunque sea feo.
**Soy el único que escribe migraciones de Supabase.** Si alguien necesita una tabla o una columna, me
la pide por el chat.
**Desde las 22:00 soy suplente de Jonatin** para la revisión final de señales y fuentes, porque él
se va al video.

> Se actualiza al cerrar cada bloque: 20:45, 22:00, 23:00, 02:00.

---

## Lo primero, y es urgente

**Deja un hello world desplegado en Render antes de las 19:00.** El brief lo dejaba para las 03:30 y
eso es un error: un despliegue que se estrena de madrugada es un despliegue que falla de madrugada.
Con `render.yaml` en la raíz y el repo conectado debería costar quince minutos. El agente de Jonatin
tiene Render conectado por MCP y puede crear el servicio, poner las variables de entorno y disparar
el deploy sin salir del editor — pídeselo si te sirve.

Está listo cuando la URL de Render responde `/health` **desde el celular de alguien, con datos
móviles.** No desde tu navegador con la caché caliente.

## Después

1. **Crear el proyecto de Supabase** y la primera migración. Un solo proyecto cloud compartido; nadie
   levanta Docker.
2. **Tablas mínimas** para que el flujo cierre: casos, señales, lecturas, suscripciones de WhatsApp,
   y una tabla de cache de respuestas de Croma (importante: el token es compartido y tiene cuota).
3. **El monitor.** Despierta, pide a Croma los contratos nuevos con causal de urgencia en los
   departamentos afectados desde el 11 de agosto, descarta lo que ya está en base, y arma casos.
4. **Twilio**, si el equipo resuelve la cuenta. Es el hard-cut #3: si a la hora no llegó un mensaje
   real a un teléfono real, se corta y el video muestra la alerta dentro de la plataforma. **No se
   mockea un WhatsApp falso.**
5. **Precomputar y cachear los 6 casos del catálogo, y generar el dump JSON** versionado en
   `fixtures/casos_demo.json`. Con `LUMEN_USAR_DUMP_LOCAL=true` la API responde desde ahí sin tocar
   Supabase ni Croma. Es el respaldo de grabación: existe para que un corte de red a las 07:00 no
   cueste el hackathon.

## Dos detalles que muerden si se descubren tarde

**CORS.** Andrew despliega el frontend en un dominio que todavía no sabemos. En cuanto lo tenga, va
a `LUMEN_CORS_ORIGINS` en local y en las variables de entorno de Render. Si esto se descubre a las
02:00, se pierden treinta minutos justo en la integración.

**Zona horaria.** Render corre en UTC y nosotros razonamos en hora de Bogotá, que es UTC-5. Todas
las fechas que salgan a Croma (`from_date`, `to_date`) y todo lo que se guarde en base va explícito.
"Desde el 11 de agosto" tiene que significar lo mismo en las dos máquinas.

---

## Bitácora

### 17:30 — Punto de partida

`api/lumen/main.py` y `api/lumen/config.py` ya están escritos y funcionando: la app arranca, tiene
CORS configurable por entorno, `/health`, `/health/croma` y los nueve endpoints declarados. Mis tres
endpoints están en `api/lumen/routers/plataforma.py` devolviendo `501`.

Nada de Supabase existe todavía. Nada está desplegado todavía.
