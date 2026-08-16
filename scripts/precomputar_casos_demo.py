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

# Sujetos que Jonatin (B1) verifico EN VIVO contra Croma, con lo que salio de
# cada uno (tabla en docs/handoff/JONATIN-B1.md). No se inventa ninguno: los
# que el marco como no resueltos van en None y el script los salta avisando.
#
# `clave`: que campo de AnalizarRequest usar. Un NIT de entidad publica va como
# `entidad_id` (el motor le busca procesos); un proveedor va como `nit`.
CATALOGO_CURADO: dict[str, dict[str, str] | None] = {
    # Verificados con datos reales:
    "Proveedor con contratos SECOP": {"nit": "79372917"},
    "Entidades de Bogotá": {"entidad_id": "899999061"},
    # Verificados en RUES pero con 0 contratos en SECOP: el caso sale delgado
    # (sin señales de contratacion), aun asi es real y sirve de contraste.
    "Ruta del Sol / Odinsa": {"nit": "800169499"},
    "Conalvías (en liquidación)": {"nit": "890318278"},
    # Sin resolver. Jonatin: "Metro de Bogota no aparece como Empresa Metro en
    # RUES. No inventar." y el NIT que se creia de la UNGRD (900144920) da 0
    # procesos, asi que no se usa.
    "Metro de Bogotá": None,
    "UNGRD 2024": None,
}


async def main() -> None:
    casos = []

    for nombre, llaves in CATALOGO_CURADO.items():
        if not llaves:
            print(f"[omitido] {nombre}: sin identificador verificado (ver CATALOGO_CURADO)")
            continue

        try:
            caso = await analizar(AnalizarRequest(**llaves))
        except HTTPException as err:
            print(f"[omitido] {nombre}: /analizar respondió {err.status_code} — {err.detail}")
            continue

        # Guardar en Supabase es deseable, no imprescindible: el dump es un
        # archivo versionado y su razon de ser es sobrevivir a que la red o la
        # base fallen. Si no hay base, se genera igual y se avisa.
        try:
            guardar_caso(caso)
            persistido = "guardado en Supabase"
        except Exception as err:  # noqa: BLE001 - el dump es el entregable, no la fila
            persistido = f"NO guardado ({type(err).__name__})"

        casos.append(json.loads(caso.model_dump_json()))
        print(
            f"[ok] {nombre} -> {caso.id} "
            f"({len(caso.senales)} señales, nivel {caso.nivel_atencion.value}, {persistido})"
        )

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
