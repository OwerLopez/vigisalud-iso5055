"""Indicadores epidemiologicos: incidencia, letalidad y grupos de edad."""

from vigisalud.datos import obtener_poblacion


def calcular_incidencia(notificaciones, anio):
    """Tasa de incidencia acumulada por 100 000 habitantes (distrito y enfermedad)."""
    casos = {}
    poblaciones = {}
    for n in notificaciones:
        if n.anio != anio:
            continue
        clave = n.distrito + "|" + n.enfermedad
        if clave not in casos:
            casos[clave] = 0
        casos[clave] = casos[clave] + 1
        poblaciones[clave] = obtener_poblacion(n.distrito)
    tasas = []
    for clave in casos:
        distrito, enfermedad = clave.split("|")
        tasa = casos[clave] / poblaciones[clave] * 100000
        tasas.append({"distrito": distrito, "enfermedad": enfermedad,
                      "casos": casos[clave], "tasa": round(tasa, 2)})
    return tasas


def calcular_letalidad(notificaciones, anio):
    """Porcentaje de fallecidos sobre el total de casos por enfermedad."""
    casos = {}
    fallecidos = {}
    for n in notificaciones:
        if n.anio != anio:
            continue
        casos[n.enfermedad] = casos.get(n.enfermedad, 0) + 1
        if n.condicion == "FALLECIDO":
            fallecidos[n.enfermedad] = fallecidos.get(n.enfermedad, 0) + 1
    letalidad = {}
    for enfermedad in casos:
        letalidad[enfermedad] = round(fallecidos.get(enfermedad, 0) / casos[enfermedad] * 100, 2)
    return letalidad


def distribuir_por_edad(notificaciones, anio):
    """Casos por grupo de edad segun la etapa de vida del MINSA."""
    grupos = {"NINO (0-11)": 0, "ADOLESCENTE (12-17)": 0, "JOVEN (18-29)": 0,
              "ADULTO (30-59)": 0, "ADULTO MAYOR (60+)": 0}
    for n in notificaciones:
        if n.anio != anio:
            continue
        if n.edad <= 11:
            grupos["NINO (0-11)"] += 1
        elif n.edad <= 17:
            grupos["ADOLESCENTE (12-17)"] += 1
        elif n.edad <= 29:
            grupos["JOVEN (18-29)"] += 1
        elif n.edad <= 59:
            grupos["ADULTO (30-59)"] += 1
        else:
            grupos["ADULTO MAYOR (60+)"] += 1
    return grupos
