"""URLs oficiales que van debajo de cada señal. Las siglas viven aquí, no en la frase."""

from datetime import datetime, timezone

from ..contracts import Fuente

URL_RUES = "https://www.rues.org.co/"
URL_SECOP = "https://www.colombiacompra.gov.co/secop"
URL_PROCURADURIA = "https://www.procuraduria.gov.co/"
URL_CONTRALORIA = "https://www.contraloria.gov.co/"
URL_SICAAC = "https://www.supersociedades.gov.co/"
URL_CONTADURIA = "https://www.contaduria.gov.co/"
URL_SUPERSOCIEDADES = "https://www.supersociedades.gov.co/"


def fuente(herramienta: str, url: str, consultado_en: datetime) -> Fuente:
    if consultado_en.tzinfo is None:
        consultado_en = consultado_en.replace(tzinfo=timezone.utc)
    return Fuente(herramienta_croma=herramienta, url_oficial=url, consultado_en=consultado_en)
