"""Flujo principal: carga, validacion, almacenamiento, indicadores, alertas y reporte."""

import sys

from vigisalud import alertas, config, datos, indicadores, reportes, validacion
from vigisalud.repositorio import Repositorio


def ejecutar(ruta_csv, ruta_bd, ruta_reporte):
    """Ejecuta el procesamiento semanal completo y devuelve un resumen."""
    filas = datos.leer_notificaciones(ruta_csv)
    validas, rechazadas = validacion.validar_lote(filas)
    anio = config.ANIO_ACTUAL
    with Repositorio(ruta_bd) as repo:
        repo.guardar_notificaciones(validas)
        semana_actual = repo.ultima_semana(anio)
        conteos = repo.conteos_por_semana(semana_actual)
        totales = repo.totales_por_enfermedad(anio)
    tasas = indicadores.calcular_incidencia(validas, anio)
    canal = alertas.calcular_canal_endemico(conteos, semana_actual)
    lista_alertas = alertas.detectar_alertas(canal)
    reportes.generar_reporte_html(ruta_reporte, anio, totales, tasas, canal, lista_alertas)
    return {"leidas": len(filas), "validas": len(validas), "rechazadas": len(rechazadas),
            "alertas": len(lista_alertas),
            "letalidad": indicadores.calcular_letalidad(validas, anio),
            "edades": indicadores.distribuir_por_edad(validas, anio)}


if __name__ == "__main__":
    print(ejecutar(sys.argv[1], sys.argv[2], sys.argv[3]))
