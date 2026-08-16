"""Cliente perezoso de Supabase. Dueno: Cristian (B3).

Un solo proyecto cloud compartido (§5.3 del brief). Este modulo no crea el
proyecto ni corre migraciones: eso es `supabase/migrations/` y la Supabase CLI.
Aqui solo se resuelve el cliente con el que el resto de `plataforma/` lee y
escribe.
"""

from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from ..config import get_settings


class SupabaseNoConfigurado(RuntimeError):
    """Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en el entorno.

    No es un error de red: es que nadie ha copiado `.env.example` a `.env` con
    los valores reales, o que el proyecto de Supabase todavia no existe.
    """


@lru_cache
def get_supabase() -> Client:
    ajustes = get_settings()
    if not ajustes.supabase_url or not ajustes.supabase_service_role_key:
        raise SupabaseNoConfigurado(
            "SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY vacios. Copia .env.example a "
            ".env y pega los valores del proyecto de Supabase, o activa "
            "LUMEN_USAR_DUMP_LOCAL=true para leer del dump versionado."
        )
    return create_client(ajustes.supabase_url, ajustes.supabase_service_role_key)
