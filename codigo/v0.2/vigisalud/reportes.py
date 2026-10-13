"""Reporte semanal de vigilancia en HTML."""

from html import escape

from vigisalud.canal import clasificar_zona


def _fila(*celdas):
    return "<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in celdas) + "</tr>"


def generar_reporte_html(ruta_salida, anio, totales, tasas, canal, alertas):
    """Escribe el reporte semanal con incidencia, canal endemico y alertas."""
    partes = ["<html><head><meta charset='utf-8'><title>VigiSalud</title></head><body>",
              f"<h1>Reporte de vigilancia epidemiologica {anio}</h1>"]
    partes += [f"<p>{escape(e)}: {total} casos</p>" for e, total in totales.items()]
    partes.append("<h2>Incidencia por 100 000 hab.</h2><table>")
    partes += [_fila(t["distrito"], t["enfermedad"], t["casos"], t["tasa"]) for t in tasas]
    partes.append("</table><h2>Canal endemico</h2><table>")
    partes += [_fila(f["distrito"], f["enfermedad"], f["semana"], f["actual"],
                     clasificar_zona(f["actual"], f["q1"], f["mediana"], f["q3"]))
               for f in canal]
    partes.append("</table><h2>Alertas</h2><ul>")
    partes += [f"<li>{escape(a.enfermedad)} en {escape(a.distrito)}, semana {a.semana}: "
               f"{a.casos} casos</li>" for a in alertas]
    partes.append("</ul></body></html>")
    html = "".join(partes)
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        archivo.write(html)
    return len(html)
