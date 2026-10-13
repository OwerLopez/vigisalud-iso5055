"""Acceso a la base de datos de notificaciones (SQLite).

Es el unico modulo que ejecuta sentencias SQL. Usa una sola conexion por
procesamiento, consultas parametrizadas e indices para las agregaciones.
"""

import sqlite3
from collections import defaultdict

ESQUEMA = """
CREATE TABLE IF NOT EXISTS notificacion (
    id_caso TEXT PRIMARY KEY, fecha TEXT, anio INTEGER, semana INTEGER,
    distrito TEXT, establecimiento TEXT, enfermedad TEXT, edad INTEGER,
    sexo TEXT, condicion TEXT, tipo_dx TEXT);
CREATE INDEX IF NOT EXISTS ix_canal ON notificacion (distrito, enfermedad, semana, anio);
"""

INSERTAR = "INSERT INTO notificacion VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


class Repositorio:
    """Gestiona la conexion y las consultas sobre las notificaciones."""

    def __init__(self, ruta_bd):
        self.ruta_bd = ruta_bd
        self.conexion = None

    def __enter__(self):
        self.conexion = sqlite3.connect(self.ruta_bd)
        self.conexion.executescript(ESQUEMA)
        return self

    def __exit__(self, tipo, valor, traza):
        if tipo is None:
            self.conexion.commit()
        self.conexion.close()

    def guardar_notificaciones(self, notificaciones):
        """Guarda las notificaciones validadas en una sola operacion."""
        self.conexion.executemany(INSERTAR, (
            (n.id_caso, n.fecha.isoformat(), n.anio, n.semana, n.distrito, n.establecimiento,
             n.enfermedad, n.edad, n.sexo, n.condicion, n.tipo_dx) for n in notificaciones))

    def conteos_por_semana(self, semana_maxima):
        """Devuelve {(distrito, enfermedad, semana): {anio: casos}} en una sola consulta."""
        cursor = self.conexion.execute(
            "SELECT distrito, enfermedad, semana, anio, COUNT(*) FROM notificacion "
            "WHERE semana <= ? GROUP BY distrito, enfermedad, semana, anio", (semana_maxima,))
        conteos = defaultdict(dict)
        for distrito, enfermedad, semana, anio, casos in cursor:
            conteos[(distrito, enfermedad, semana)][anio] = casos
        return conteos

    def ultima_semana(self, anio):
        """Ultima semana epidemiologica con datos en el anio indicado."""
        fila = self.conexion.execute(
            "SELECT MAX(semana) FROM notificacion WHERE anio = ?", (anio,)).fetchone()
        return fila[0] or 0

    def totales_por_enfermedad(self, anio):
        """Total de casos del anio por enfermedad."""
        return dict(self.conexion.execute(
            "SELECT enfermedad, COUNT(*) FROM notificacion WHERE anio = ? GROUP BY enfermedad",
            (anio,)))
