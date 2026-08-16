#!/usr/bin/env bash
#
# Aplica las migraciones de supabase/migrations/ en orden. Dueno: Cristian (B3).
#
# Existe porque la CLI de Supabase no esta instalada en todas las maquinas del
# equipo y a esta hora nadie quiere pelear con un `brew install`. Solo necesita
# psql y la cadena de conexion.
#
#   1. Crea el proyecto en https://supabase.com/dashboard
#   2. Project Settings -> Database -> Connection string -> URI
#   3. Pegala en .env como SUPABASE_DB_URL=postgresql://postgres:...@...
#   4. bash scripts/aplicar_migraciones.sh
#
# Las migraciones son idempotentes (todo es CREATE TABLE IF NOT EXISTS), asi
# que correrlo dos veces no rompe nada.

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIGRACIONES="$RAIZ/supabase/migrations"

if [ ! -f "$RAIZ/.env" ]; then
    echo "ERROR: no existe .env en la raiz del repo."
    echo "       cp .env.example .env  y pega los valores reales."
    exit 1
fi

# Solo leemos la linea que nos interesa; no volcamos el .env entero al entorno.
DB_URL="$(grep -E '^SUPABASE_DB_URL=' "$RAIZ/.env" | head -1 | cut -d= -f2-)"

if [ -z "$DB_URL" ]; then
    echo "ERROR: SUPABASE_DB_URL esta vacia en .env."
    echo "       Supabase Dashboard -> Project Settings -> Database -> Connection string (URI)"
    exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
    echo "ERROR: psql no esta instalado.  brew install libpq  (o postgresql)"
    exit 1
fi

echo "Aplicando migraciones de $MIGRACIONES"

for archivo in "$MIGRACIONES"/*.sql; do
    [ -e "$archivo" ] || continue
    echo ""
    echo "--> $(basename "$archivo")"
    # ON_ERROR_STOP hace que un error corte aqui en vez de seguir dejando la
    # base a medio migrar, que es peor que no migrar.
    psql "$DB_URL" -v ON_ERROR_STOP=1 -q -f "$archivo"
    echo "    ok"
done

echo ""
echo "Listo. Comprueba las tablas con:"
echo "  psql \"\$SUPABASE_DB_URL\" -c '\\dt'"
