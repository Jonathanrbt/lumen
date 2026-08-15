"""llm_client, lector de justificaciones, prompts y artefactos. Dueno: Freddy (B2).

Todo lo que hable con un modelo pasa por un unico `llm_client`. Si a las 22:00 el
consumo se dispara o la latencia mata el chat, se cambia de proveedor en veinte
minutos y no en seis horas.

Presupuesto duro: US$50. Ver las seis reglas en HERRAMIENTAS.md.
"""
