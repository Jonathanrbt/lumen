"""Motor de las 8 senales deterministas. Dueno: Jonatin (B1).

La IA narra y contextualiza estas reglas, no las inventa. Que sean deterministas
es una decision de producto: la trazabilidad es parte del entregable, y cada senal
tiene que poder explicarse con su regla, su dato y su fuente.

Senales del MVP: S1 a S8 y S10. S9 (adiciones significativas) va al roadmap.
"""

from .motor import analizar, red

__all__ = ["analizar", "red"]
