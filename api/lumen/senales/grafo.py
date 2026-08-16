"""Subgrafo curado 5–12 nodos. Un hairball no se publica."""

from __future__ import annotations

from typing import Any

from ..contracts import Actor, Arista, Grafo, TipoActor
from . import extraer
from .fuentes import URL_RUES, URL_SECOP, fuente
from .s2 import nits_relacionados

MAX_NODOS = 12


def armar(
    *,
    nit_proveedor: str | None,
    nombre_proveedor: str | None,
    entidad: str | None,
    entidad_nit: str | None,
    rues: Any,
    contratos: list[dict[str, Any]],
    consultado_en,
) -> Grafo:
    nodos: list[Actor] = []
    aristas: list[Arista] = []
    ids: set[str] = set()

    def agregar(actor: Actor) -> None:
        if actor.id in ids or len(nodos) >= MAX_NODOS:
            return
        ids.add(actor.id)
        nodos.append(actor)

    if entidad_nit or entidad:
        eid = f"ent-{entidad_nit or 'sin-nit'}"
        agregar(
            Actor(
                id=eid,
                tipo=TipoActor.ENTIDAD,
                nombre=entidad or entidad_nit or "Entidad",
                nit=entidad_nit,
                rol="contratante",
            )
        )
    pid = f"prov-{nit_proveedor or 'desconocido'}"
    agregar(
        Actor(
            id=pid,
            tipo=TipoActor.EMPRESA,
            nombre=nombre_proveedor or nit_proveedor or "Proveedor",
            nit=nit_proveedor,
            rol="proveedor",
        )
    )
    if entidad_nit or entidad:
        eid = f"ent-{entidad_nit or 'sin-nit'}"
        if eid in ids and pid in ids:
            aristas.append(
                Arista(
                    origen=eid,
                    destino=pid,
                    tipo="contrato_a",
                    fuente=fuente("secop_contracts_by_provider", URL_SECOP, consultado_en),
                )
            )

    contrato = contratos[0] if contratos else {}
    rep = extraer.texto(contrato.get("legal_rep_name"))
    if rep:
        rid = "rep-contrato"
        agregar(
            Actor(id=rid, tipo=TipoActor.PERSONA, nombre=rep, nit=None, rol="representante legal")
        )
        if rid in ids and pid in ids:
            aristas.append(
                Arista(
                    origen=rid,
                    destino=pid,
                    tipo="representante_legal_de",
                    fuente=fuente("secop_contracts_by_provider", URL_SECOP, consultado_en),
                )
            )

    for nit_h, nombre_h in nits_relacionados(rues)[:2]:
        hid = f"herm-{nit_h}"
        agregar(
            Actor(
                id=hid,
                tipo=TipoActor.EMPRESA,
                nombre=nombre_h or nit_h,
                nit=nit_h,
                rol="empresa relacionada",
            )
        )
        if hid in ids and pid in ids:
            aristas.append(
                Arista(
                    origen=pid,
                    destino=hid,
                    tipo="representante_legal_compartido",
                    fuente=fuente("rues_entity_by_nit", URL_RUES, consultado_en),
                )
            )

    return Grafo(nodos=nodos, aristas=aristas)
