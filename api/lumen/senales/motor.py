"""Orquesta Croma y las 8 reglas. Un motor para los dos modos."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from ..contracts import AnalizarRequest, Caso, Grafo, ModoCaso, Senal
from ..croma.client import CromaClient
from . import extraer, grafo, nivel, s1, s10, s2, s3, s4, s5, s6, s7, s8
from .consultas import Consultas

log = logging.getLogger(__name__)

MAX_HERMANAS_RUES = 1


def id_caso(llave: str) -> str:
    """El id de un Caso a partir de su llave (contrato, NIT o entidad).

    Es determinista a proposito: la misma llave da siempre el mismo id, asi que
    re-analizar algo lo reemplaza en vez de duplicarlo. Publica desde el
    16.ago porque `ia/chat.py` la necesita para preguntarle a Supabase si un
    caso ya existe **antes** de gastar 80 segundos de Croma re-analizandolo
    (brief §4.6, Flujo B paso 4: "si el caso ya esta cacheado, responde al
    instante"). Era `_id_caso`; solo cambio el nombre.
    """
    return "caso-" + hashlib.sha256(llave.encode("utf-8")).hexdigest()[:12]


def _contratos_de(datos: Any) -> list[dict[str, Any]]:
    if isinstance(datos, dict) and extraer.es_encontrado(datos):
        contrato = datos.get("contract")
        if isinstance(contrato, dict):
            return [contrato]
    return extraer.lista(datos, "contracts")


async def analizar(peticion: AnalizarRequest) -> Caso:
    async with CromaClient() as croma:
        q = Consultas(croma)
        return await _analizar(peticion, q)


async def red(nit: str) -> Grafo:
    async with CromaClient() as croma:
        q = Consultas(croma)
        caso = await _analizar(AnalizarRequest(nit=nit), q)
        return caso.grafo or Grafo()


async def _analizar(peticion: AnalizarRequest, q: Consultas) -> Caso:
    modo = ModoCaso.VIGILANCIA
    contrato_foco: dict[str, Any] = {}
    contratos: list[dict[str, Any]] = []
    nit = extraer.nit_limpio(peticion.nit)
    entidad_id = extraer.nit_limpio(peticion.entidad_id)
    contrato_id = extraer.texto(peticion.contrato_id)

    if contrato_id:
        modo = ModoCaso.EMERGENCIA
        detalle = await q.get("secop_contract", {"contract_id": contrato_id})
        contratos = _contratos_de(detalle)
        if contratos:
            contrato_foco = contratos[0]
            nit = extraer.nit_limpio(contrato_foco.get("provider_document")) or nit
            entidad_id = extraer.nit_limpio(contrato_foco.get("entity_nit")) or entidad_id

    if nit:
        lista_prov = await q.get("secop_contracts_by_provider", {"document_number": nit})
        contratos = _contratos_de(lista_prov) or contratos
        if not contrato_foco and contratos:
            contrato_foco = contratos[0]
        if not entidad_id and contrato_foco:
            entidad_id = extraer.nit_limpio(contrato_foco.get("entity_nit"))

    procesos: list[dict[str, Any]] = []
    if entidad_id:
        proc = await q.get(
            "secop_processes_by_entity",
            {"document_number": entidad_id, "page": 1},
        )
        procesos = extraer.lista(proc, "processes")

    if not contrato_foco and procesos:
        procesos_ord = sorted(
            procesos,
            key=lambda p: extraer.numero(p.get("base_price")) or 0,
            reverse=True,
        )
        contrato_foco = procesos_ord[0]

    rues: Any = {"found": False}
    if nit:
        rues = await q.get("rues_entity_by_nit", {"document_number": nit})

    contratos_entidad = [
        c
        for c in contratos
        if not entidad_id or extraer.nit_limpio(c.get("entity_nit")) == entidad_id
    ] or contratos

    senales: list[Senal] = []

    if contrato_foco:
        s = s1.evaluar(rues, contrato_foco, q.consultado_en)
        if s:
            senales.append(s)

    contratos_hermana: list[dict[str, Any]] = []
    for nit_h, _nombre in s2.nits_relacionados(rues)[:MAX_HERMANAS_RUES]:
        if entidad_id:
            h = await q.get(
                "secop_contracts_by_provider",
                {"document_number": nit_h, "entity_nit": entidad_id},
            )
        else:
            h = await q.get("secop_contracts_by_provider", {"document_number": nit_h})
        contratos_hermana = _contratos_de(h)
        if contratos_hermana:
            break
    if nit:
        s = s2.evaluar(rues, nit, contratos_hermana, q.consultado_en)
        if s:
            senales.append(s)

    if nit:
        tipo_doc = "NIT" if nit and len(nit) >= 9 else "CC"
        sanciones = await q.get("secop_sanctions_by_provider", {"document_number": nit})
        procuraduria = await q.get(
            "procuraduria_disciplinary_records",
            {"document_number": nit, "document_type": tipo_doc if tipo_doc in {"CC", "CE", "NIT"} else "CC"},
        )
        contraloria: Any = {"found": False}
        if tipo_doc == "CC":
            contraloria = await q.get(
                "contraloria_fiscal_records",
                {"document_number": nit, "document_type": "CC"},
            )
        s = s3.evaluar(sanciones, procuraduria, contraloria, contratos, q.consultado_en)
        if s:
            senales.append(s)

        if tipo_doc == "NIT":
            estados = await q.get(
                "supersociedades_financial_statements", {"document_number": nit}
            )
        else:
            estados = {"found": False}
        if contrato_foco:
            s = s4.evaluar(rues, estados, contrato_foco, q.consultado_en)
            if s:
                senales.append(s)

        sicaac = await q.get(
            "sicaac_insolvency_cases",
            {"document_number": nit, "document_type": tipo_doc},
        )
        s = s5.evaluar(sicaac, contratos, q.consultado_en)
        if s:
            senales.append(s)

        bdme = await q.get(
            "contaduria_state_delinquent_debtors",
            {"document_number": nit, "document_type": tipo_doc},
        )
        s = s10.evaluar(bdme, contratos, q.consultado_en)
        if s:
            senales.append(s)

    s = s6.evaluar(contratos_entidad or procesos, q.consultado_en)
    if s:
        senales.append(s)

    if contratos_entidad and procesos:
        s = s7.evaluar(contratos_entidad, procesos, q.consultado_en)
        if s:
            senales.append(s)

    s = s8.evaluar(contratos_entidad or contratos, q.consultado_en)
    if s:
        senales.append(s)

    nombre_prov = extraer.texto(contrato_foco.get("provider"))
    if extraer.es_encontrado(rues) and isinstance(rues, dict):
        entidad_rues = rues.get("entity") if isinstance(rues.get("entity"), dict) else rues
        nombre_prov = extraer.texto(entidad_rues.get("name")) or nombre_prov

    entidad_nombre = extraer.texto(contrato_foco.get("entity")) or entidad_id or "Entidad no identificada"
    municipio = None
    departamento = None
    loc = extraer.texto(contrato_foco.get("location"))
    if loc:
        partes = [p.strip() for p in loc.split(",") if p.strip()]
        if len(partes) >= 3:
            departamento = partes[1]
            municipio = partes[2]
        elif len(partes) == 2:
            departamento = partes[0]
            municipio = partes[1]

    red = grafo.armar(
        nit_proveedor=nit,
        nombre_proveedor=nombre_prov,
        entidad=entidad_nombre,
        entidad_nit=entidad_id,
        rues=rues,
        contratos=contratos,
        consultado_en=q.consultado_en,
    )

    llave = contrato_id or nit or entidad_id or "sin-llave"
    valor = extraer.numero(contrato_foco.get("value") or contrato_foco.get("base_price"))
    fecha = None
    from .pesos import a_fecha

    fecha = a_fecha(contrato_foco.get("sign_date") or contrato_foco.get("published_date"))

    return Caso(
        id=id_caso(llave),
        modo=modo,
        entidad=entidad_nombre,
        proveedor=nombre_prov,
        municipio=municipio,
        departamento=departamento,
        valor=valor,
        objeto=extraer.texto(contrato_foco.get("object") or contrato_foco.get("name")),
        fecha=fecha,
        nivel_atencion=nivel.desde_senales(senales),
        senales=senales,
        lectura=None,
        grafo=red,
        narracion=None,
        generado_en=datetime.now(timezone.utc),
    )
