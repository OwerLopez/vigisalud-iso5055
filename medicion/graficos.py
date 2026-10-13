"""Genera los graficos del informe (ES) y de las diapositivas (EN) con QuickChart.

Uso: python medicion/graficos.py
Envia solo cifras agregadas de la medicion (sin datos personales) a quickchart.io,
guarda una copia PNG en docs/graficos/ y las URL publicas en resultados/graficos.json
(Google Docs y Slides necesitan una URL publica para insertar imagenes).
"""

import json
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GUINDA, VERDE_AZUL, GRIS = "#7A1F2B", "#2E7D74", "#6B7280"

TEXTOS = {
    "es": {"v01": "v0.1 (línea base)", "v02": "v0.2 (tras la revisión)",
           "medidas": ["Mantenibilidad", "Eficiencia", "Fiabilidad", "Seguridad"],
           "ocurrencias": "Ocurrencias de debilidades CWE", "n": "Notificaciones procesadas (N)",
           "t": "Tiempo (s, escala log)", "cwe": "Ocurrencias en v0.1"},
    "en": {"v01": "v0.1 (baseline)", "v02": "v0.2 (after review)",
           "medidas": ["Maintainability", "Perf. efficiency", "Reliability", "Security"],
           "ocurrencias": "CWE weakness occurrences", "n": "Notifications processed (N)",
           "t": "Time (s, log scale)", "cwe": "Occurrences in v0.1"},
}
NOMBRES_CWE_EN = {
    772: "Resource not released", 1072: "No connection reuse", 89: "SQL injection",
    1046: "String concat in loop", 390: "Error without action", 703: "Exception handling",
    775: "File handle not released", 1067: "Sequential searches", 369: "Divide by zero",
    1060: "Queries inside loop", 1088: "Remote call w/o timeout", 1051: "Hard-coded network",
    798: "Hard-coded credentials", 1041: "Copy-paste code", 1057: "SQL outside data layer",
    1085: "Commented-out code", 561: "Dead code", 1050: "Resource use in loop",
    1064: "Too many parameters", 1121: "High McCabe complexity",
}
NOMBRES_CWE_ES = {
    772: "Recurso no liberado", 1072: "Sin reutilizar conexiones", 89: "Inyección SQL",
    1046: "Concatenación en bucle", 390: "Error sin acción", 703: "Manejo de excepciones",
    775: "Archivo no cerrado", 1067: "Búsquedas secuenciales", 369: "División por cero",
    1060: "Consultas en bucle", 1088: "Red sin timeout", 1051: "Red codificada",
    798: "Credencial codificada", 1041: "Código duplicado", 1057: "SQL fuera del repositorio",
    1085: "Código comentado", 561: "Código muerto", 1050: "Recurso en bucle",
    1064: "Exceso de parámetros", 1121: "Complejidad excesiva",
}


def _barras_medidas(d, t):
    conteos = d["conteos_5055"]
    claves = ["ASCMM", "ASCPEM", "ASCRM", "ASCSM"]
    return {"type": "bar", "data": {"labels": t["medidas"], "datasets": [
        {"label": t["v01"], "data": [conteos["v0.1"][k] for k in claves], "backgroundColor": GUINDA},
        {"label": t["v02"], "data": [conteos["v0.2"][k] for k in claves], "backgroundColor": VERDE_AZUL}]},
        "options": {"layout": {"padding": {"top": 24}}, "plugins": {"legend": {"position": "bottom"},
                                "datalabels": {"anchor": "end", "align": "end", "color": "#222"}},
                    "scales": {"y": {"beginAtZero": True, "title": {"display": True, "text": t["ocurrencias"]}}}}}


def _barras_cwe(d, nombres, t):
    filas = d["hallazgos_por_cwe_v0.1"]
    return {"type": "bar", "data": {
        "labels": [f"CWE-{f['cwe']} {nombres.get(f['cwe'], '')}" for f in filas],
        "datasets": [{"label": t["cwe"], "data": [f["ocurrencias"] for f in filas],
                      "backgroundColor": GUINDA}]},
        "options": {"indexAxis": "y", "layout": {"padding": {"right": 36}}, "plugins": {"legend": {"display": False},
                    "datalabels": {"anchor": "end", "align": "end", "color": "#222"}},
                    "scales": {"x": {"beginAtZero": True}}}}


def _curva(d, t):
    series = []
    for v, color, clave in (("v0.1", GUINDA, "v01"), ("v0.2", VERDE_AZUL, "v02")):
        series.append({"label": t[clave], "borderColor": color, "backgroundColor": color,
                       "fill": False, "tension": 0,
                       "data": [{"x": p["n"], "y": p["mediana_s"]} for p in d["curvas"][v]]})
    return {"type": "line", "data": {"datasets": series},
            "options": {"plugins": {"legend": {"position": "bottom"}, "datalabels": {"display": False}},
                        "scales": {"x": {"type": "logarithmic", "title": {"display": True, "text": t["n"]}},
                                   "y": {"type": "logarithmic", "title": {"display": True, "text": t["t"]}}}}}


def _crear(config, ancho, alto):
    cuerpo = json.dumps({"chart": config, "width": ancho, "height": alto, "backgroundColor": "white",
                         "format": "png", "version": "4", "devicePixelRatio": 2}).encode()
    peticion = urllib.request.Request("https://quickchart.io/chart/create", data=cuerpo,
                                      headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        return json.load(respuesta)["url"]


def main():
    d = json.loads((RAIZ / "resultados" / "indicadores.json").read_text(encoding="utf-8"))
    carpeta = RAIZ / "docs" / "graficos"
    carpeta.mkdir(parents=True, exist_ok=True)
    urls = {}
    for idioma, nombres in (("es", NOMBRES_CWE_ES), ("en", NOMBRES_CWE_EN)):
        t = TEXTOS[idioma]
        for nombre, config, ancho, alto in (
                ("medidas", _barras_medidas(d, t), 800, 420),
                ("cwe", _barras_cwe(d, nombres, t), 800, 560),
                ("escalabilidad", _curva(d, t), 800, 420)):
            url = _crear(config, ancho, alto)
            urls[f"{nombre}_{idioma}"] = url
            with urllib.request.urlopen(url, timeout=30) as r:
                (carpeta / f"{nombre}_{idioma}.png").write_bytes(r.read())
    (RAIZ / "resultados" / "graficos.json").write_text(json.dumps(urls, indent=2), encoding="utf-8")
    print(json.dumps(urls, indent=1))


if __name__ == "__main__":
    main()
