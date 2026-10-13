"""Validacion de las notificaciones recibidas de los establecimientos."""

from datetime import date

from vigisalud import config
from vigisalud.datos import DISTRITOS
from vigisalud.modelos import Notificacion

REGLAS_CATALOGO = (
    ("enfermedad", config.ENFERMEDADES, "enfermedad no vigilada"),
    ("distrito", DISTRITOS, "distrito fuera de jurisdiccion"),
    ("sexo", config.SEXOS, "sexo invalido"),
    ("condicion", config.CONDICIONES, "condicion invalida"),
    ("tipo_dx", config.TIPOS_DX, "tipo de diagnostico invalido"),
)

RANGOS = (
    ("edad", 0, 110, "edad fuera de rango"),
    ("semana", 1, 53, "semana epidemiologica invalida"),
    ("anio", 2000, config.ANIO_ACTUAL, "anio invalido"),
)


def _entero(valor):
    """Convierte a entero; devuelve None si el valor no es numerico."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _fecha(valor):
    """Convierte una fecha ISO; devuelve None si no es valida."""
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        return None


def _errores_de_catalogo(fila):
    return [mensaje for campo, valores, mensaje in REGLAS_CATALOGO if fila[campo] not in valores]


def _errores_de_rango(fila, numeros):
    errores = []
    for campo, minimo, maximo, mensaje in RANGOS:
        valor = numeros[campo]
        if valor is None or not minimo <= valor <= maximo:
            errores.append(mensaje)
    return errores


def validar_notificacion(fila):
    """Valida una fila del CSV y devuelve (notificacion, errores)."""
    numeros = {campo: _entero(fila[campo]) for campo, *_ in RANGOS}
    fecha = _fecha(fila["fecha"])
    errores = _errores_de_catalogo(fila) + _errores_de_rango(fila, numeros)
    if not fila["id_caso"] or not fila["establecimiento"]:
        errores.append("campo obligatorio vacio")
    if fecha is None or fecha.year != numeros["anio"]:
        errores.append("fecha invalida o no coincide con el anio")
    if errores:
        return None, errores
    campos = dict(fila, fecha=fecha, **numeros)
    return Notificacion(**campos), errores


def validar_lote(filas):
    """Valida un lote completo y descarta duplicados."""
    validas, rechazadas, ids_vistos = [], [], set()
    for fila in filas:
        if fila["id_caso"] in ids_vistos:
            rechazadas.append((fila, ["caso duplicado"]))
            continue
        ids_vistos.add(fila["id_caso"])
        notificacion, errores = validar_notificacion(fila)
        if notificacion is None:
            rechazadas.append((fila, errores))
        else:
            validas.append(notificacion)
    return validas, rechazadas
