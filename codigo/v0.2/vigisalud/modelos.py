"""Entidades del dominio de vigilancia epidemiologica."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Notificacion:
    """Caso notificado por un establecimiento de salud."""

    id_caso: str
    fecha: date
    anio: int
    semana: int
    distrito: str
    establecimiento: str
    enfermedad: str
    edad: int
    sexo: str
    condicion: str
    tipo_dx: str


@dataclass
class Alerta:
    """Alerta generada por el canal endemico."""

    distrito: str
    enfermedad: str
    semana: int
    casos: int
    limite_superior: float
    zona: str
