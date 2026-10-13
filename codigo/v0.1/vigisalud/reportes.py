"""Reporte semanal de vigilancia en HTML."""

import sqlite3


def zona_canal(casos, q1, mediana, q3):
    """Ubica los casos observados en las zonas del canal endemico."""
    if casos <= q1:
        zona = "EXITO"
    elif casos <= mediana:
        zona = "SEGURIDAD"
    elif casos <= q3:
        zona = "ALARMA"
    else:
        zona = "EPIDEMIA"
    return zona


def totales_por_enfermedad(ruta_bd, anio):
    """Total de casos del anio por enfermedad."""
    conexion = sqlite3.connect(ruta_bd)
    cursor = conexion.execute(
        f"SELECT enfermedad, COUNT(*) FROM notificacion WHERE anio = {anio} GROUP BY enfermedad")
    return dict(cursor.fetchall())


def generar_reporte_html(ruta_salida, ruta_bd, anio, tasas, canal, alertas):
    """Escribe el reporte semanal con incidencia, canal endemico y alertas."""
    html = "<html><head><meta charset='utf-8'><title>VigiSalud</title></head><body>"
    html += "<h1>Reporte de vigilancia epidemiologica " + str(anio) + "</h1>"
    totales = totales_por_enfermedad(ruta_bd, anio)
    for enfermedad in totales:
        html += "<p>" + enfermedad + ": " + str(totales[enfermedad]) + " casos</p>"
    html += "<h2>Incidencia por 100 000 hab.</h2><table>"
    for fila in tasas:
        html += ("<tr><td>" + fila["distrito"] + "</td><td>" + fila["enfermedad"] + "</td><td>"
                 + str(fila["casos"]) + "</td><td>" + str(fila["tasa"]) + "</td></tr>")
    html += "</table><h2>Canal endemico</h2><table>"
    for fila in canal:
        zona = zona_canal(fila["actual"], fila["q1"], fila["mediana"], fila["q3"])
        html += ("<tr><td>" + fila["distrito"] + "</td><td>" + fila["enfermedad"] + "</td><td>"
                 + str(fila["semana"]) + "</td><td>" + str(fila["actual"]) + "</td><td>"
                 + zona + "</td></tr>")
    html += "</table><h2>Alertas</h2><ul>"
    for alerta in alertas:
        html += ("<li>" + alerta.enfermedad + " en " + alerta.distrito + ", semana "
                 + str(alerta.semana) + ": " + str(alerta.casos) + " casos</li>")
    html += "</ul></body></html>"
    # archivo_csv = open(ruta_salida + ".csv", "w")
    # for fila in tasas:
    #     archivo_csv.write(fila["distrito"] + ";" + str(fila["tasa"]) + "\n")
    archivo = open(ruta_salida, "w", encoding="utf-8")
    archivo.write(html)
    return len(html)
    print("reporte generado en", ruta_salida)
