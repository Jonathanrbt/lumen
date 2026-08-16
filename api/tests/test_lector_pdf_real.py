"""Pruebas del lector contra PDFs reales (sin mockear la extracción).

`preguntar` sigue mockeado (no gasta presupuesto en CI), pero `pypdf` corre
de verdad sobre bytes de PDF reales, para no dar por buena una función de
extracción que en realidad nunca se probó contra un PDF. `_pdf_con_texto`
construye un PDF válido a mano (sintaxis cruda, sin dependencias nuevas):
no hace falta una librería de generación solo para un test.
"""

from __future__ import annotations

import asyncio
import io

import pytest
from pypdf import PdfWriter

from lumen.contracts import Veredicto
from lumen.ia import lector


def _run(coro):
    return asyncio.run(coro)


def _pdf_en_blanco() -> bytes:
    escritor = PdfWriter()
    escritor.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    escritor.write(buffer)
    return buffer.getvalue()


def _pdf_con_texto(texto: str) -> bytes:
    """PDF de una página, válido, con `texto` como único contenido."""
    contenido_stream = f"BT /F1 12 Tf 72 700 Td ({texto}) Tj ET".encode("latin-1")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(contenido_stream)} >>\nstream\n".encode("latin-1")
        + contenido_stream
        + b"\nendstream",
    ]

    partes = [b"%PDF-1.4\n"]
    offsets = [0]
    for i, obj in enumerate(objetos, start=1):
        offsets.append(sum(len(p) for p in partes))
        partes.append(f"{i} 0 obj\n".encode("latin-1") + obj + b"\nendobj\n")

    xref_offset = sum(len(p) for p in partes)
    n = len(objetos) + 1
    xref = [f"xref\n0 {n}\n0000000000 65535 f \n".encode("latin-1")]
    for off in offsets[1:]:
        xref.append(f"{off:010d} 00000 n \n".encode("latin-1"))
    partes.extend(xref)
    partes.append(f"trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("latin-1"))
    return b"".join(partes)


def test_pdf_real_sin_texto_da_documento_ilegible() -> None:
    with pytest.raises(lector.DocumentoIlegible):
        lector._texto_por_pagina(_pdf_en_blanco())


def test_pdf_corrupto_da_documento_ilegible() -> None:
    with pytest.raises(lector.DocumentoIlegible):
        lector._texto_por_pagina(b"esto no es un PDF")


def test_pdf_con_texto_real_se_extrae_y_llega_al_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    contenido = _pdf_con_texto("Objeto: suministro de mobiliario de oficina.")

    capturado = {}

    async def _preguntar_falso(prompt: str, modelo) -> str:
        capturado["prompt"] = prompt
        return """{"veredicto": "sin_relacion", "puntos": [
            {"hallazgo": "a", "cita_textual": null, "pagina": null, "no_concluye_por": "a"},
            {"hallazgo": "b", "cita_textual": null, "pagina": null, "no_concluye_por": "b"},
            {"hallazgo": "c", "cita_textual": null, "pagina": null, "no_concluye_por": "c"}
        ]}"""

    monkeypatch.setattr(lector, "preguntar", _preguntar_falso)

    resultado = _run(lector.leer_justificacion(contenido))

    assert resultado.veredicto == Veredicto.SIN_RELACION
    assert "mobiliario de oficina" in capturado["prompt"]
    assert "Página 1" in capturado["prompt"]
