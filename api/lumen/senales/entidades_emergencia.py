"""Entidades del Modo Emergencia (sismo 10.ago.2026). Dueno: Jonatin (B1).

Lista corta para el monitor de Cristian. Croma no acepta departamento:
hay que recorrer cada NIT con secop_processes_by_entity y from_date=2026-08-11.

Cristian puede importar esto; no hace falta copiar a mano. No edites este
archivo si no eres B1: un NIT mal puesto dispara el radar sobre la entidad equivocada.

Verificado en vivo contra api.croma.run el 15.ago.2026 ~23:50 (hora Bogotá).
"""

from __future__ import annotations

from datetime import date

FECHA_APERTURA = date(2026, 8, 11)
HERRAMIENTA_CROMA = "secop_processes_by_entity"

ENTIDADES_EMERGENCIA: list[dict[str, str]] = [
    {"nombre": "Santiago de Cali Distrito Especial", "nit": "890399011"},
    {"nombre": "Alcaldía Distrital de Buenaventura", "nit": "890399045"},
    {"nombre": "Gobernación del Valle del Cauca", "nit": "890399029"},
    {"nombre": "Gobernación del Chocó", "nit": "891680010"},
]


def nits() -> list[str]:
    return [e["nit"] for e in ENTIDADES_EMERGENCIA]
