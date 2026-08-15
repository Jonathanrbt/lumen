"""Vocabulario compartido de Lumen.

Estos modelos son el contrato entre las cuatro personas del equipo. Andrew construye
el frontend contra ellos, B1 los produce, B2 los enriquece y B3 los persiste.

Cambiar algo de aqui mueve el suelo de los cuatro a la vez: se anuncia en el chat
del equipo ANTES de pushear y se anota en el handoff propio. Anadir un campo
opcional es barato; renombrar o quitar uno, no.

Dos reglas del producto viven en los tipos, no en la documentacion, para que dejen
de depender de que alguien se acuerde:

1. `Senal` no se puede construir sin `fuente`. Si no hay fuente oficial con fecha,
   no hay senal.
2. `nivel_atencion` es un enum de tres valores. No es un numero, no es un
   porcentaje, no es un score. Si aparece un float ahi, alguien rompio el producto.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field

DISCLAIMER = (
    "Herramienta de priorización ciudadana. Una señal no es prueba de irregularidad."
)


class NivelAtencion(str, Enum):
    """Tres estados con color. Nunca un numero.

    El frontend los pinta como color, no como porcentaje. Que sea un enum y no un
    float es una decision de producto: un "78% de probabilidad de corrupcion" es
    exactamente lo que este proyecto se niega a publicar.
    """

    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class ModoCaso(str, Enum):
    """Por que puerta entro el caso. Mismo motor, distinto disparador."""

    EMERGENCIA = "emergencia"  # push: lo encontro el monitor
    VIGILANCIA = "vigilancia"  # pull: lo pidio una persona


class TipoActor(str, Enum):
    EMPRESA = "empresa"
    PERSONA = "persona"
    ENTIDAD = "entidad"


class CodigoSenal(str, Enum):
    """Las 8 senales del MVP.

    S9 (adiciones significativas) queda fuera: depende de que el dato de
    modificaciones este disponible y no vale el riesgo hoy. Va al roadmap.
    """

    S1 = "S1"  # empresa recien creada que gana
    S2 = "S2"  # representante legal compartido
    S3 = "S3"  # sancionado que sigue contratando
    S4 = "S4"  # contrato desproporcionado frente a su musculo financiero
    S5 = "S5"  # insolvente contratando
    S6 = "S6"  # fraccionamiento
    S7 = "S7"  # concentracion de valor en un proveedor
    S8 = "S8"  # contratacion directa recurrente
    S10 = "S10"  # deudor moroso del Estado contratando


class Veredicto(str, Enum):
    """Salida del lector de justificaciones de urgencia manifiesta."""

    SOLIDA = "solida"
    GENERICA = "generica"
    SIN_RELACION = "sin_relacion"


class TipoArtefacto(str, Enum):
    PAQUETE_EVIDENCIA = "paquete_evidencia"
    DERECHO_PETICION = "derecho_peticion"
    INFORME_VEEDURIA = "informe_veeduria"
    GUIA_DENUNCIA = "guia_denuncia"


class Fuente(BaseModel):
    """De donde salio el dato y cuando se consulto.

    Sin esto no publicamos nada. Es lo que hace que el jurado nos crea y lo que
    convierte una senal en algo que un ciudadano puede verificar por su cuenta.
    """

    herramienta_croma: str = Field(
        description="Herramienta de Croma que produjo el dato, ej. 'rues_entity_by_nit'"
    )
    url_oficial: str = Field(
        description="Enlace a la fuente oficial para que cualquiera lo verifique"
    )
    consultado_en: datetime = Field(
        description="Cuando se consulto. Los datos publicos cambian"
    )


class Candidato(BaseModel):
    """Lo que devuelve la resolucion de entidades para que el usuario desambigue.

    Nunca se asume cual es. Si hay tres empresas con nombre parecido, se muestran
    las tres y elige la persona.
    """

    nombre: str
    nit: str | None = None
    ciudad: str | None = None
    actividad: str | None = Field(
        default=None, description="Actividad economica, CIIU o descripcion"
    )
    tipo: TipoActor


class Senal(BaseModel):
    """Un patron que merece revision. No una acusacion.

    `fuente` es obligatoria a proposito: el guardarrail etico vive aqui, en el tipo,
    y no en la buena memoria de quien escribe el codigo a las tres de la manana.
    """

    codigo: CodigoSenal
    nombre: str = Field(description="Nombre corto y humano, ej. 'Empresa recién creada'")
    nivel: NivelAtencion
    regla_legible: str = Field(
        description=(
            "La regla contada como la entenderia un ciudadano, no la expresion. "
            "'La empresa se creó 41 días antes de ganar el contrato', no "
            "'fecha_adjudicacion - fecha_constitucion < 365'"
        )
    )
    datos_usados: dict = Field(
        default_factory=dict,
        description="Los valores concretos que dispararon la regla, para poder auditarla",
    )
    fuente: Fuente


class PuntoLectura(BaseModel):
    """Un punto del veredicto del lector, con la cita que lo sostiene.

    Si el modelo no puede citar el fragmento del documento, no afirma: llena
    `no_concluye_por` y deja `cita_textual` vacia. Eso es guardarrail, no
    preferencia.
    """

    pregunta: str = Field(
        description="Que se le preguntó al documento, ej. '¿menciona daños concretos y ubicados?'"
    )
    hallazgo: str
    cita_textual: str | None = None
    pagina: int | None = None
    no_concluye_por: str | None = Field(
        default=None,
        description="Por que no se pudo concluir. Se llena cuando no hay cita que respalde",
    )


class Lectura(BaseModel):
    """Veredicto del lector de justificaciones de urgencia manifiesta.

    La norma exige que la contratacion bajo urgencia manifiesta tenga relacion
    directa y verificable con los hechos de la emergencia. Esto evalua si la tiene.
    """

    veredicto: Veredicto
    puntos: list[PuntoLectura] = Field(default_factory=list)
    documento_url: str | None = None
    analizado_en: datetime | None = None


class Actor(BaseModel):
    """Nodo del grafo: quien esta detras de quien."""

    id: str
    tipo: TipoActor
    nombre: str
    nit: str | None = None
    rol: str | None = Field(
        default=None, description="Su papel en este caso: contratante, proveedor, representante legal"
    )


class Arista(BaseModel):
    origen: str = Field(description="id del Actor de origen")
    destino: str = Field(description="id del Actor de destino")
    tipo: str = Field(description="Naturaleza del vinculo, ej. 'representante_legal_de'")
    fuente: Fuente


class Grafo(BaseModel):
    """Subgrafo curado de actores. Entre 5 y 12 nodos.

    El limite no esta forzado en el tipo porque romper a las dos de la manana por
    tener 13 nodos seria absurdo, pero es una regla de producto: un hairball es
    peor que no mostrar grafo.
    """

    nodos: list[Actor] = Field(default_factory=list)
    aristas: list[Arista] = Field(default_factory=list)


class Caso(BaseModel):
    """El objeto central. Todo el producto gira alrededor de esto.

    Lo produce el mismo motor venga del push (monitor) o del pull (una persona
    preguntando). Si alguien empieza a escribir un segundo motor, se salio del plan.
    """

    id: str
    modo: ModoCaso
    entidad: str = Field(description="Entidad publica contratante")
    proveedor: str | None = None
    municipio: str | None = None
    departamento: str | None = None
    valor: float | None = Field(default=None, description="Valor del contrato en pesos")
    objeto: str | None = Field(default=None, description="Objeto contractual")
    fecha: date | None = None
    nivel_atencion: NivelAtencion
    senales: list[Senal] = Field(default_factory=list)
    lectura: Lectura | None = None
    grafo: Grafo | None = None
    narracion: str | None = Field(
        default=None, description="El hallazgo contado en lenguaje ciudadano"
    )
    disclaimer: str = DISCLAIMER
    generado_en: datetime | None = None


class Artefacto(BaseModel):
    """La capa de accion: que hago yo, ciudadano, con esto.

    Es la brecha que nadie mas cubre. Sin esto, una alerta es solo una alerta.
    """

    tipo: TipoArtefacto
    titulo: str
    cuerpo_markdown: str
    normas_citadas: list[str] = Field(default_factory=list)
    destinatario: str | None = Field(
        default=None, description="Entidad a la que va dirigido, con su nombre oficial"
    )
    caso_id: str | None = None
