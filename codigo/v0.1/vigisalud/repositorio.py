"""Acceso a la base de datos de notificaciones (SQLite)."""

import sqlite3


def crear_tablas(ruta_bd):
    """Crea la tabla de notificaciones si no existe."""
    conexion = sqlite3.connect(ruta_bd)
    conexion.execute(
        "CREATE TABLE IF NOT EXISTS notificacion ("
        "id_caso TEXT PRIMARY KEY, fecha TEXT, anio INTEGER, semana INTEGER, "
        "distrito TEXT, establecimiento TEXT, enfermedad TEXT, edad INTEGER, "
        "sexo TEXT, condicion TEXT, tipo_dx TEXT)"
    )
    conexion.commit()


def guardar_notificaciones(ruta_bd, notificaciones):
    """Guarda las notificaciones validadas."""
    conexion = sqlite3.connect(ruta_bd)
    for n in notificaciones:
        conexion.execute(
            f"INSERT INTO notificacion VALUES ('{n.id_caso}', '{n.fecha}', {n.anio}, "
            f"{n.semana}, '{n.distrito}', '{n.establecimiento}', '{n.enfermedad}', "
            f"{n.edad}, '{n.sexo}', '{n.condicion}', '{n.tipo_dx}')"
        )
    conexion.commit()


def contar_casos_por_anio(ruta_bd, distrito, enfermedad, semana):
    """Devuelve {anio: casos} para un distrito, enfermedad y semana."""
    conexion = sqlite3.connect(ruta_bd)
    cursor = conexion.execute(
        f"SELECT anio, COUNT(*) FROM notificacion WHERE distrito = '{distrito}' "
        f"AND enfermedad = '{enfermedad}' AND semana = {semana} GROUP BY anio"
    )
    resultado = {}
    for anio, casos in cursor.fetchall():
        resultado[anio] = casos
    return resultado


def ultima_semana(ruta_bd, anio):
    """Ultima semana epidemiologica con datos en el anio indicado."""
    conexion = sqlite3.connect(ruta_bd)
    cursor = conexion.execute(f"SELECT MAX(semana) FROM notificacion WHERE anio = {anio}")
    return cursor.fetchone()[0]
