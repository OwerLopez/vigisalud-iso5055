"""Genera notificaciones sinteticas reproducibles para medir la eficiencia.

Los datos son ficticios: no contienen informacion de pacientes reales.
Incluyen estacionalidad por enfermedad, un brote simulado de dengue en 2026,
un 2 % de filas con errores y un 1 % de duplicados para ejercitar la validacion.
"""

import csv
import random
import sys
from datetime import date, timedelta

DISTRITOS = ["AREQUIPA", "CAYMA", "CERRO COLORADO", "YANAHUARA", "PAUCARPATA", "MIRAFLORES",
             "MARIANO MELGAR", "SOCABAYA", "ALTO SELVA ALEGRE", "JOSE LUIS BUSTAMANTE Y RIVERO"]
ESTACIONALIDAD = {"DENGUE": (6, 16), "IRA": (20, 32), "EDA": (1, 10)}
ANIOS = [2021, 2022, 2023, 2024, 2025, 2026]
SEMANAS_2026 = 26
CAMPOS = ["id_caso", "fecha", "anio", "semana", "distrito", "establecimiento", "enfermedad",
          "edad", "sexo", "condicion", "tipo_dx"]


def _semana(rng, enfermedad, max_semana):
    inicio, fin = ESTACIONALIDAD[enfermedad]
    if rng.random() < 0.6:
        return min(rng.randint(inicio, fin), max_semana)
    return rng.randint(1, max_semana)


def _fecha(anio, semana, rng):
    base = date(anio, 1, 1) + timedelta(days=(semana - 1) * 7 + rng.randint(0, 6))
    return base if base.year == anio else date(anio, 12, 31)


def generar(n_registros, semilla=2026):
    """Devuelve una lista de filas (dict) con n_registros notificaciones."""
    rng = random.Random(semilla)
    filas = []
    for i in range(n_registros):
        anio = rng.choices(ANIOS, weights=[2, 2, 2, 2, 2, 1])[0]
        enfermedad = rng.choice(list(ESTACIONALIDAD))
        max_semana = SEMANAS_2026 if anio == 2026 else 52
        semana = _semana(rng, enfermedad, max_semana)
        distrito = rng.choice(DISTRITOS)
        if anio == 2026 and enfermedad == "DENGUE" and rng.random() < 0.08:
            distrito, semana = "CERRO COLORADO", rng.randint(10, 14)
        fila = {
            "id_caso": f"N{i:07d}",
            "fecha": _fecha(anio, semana, rng).isoformat(),
            "anio": anio, "semana": semana, "distrito": distrito,
            "establecimiento": f"EESS-{rng.randint(1, 40):03d}",
            "enfermedad": enfermedad, "edad": rng.randint(0, 95),
            "sexo": rng.choice("MF"),
            "condicion": "FALLECIDO" if rng.random() < 0.012 else "VIVO",
            "tipo_dx": rng.choice(["CONFIRMADO", "PROBABLE"]),
        }
        if rng.random() < 0.02:
            fila["edad"] = "sin dato"
        filas.append(fila)
    duplicados = [dict(rng.choice(filas)) for _ in range(n_registros // 100)]
    return filas + duplicados


def escribir_csv(ruta, filas):
    """Guarda las filas en un CSV UTF-8."""
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(filas)


if __name__ == "__main__":
    escribir_csv(sys.argv[1], generar(int(sys.argv[2])))
