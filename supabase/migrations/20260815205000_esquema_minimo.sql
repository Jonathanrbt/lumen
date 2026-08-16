-- Esquema minimo de Lumen. Dueno: Cristian (B3) — unico que escribe migraciones.
--
-- Tres tablas, no cinco: `casos` guarda el objeto completo como jsonb en vez de
-- normalizar senales/lecturas en tablas propias (design.md, change
-- plataforma-b3-flujo-completo, Decision 3). Para 6 casos curados mas lo que
-- entre el monitor en 12 horas, normalizar de mas cuesta tiempo que no se
-- recupera en valor de consulta. Si Jonatin o Freddy necesitan consultar
-- senales o lecturas sueltas, se piden por el chat y se anaden entonces.

create extension if not exists "pgcrypto";

-- El objeto Caso completo (contracts/modelos.py), mas las columnas que el
-- propio backend necesita para filtrar sin deserializar el jsonb entero.
create table if not exists casos (
    id text primary key,
    contrato_id text,
    modo text not null,
    nivel_atencion text not null,
    municipio text,
    departamento text,
    cuerpo jsonb not null,
    creado_en timestamptz not null default now(),
    actualizado_en timestamptz not null default now()
);

create unique index if not exists casos_contrato_id_idx
    on casos (contrato_id)
    where contrato_id is not null;

create index if not exists casos_departamento_idx on casos (departamento);
create index if not exists casos_nivel_atencion_idx on casos (nivel_atencion);

-- Quien quiere alertas de WhatsApp, por municipio o departamento.
create table if not exists suscripciones_whatsapp (
    id uuid primary key default gen_random_uuid(),
    telefono text not null,
    municipio text,
    departamento text,
    creado_en timestamptz not null default now(),
    unique (telefono, municipio, departamento)
);

create index if not exists suscripciones_municipio_idx on suscripciones_whatsapp (municipio);
create index if not exists suscripciones_departamento_idx on suscripciones_whatsapp (departamento);

-- Cache de respuestas de Croma: protege la cuota compartida del token entre
-- las 4 personas y el monitor (plataforma/cache-croma).
create table if not exists cache_croma (
    clave text primary key,
    herramienta text not null,
    argumentos jsonb not null,
    respuesta jsonb not null,
    consultado_en timestamptz not null
);

create index if not exists cache_croma_herramienta_idx on cache_croma (herramienta);

-- ---------------------------------------------------------------------------
-- Row Level Security: se activa SIN politicas, a proposito.
--
-- La llave `anon` de Supabase esta pensada para ser publica (vive en el
-- frontend). Sin RLS, cualquiera con esa llave lee estas tablas enteras — y
-- `suscripciones_whatsapp` guarda TELEFONOS de veedoras. Eso choca de frente
-- con el guardarrail 4 del brief: "no exponer datos sensibles de personas".
--
-- Activar RLS y no declarar ninguna politica = nadie entra por `anon` ni por
-- `authenticated`. El backend no se entera: usa SUPABASE_SERVICE_ROLE_KEY, y
-- el rol `service_role` se salta RLS por diseño.
--
-- Si algun dia el frontend de Andrew quiere leer casos directo de Supabase sin
-- pasar por la API, entonces SI hay que escribir una politica de solo lectura
-- para `casos` — y solo para `casos`, nunca para suscripciones.
-- ---------------------------------------------------------------------------

alter table casos enable row level security;
alter table suscripciones_whatsapp enable row level security;
alter table cache_croma enable row level security;
