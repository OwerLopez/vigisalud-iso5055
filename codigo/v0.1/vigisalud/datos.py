"""Lectura de notificaciones y datos de poblacion."""

import csv

# Poblacion referencial por distrito (valores sinteticos para el prototipo).
POBLACION = [
    {"distrito": "AREQUIPA", "poblacion": 55400},
    {"distrito": "CAYMA", "poblacion": 98200},
    {"distrito": "CERRO COLORADO", "poblacion": 197900},
    {"distrito": "YANAHUARA", "poblacion": 26800},
    {"distrito": "PAUCARPATA", "poblacion": 131300},
    {"distrito": "MIRAFLORES", "poblacion": 60600},
    {"distrito": "MARIANO MELGAR", "poblacion": 59900},
    {"distrito": "SOCABAYA", "poblacion": 85400},
    {"distrito": "ALTO SELVA ALEGRE", "poblacion": 85900},
    {"distrito": "JOSE LUIS BUSTAMANTE Y RIVERO", "poblacion": 81200},
]


def leer_notificaciones(ruta):
    """Lee el archivo CSV de notificaciones y devuelve una lista de filas."""
    archivo = open(ruta, encoding="utf-8")
    lector = csv.DictReader(archivo)
    filas = []
    for fila in lector:
        filas.append(fila)
    return filas


def obtener_poblacion(distrito):
    """Busca la poblacion de un distrito."""
    for registro in POBLACION:
        if registro["distrito"] == distrito:
            return registro["poblacion"]
    return 0


def listar_distritos():
    """Devuelve los nombres de los distritos vigilados."""
    distritos = []
    for registro in POBLACION:
        distritos.append(registro["distrito"])
    return distritos
