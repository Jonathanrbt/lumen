"""Precomputa los 6 casos del catalogo curado y genera fixtures/casos_demo.json.

Dueno: Cristian (B3). El catalogo de NIT/entidad_id por caso lo valida Jonatin
(B1) a mano (docs/brief-final-claude.md SS4.5.4) — este script no inventa esos
identificadores, los consume de CATALOGO_CURADO de abajo.

Uso (desde la raiz del repo, con .env cargado):

    .venv/bin/python scripts/precomputar_casos_demo.py

Requiere CROMA_API_KEY y SUPABASE_* configurados: llama al motor real
(`/analizar`, de Jonatin) para cada caso y lo persiste en Supabase antes de
exportarlo. Si `/analizar` todavia no esta implementado, cada caso se salta
con un aviso — no rompe el script, pero tampoco produce nada nuevo.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "api"))

from fastapi import HTTPException  # noqa: E402

from lumen.contracts import AnalizarRequest  # noqa: E402
from lumen.plataforma.casos import guardar_caso  # noqa: E402
from lumen.routers.analisis import analizar  # noqa: E402

DESTINO = RAIZ / "fixtures" / "casos_demo.json"

# TODO(Jonatin/B1): completar nit o entidad_id de cada caso validado a mano
# (brief SS4.5.4, catalogo curado de 6 casos). Mientras el valor sea None, el
# script salta ese caso y avisa por consola en vez de inventar un identificador.
CATALOGO_CURADO: dict[str, str | None] = {
    "Metro de Bogotá": None,
    "Ruta del Sol": None,
    "Centros Poblados / MinTIC": None,
    "UNGRD 2024": None,
    "Mocoa 2017": None,
    "Providencia post-Iota 2020": None,
}


async def main() -> None:
    casos = []

    for nombre, nit in CATALOGO_CURADO.items():
        if not nit:
            print(f"[omitido] {nombre}: falta nit/entidad_id en CATALOGO_CURADO")
            continue

        try:
            caso = await analizar(AnalizarRequest(nit=nit))
        except HTTPException as err:
            print(f"[omitido] {nombre}: /analizar respondió {err.status_code} — {err.detail}")
            continue

        guardar_caso(caso)
        casos.append(json.loads(caso.model_dump_json()))
        print(f"[ok] {nombre} -> {caso.id}")

    if not casos:
        print(
            "Ningún caso calculado todavía: completa CATALOGO_CURADO y confirma que "
            "/analizar (Jonatin/B1) ya está implementado."
        )
        return

    DESTINO.write_text(
        json.dumps(
            {
                "_nota": "Generado por scripts/precomputar_casos_demo.py. Reemplaza al placeholder.",
                "casos": casos,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Escrito {DESTINO} con {len(casos)} caso(s).")


if __name__ == "__main__":
    asyncio.run(main())
