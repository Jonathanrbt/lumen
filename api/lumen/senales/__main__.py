"""CLI: python -m lumen.senales --nit 79372917"""

from __future__ import annotations

import argparse
import asyncio
import json

from lumen.contracts import AnalizarRequest
from lumen.senales.motor import analizar


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Corre el motor de señales contra Croma.")
    parser.add_argument("--nit", default=None)
    parser.add_argument("--entidad-id", default=None)
    parser.add_argument("--contrato-id", default=None)
    args = parser.parse_args()
    if not any([args.nit, args.entidad_id, args.contrato_id]):
        parser.error("pasa --nit, --entidad-id o --contrato-id")
    caso = await analizar(
        AnalizarRequest(nit=args.nit, entidad_id=args.entidad_id, contrato_id=args.contrato_id)
    )
    print(json.dumps(json.loads(caso.model_dump_json()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
