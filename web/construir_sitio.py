"""Construye el dashboard estatico bilingue (site/index.html) a partir de las mediciones.

Uso: python web/construir_sitio.py
"""

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "medicion"))
import exportar_dashboard as ex  # noqa: E402
import graficos as gr  # noqa: E402

REPO = "https://github.com/OwerLopez/vigisalud-iso5055"
GRUPO = {"Calidad": "quality", "Eficiencia": "efficiency", "Proceso de revisión": "review"}
ESTADO = {"VERDE": "good", "AMBAR": "warning", "ROJO": "critical", "SIN DATO": "na"}
MEDIDAS = {"ASCMM": ("Maintainability", "Mantenibilidad"), "ASCPEM": ("Performance efficiency", "Eficiencia de desempeño"),
           "ASCRM": ("Reliability", "Fiabilidad"), "ASCSM": ("Security", "Seguridad")}


def funcion(nombre):
    """Nombre legible de una entrada de cProfile."""
    m = re.match(r"~:0\(<(?:built-in )?method '?(\w+)'?(?: of '[\w.]+' objects)?>\)", nombre)
    if m:
        return f"sqlite3.{m.group(1)}" if m.group(1) in ("execute", "executemany", "executescript", "connect") \
            else m.group(1)
    m = re.match(r"~:0\(<built-in method ([\w.]+)>\)", nombre)
    if m:
        return m.group(1)
    return nombre


def main():
    d = json.loads((RAIZ / "resultados" / "indicadores.json").read_text(encoding="utf-8"))
    datos = {
        "indicators": [{
            "code": i["codigo"], "group": GRUPO[i["grupo"]],
            "name": {"en": ex.NOMBRES[i["codigo"]], "es": i["nombre"]},
            "unit": {"en": ex.UNIDADES[i["unidad"]], "es": "" if i["unidad"] == "adimensional" else i["unidad"]},
            "better": "lower" if i["sentido"].startswith("menor") else "higher",
            "green": i["verde"], "amber": i["ambar"], "v01": i["v0.1"], "v02": i["v0.2"],
            "s_v01": ESTADO[i["semaforo_v0.1"]], "s_v02": ESTADO[i["semaforo_v0.2"]],
        } for i in d["indicadores"]],
        "measures": [{"key": k, "name": {"en": MEDIDAS[k][0], "es": MEDIDAS[k][1]}, "total": c["total_cwe"],
                      "covered": c["cubiertos"], "v01": d["conteos_5055"]["v0.1"][k], "v02": d["conteos_5055"]["v0.2"][k]}
                     for k, c in d["cobertura_5055"].items()],
        "cwe": [{"cwe": h["cwe"], "n": h["ocurrencias"], "measures": h["medidas"],
                 "name": {"en": gr.NOMBRES_CWE_EN[h["cwe"]], "es": gr.NOMBRES_CWE_ES[h["cwe"]]}}
                for h in d["hallazgos_por_cwe_v0.1"]],
        "issues": [{"id": f"F-{n:02d}", "module": h["modulo"].replace("vigisalud.", ""), "line": h["linea"],
                    "cwe": h["cwe"], "measures": h["medidas"], "tool": h["herramienta"], "rule": h["regla"],
                    "name": {"en": gr.NOMBRES_CWE_EN[h["cwe"]], "es": gr.NOMBRES_CWE_ES[h["cwe"]]}}
                   for n, h in enumerate(d["issue_log_v0.1"], start=1)],
        "curves": {v.replace(".", ""): [{"n": p["n"], "t": p["mediana_s"]} for p in curva]
                   for v, curva in d["curvas"].items()},
        "hotspots": {v.replace(".", ""): [{"fn": funcion(h["funcion"]), "pct": h["porcentaje"]} for h in lista]
                     for v, lista in d["hotspots"].items()},
        "locked": {v.replace(".", ""): x for v, x in d["bd_bloqueada"].items()},
    }
    html = (RAIZ / "web" / "plantilla.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", json.dumps(datos, ensure_ascii=False)).replace("__REPO__", REPO)
    salida = RAIZ / "site" / "index.html"
    salida.parent.mkdir(exist_ok=True)
    salida.write_text(html, encoding="utf-8")
    print(salida, len(html), [h["fn"] for h in datos["hotspots"]["v01"]])


if __name__ == "__main__":
    main()
