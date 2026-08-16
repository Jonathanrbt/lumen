"""Servidor MCP de Lumen. Dueno: Cristian (B3).

Expone el motor como herramientas para agentes externos (Claude, Cursor) en la
ruta `/mcp` del mismo servicio que sirve los nueve endpoints HTTP.

Cuatro modulos, cada uno con un trabajo:

    instrucciones.py  -> el manual que se le entrega al agente que se conecta
    prompts.py        -> las aperturas de conversacion
    herramientas.py   -> las nueve tools sobre las funciones del motor
    auth.py           -> el guardia de bearer token que envuelve la sub-app
    servidor.py       -> arma todo y lo deja listo para montar

Lo que este paquete NO hace: un segundo motor. Cada herramienta llama a la
misma funcion que ya usa su router HTTP (`senales.motor`, `ia.resolver`, ...).
"""

from __future__ import annotations

from .servidor import RUTAS_MCP, app_mcp, lifespan_mcp, servidor_mcp

__all__ = ["RUTAS_MCP", "app_mcp", "lifespan_mcp", "servidor_mcp"]
