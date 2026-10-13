"""Lectura de notificaciones y datos de poblacion."""

import csv

# Poblacion referencial por distrito (valores sinteticos para el prototipo).
POBLACION = {
    "AREQUIPA": 55400,
    "CAYMA": 98200,
    "CERRO COLORADO": 197900,
    "YANAHUARA": 26800,
    "PAUCARPATA": 131300,
    "MIRAFLORES": 60600,
    "MARIANO MELGAR": 59900,
    "SOCABAYA": 85400,
    "ALTO SELVA ALEGRE": 85900,
    "JOSE LUIS BUSTAMANTE Y RIVERO": 81200,
}

DISTRITOS = frozenset(POBLACION)


def leer_notificaciones(ruta):
    """Lee el archivo CSV de notificaciones y devuelve una lista de filas."""
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))
