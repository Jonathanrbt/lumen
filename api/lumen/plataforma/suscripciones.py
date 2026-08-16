"""Suscriptores de WhatsApp por alcance geografico. Dueno: Cristian (B3).

Spec `plataforma/alertas-whatsapp`: cuando un Caso llega a nivel medio o alto,
el monitor necesita saber a quien avisar en ese municipio o departamento.
"""

from __future__ import annotations

from .supabase_client import get_supabase

TABLA = "suscripciones_whatsapp"


def listar_suscriptores(municipio: str | None, departamento: str | None) -> list[str]:
    if not municipio and not departamento:
        return []

    supabase = get_supabase()
    consulta = supabase.table(TABLA).select("telefono")
    consulta = consulta.eq("municipio", municipio) if municipio else consulta.eq(
        "departamento", departamento
    )
    resultado = consulta.execute()
    return [fila["telefono"] for fila in resultado.data]
