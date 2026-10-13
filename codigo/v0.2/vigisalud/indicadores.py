"""Indicadores epidemiologicos: incidencia, letalidad y grupos de edad."""

from bisect import bisect_left
from collections import Counter

from vigisalud.datos import POBLACION

POR_100_MIL = 100_000
LIMITES_EDAD = (11, 17, 29, 59)
GRUPOS_EDAD = ("NINO (0-11)", "ADOLESCENTE (12-17)", "JOVEN (18-29)", "ADULTO (30-59)",
               "ADULTO MAYOR (60+)")


def _del_anio(notificaciones, anio):
    return [n for n in notificaciones if n.anio == anio]


def calcular_incidencia(notificaciones, anio):
    """Tasa de incidencia acumulada por 100 000 habitantes (distrito y enfermedad)."""
    casos = Counter((n.distrito, n.enfermedad) for n in _del_anio(notificaciones, anio))
    tasas = []
    for (distrito, enfermedad), total in casos.items():
        poblacion = POBLACION.get(distrito, 0)
        tasa = total / poblacion * POR_100_MIL if poblacion > 0 else 0.0
        tasas.append({"distrito": distrito, "enfermedad": enfermedad,
                      "casos": total, "tasa": round(tasa, 2)})
    return tasas


def calcular_letalidad(notificaciones, anio):
    """Porcentaje de fallecidos sobre el total de casos por enfermedad."""
    del_anio = _del_anio(notificaciones, anio)
    casos = Counter(n.enfermedad for n in del_anio)
    fallecidos = Counter(n.enfermedad for n in del_anio if n.condicion == "FALLECIDO")
    return {enfermedad: round(fallecidos[enfermedad] / total * 100, 2)
            for enfermedad, total in casos.items() if total > 0}


def distribuir_por_edad(notificaciones, anio):
    """Casos por grupo de edad segun la etapa de vida del MINSA."""
    conteo = Counter(GRUPOS_EDAD[bisect_left(LIMITES_EDAD, n.edad)]
                     for n in _del_anio(notificaciones, anio))
    return {grupo: conteo[grupo] for grupo in GRUPOS_EDAD}
