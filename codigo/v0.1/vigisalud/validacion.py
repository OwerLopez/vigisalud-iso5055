"""Validacion de las notificaciones recibidas de los establecimientos."""

from datetime import date

from vigisalud import config
from vigisalud.datos import listar_distritos
from vigisalud.modelos import Notificacion


def crear_notificacion(id_caso, fecha, anio, semana, distrito, establecimiento,
                       enfermedad, edad, sexo, condicion, tipo_dx):
    """Construye una notificacion a partir de sus campos."""
    return Notificacion(id_caso, fecha, anio, semana, distrito, establecimiento,
                        enfermedad, edad, sexo, condicion, tipo_dx)


def validar_notificacion(fila, distritos):
    """Valida una fila del CSV y devuelve (notificacion, errores)."""
    errores = []
    if fila["id_caso"] == "":
        errores.append("id_caso vacio")
    if fila["enfermedad"] not in config.ENFERMEDADES:
        errores.append("enfermedad no vigilada")
    if fila["distrito"] not in distritos:
        errores.append("distrito fuera de jurisdiccion")
    if fila["sexo"] not in config.SEXOS:
        errores.append("sexo invalido")
    if fila["condicion"] not in config.CONDICIONES:
        errores.append("condicion invalida")
    if fila["tipo_dx"] not in config.TIPOS_DX:
        errores.append("tipo de diagnostico invalido")
    edad = -1
    try:
        edad = int(fila["edad"])
    except:
        pass
    if edad < 0 or edad > 110:
        errores.append("edad fuera de rango")
    semana = 0
    try:
        semana = int(fila["semana"])
    except:
        pass
    if semana < 1 or semana > 53:
        errores.append("semana epidemiologica invalida")
    anio = 0
    try:
        anio = int(fila["anio"])
    except:
        pass
    if anio < 2000 or anio > config.ANIO_ACTUAL:
        errores.append("anio invalido")
    fecha = None
    try:
        fecha = date.fromisoformat(fila["fecha"])
    except:
        pass
    if fecha is None:
        errores.append("fecha invalida")
    elif fecha.year != anio:
        errores.append("fecha no coincide con el anio")
    if fila["establecimiento"] == "":
        errores.append("establecimiento vacio")
    if len(errores) > 0:
        return None, errores
    notificacion = crear_notificacion(fila["id_caso"], fecha, anio, semana,
                                      fila["distrito"], fila["establecimiento"],
                                      fila["enfermedad"], edad, fila["sexo"],
                                      fila["condicion"], fila["tipo_dx"])
    return notificacion, errores


def validar_lote(filas):
    """Valida un lote completo y descarta duplicados."""
    distritos = listar_distritos()
    validas = []
    rechazadas = []
    ids_vistos = []
    for fila in filas:
        if fila["id_caso"] in ids_vistos:
            rechazadas.append((fila, ["caso duplicado"]))
            continue
        ids_vistos.append(fila["id_caso"])
        notificacion, errores = validar_notificacion(fila, distritos)
        if notificacion is None:
            rechazadas.append((fila, errores))
        else:
            validas.append(notificacion)
    return validas, rechazadas
