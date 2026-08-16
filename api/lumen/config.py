"""Configuracion por variables de entorno. Cero secretos en el codigo.

Todo sale de `.env` (que esta en .gitignore) o del entorno de Render. La plantilla
con las llaves y sin los valores es `.env.example`.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

VERSION = "0.1.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Croma: fuente unica de datos (API HTTP; URL fija en el cliente) ---
    croma_api_key: str = ""

    # Interruptor general de Croma. En false, NINGUNA llamada sale a la red:
    # ni el motor, ni el monitor, ni /health/croma. El token es uno solo para
    # las cuatro personas y tiene creditos finitos.
    #
    # Por defecto True para que quien haga pull no se encuentre el backend
    # mudo sin saber por que; se apaga en el .env de cada uno.
    lumen_croma_habilitado: bool = True

    # --- IA ---
    cursor_api_key: str = ""
    lumen_modelo_rapido: str = "composer-2.5"
    lumen_modelo_fuerte: str = ""
    # El agente NUNCA apunta a la raiz del repo: lee archivos que nadie pidio y
    # quema presupuesto. Solo el documento que se esta analizando.
    lumen_scratch_dir: str = "./scratch"

    # --- Supabase ---
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_db_url: str = ""

    # --- Canal de alerta (api/lumen/telegram/, api/lumen/whatsapp/) ---
    # Dueno: Freddy (B2). "telegram" o "whatsapp". Telegram es el canal de la
    # demo desde las ~02:00 (sin trial, sin plantillas, bot en minutos);
    # WhatsApp queda funcional en el repo para quien lo revise, pero no se
    # muestra en video. Ver docs/handoff/FREDDY-B2.md.
    lumen_canal_alerta: str = "telegram"

    # Telegram Bot API
    telegram_bot_token: str = ""
    telegram_chat_id_demo: str = ""

    # --- WhatsApp (api/lumen/whatsapp/, dueno: Freddy B2 desde las 22:14) ---
    # "twilio" o "evolution". Se prueban los dos y se deja el que responda mejor.
    lumen_whatsapp_provider: str = "twilio"

    # Twilio (sandbox)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    twilio_whatsapp_to_demo: str = ""

    # Evolution API (alternativa a Twilio, si resuelve mejor)
    evolution_api_url: str = ""
    evolution_api_key: str = ""
    evolution_instance: str = ""
    evolution_whatsapp_to_demo: str = ""

    # --- Servidor MCP (api/lumen/mcp/, dueno: Cristian B3) ---
    # Credencial propia del servidor MCP. NO se reutiliza CROMA_API_KEY ni
    # SUPABASE_SERVICE_ROLE_KEY: compartir un secreto entre dos propositos
    # significa que rotar uno rompe el otro.
    #
    # Vacio por defecto y eso NO significa "abierto": el guardia responde 503
    # cuando no hay token configurado. Un servidor que deja pasar todo porque
    # falto una variable en Render es justo el fallo que esto evita.
    #
    #   python -c "import secrets; print(secrets.token_urlsafe(32))"
    lumen_mcp_token: str = ""

    # Interruptor del MCP, independiente del de Croma. Apagarlo desde el
    # dashboard de Render deja /mcp en 503 y el resto del servicio intacto:
    # es el rollback sin redesplegar.
    lumen_mcp_habilitado: bool = True

    # --- Aplicacion ---
    lumen_env: str = "local"
    lumen_log_level: str = "info"
    lumen_cors_origins: str = "*"

    # Dominio del frontend de Andrew, una vez lo declare. Solo se usa para
    # construir el enlace a la ficha dentro del mensaje de WhatsApp; no
    # reemplaza a LUMEN_CORS_ORIGINS, que es quien controla seguridad.
    lumen_frontend_url: str = ""

    # Tope de casos que arma el monitor por corrida. Las 4 entidades del sismo
    # suman ~427 procesos desde el 11.ago; analizarlos todos son varias llamadas
    # a Croma cada uno y el token es compartido. Ninguna demo necesita 427 casos.
    lumen_monitor_max_casos: int = 4

    # Respaldo de grabacion: la API responde desde el dump JSON versionado en vez
    # de tocar Supabase o Croma. Existe para que un corte de red a las 07:00 no
    # cueste el hackathon. No es la arquitectura.
    lumen_usar_dump_local: bool = False
    lumen_dump_path: str = "./fixtures/casos_demo.json"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.lumen_cors_origins.split(",") if o.strip()]

    @property
    def croma_configurado(self) -> bool:
        return bool(self.croma_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
