"""Canal de WhatsApp. Dueno: Freddy (B2), desde las 22:14 (ver docs/PLAN.md y
docs/handoff/FREDDY-B2.md).

Un solo punto de entrada, `enviar_alerta`, igual que `llm_client` es el unico
punto de entrada al LLM: todo lo que manda un WhatsApp pasa por aqui y solo
por aqui. Por dentro, `LUMEN_WHATSAPP_PROVIDER` decide si el envio real lo
hace Twilio o Evolution API — cambiar de proveedor es cambiar una variable de
entorno, no reescribir el router de Cristian.

Regla que no se negocia (viene del fallback de Cristian y sigue aplicando):
nunca se simula un envio. Si el proveedor no esta configurado o falla, el
estado es 'error', jamas 'enviado'.
"""

from __future__ import annotations

from .cliente import enviar_alerta

__all__ = ["enviar_alerta"]
