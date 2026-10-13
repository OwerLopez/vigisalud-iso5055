"""Flujo principal: carga, validacion, almacenamiento, indicadores, alertas y reporte."""

import sys

from vigisalud import alertas, config, datos, indicadores, reportes, repositorio, validacion


def ejecutar(ruta_csv, ruta_bd, ruta_reporte):
    """Ejecuta el procesamiento semanal completo y devuelve un resumen."""
    filas = datos.leer_notificaciones(ruta_csv)
    validas, rechazadas = validacion.validar_lote(filas)
    repositorio.crear_tablas(ruta_bd)
    repositorio.guardar_notificaciones(ruta_bd, validas)
    tasas = indicadores.calcular_incidencia(validas, config.ANIO_ACTUAL)
    letalidad = indicadores.calcular_letalidad(validas, config.ANIO_ACTUAL)
    edades = indicadores.distribuir_por_edad(validas, config.ANIO_ACTUAL)
    semana_actual = repositorio.ultima_semana(ruta_bd, config.ANIO_ACTUAL)
    canal = alertas.calcular_canal_endemico(ruta_bd, semana_actual)
    lista_alertas = alertas.detectar_alertas(canal)
    reportes.generar_reporte_html(ruta_reporte, ruta_bd, config.ANIO_ACTUAL, tasas, canal,
                                  lista_alertas)
    return {"leidas": len(filas), "validas": len(validas), "rechazadas": len(rechazadas),
            "alertas": len(lista_alertas), "letalidad": letalidad, "edades": edades}


if __name__ == "__main__":
    print(ejecutar(sys.argv[1], sys.argv[2], sys.argv[3]))
