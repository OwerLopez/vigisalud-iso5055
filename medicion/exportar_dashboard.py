"""Exporta resultados/indicadores.json a datasets en ingles para el dashboard web.

Uso: python medicion/exportar_dashboard.py
Genera resultados/dashboard/*.json (filas planas, una por registro).
"""

import json
from pathlib import Path

RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"
DESTINO = RESULTADOS / "dashboard"

NOMBRES = {
    "IC-01": "Maintainability weakness density", "IC-02": "Reliability weakness density",
    "IC-03": "Security weakness density", "IC-04": "Functions with excessive complexity",
    "IC-05": "Maintainability index", "IC-06": "Duplicated code",
    "IE-01": "Performance-efficiency weakness density", "IE-02": "Weekly processing time",
    "IE-03": "Throughput", "IE-04": "Peak memory", "IE-05": "Scalability exponent",
    "IE-06": "Cost concentration (hotspot)", "IR-01": "Finding resolution rate",
}
UNIDADES = {
    "debilidades/KSLOC": "weaknesses/KSLOC", "%": "%", "puntos (0-100)": "points (0-100)",
    "segundos": "s", "notificaciones/s": "notifications/s", "MB": "MB", "adimensional": "",
}
GRUPOS = {"Calidad": "Code quality", "Eficiencia": "Efficiency", "Proceso de revisión": "Review process"}
ESTADOS = {"VERDE": "green", "AMBAR": "amber", "ROJO": "red", "SIN DATO": "n/a"}
MEDIDAS = {"ASCMM": "Maintainability", "ASCPEM": "Performance efficiency",
           "ASCRM": "Reliability", "ASCSM": "Security"}
DEBILIDADES = {
    561: "Dead code", 570: "Expression always false", 1041: "Redundant (copy-paste) code",
    1047: "Circular module dependencies", 1051: "Hard-coded network configuration",
    1064: "Too many parameters", 1085: "Commented-out code", 1121: "Excessive McCabe complexity",
    369: "Divide by zero", 390: "Error detected without action",
    703: "Improper handling of exceptional conditions", 1088: "Remote access without timeout",
    89: "SQL injection", 798: "Hard-coded credentials", 772: "Resource not released",
    775: "File handle not released", 1046: "String concatenation in a loop",
    1050: "Resource consumption inside a loop", 1057: "Data access outside the data manager",
    1060: "Excessive server-side data accesses", 1067: "Excessive sequential searches",
    1072: "No connection reuse (pooling)",
}


def _escribir(nombre, filas):
    (DESTINO / f"{nombre}.json").write_text(json.dumps(filas, indent=1, ensure_ascii=False),
                                            encoding="utf-8")


def main():
    datos = json.loads((RESULTADOS / "indicadores.json").read_text(encoding="utf-8"))
    DESTINO.mkdir(exist_ok=True)

    _escribir("indicators", [{
        "code": i["codigo"], "group": GRUPOS[i["grupo"]], "indicator": NOMBRES[i["codigo"]],
        "unit": UNIDADES[i["unidad"]], "better": "lower" if i["sentido"].startswith("menor") else "higher",
        "green_limit": i["verde"], "amber_limit": i["ambar"],
        "v01": i["v0.1"], "v02": i["v0.2"],
        "status_v01": ESTADOS[i["semaforo_v0.1"]], "status_v02": ESTADOS[i["semaforo_v0.2"]],
    } for i in datos["indicadores"]])

    _escribir("measures", [{
        "measure": clave, "characteristic": MEDIDAS[clave],
        "cwe_in_standard": c["total_cwe"], "cwe_covered": c["cubiertos"],
        "occurrences_v01": datos["conteos_5055"]["v0.1"][clave],
        "occurrences_v02": datos["conteos_5055"]["v0.2"][clave],
    } for clave, c in datos["cobertura_5055"].items()])

    _escribir("issues", [{
        "id": f"F-{n:02d}", "module": h["modulo"].replace("vigisalud.", ""), "line": h["linea"],
        "cwe": f"CWE-{h['cwe']}", "weakness": DEBILIDADES.get(h["cwe"], f"CWE-{h['cwe']}"),
        "measures": " ".join(h["medidas"]), "tool": h["herramienta"], "rule": h["regla"],
        "status": "Fixed in v0.2",
    } for n, h in enumerate(datos["issue_log_v0.1"], start=1)])

    _escribir("scaling", [{"version": v, "n": p["n"], "median_s": p["mediana_s"]}
                          for v, curva in datos["curvas"].items() for p in curva])

    _escribir("hotspots", [{"version": v, "rank": r, "function": h["funcion"],
                            "share_pct": h["porcentaje"]}
                           for v, lista in datos["hotspots"].items()
                           for r, h in enumerate(lista, start=1)])

    _escribir("versions", [{
        "version": v, "sloc": t["sloc"], "functions": t["funciones"], "modules": t["modulos"],
        "weaknesses": len(datos["issue_log_v0.1"]) if v == "v0.1" else 0,
        "db_locked_runs": datos["bd_bloqueada"][v],
    } for v, t in datos["tamano"].items()])
    print(sorted(p.name for p in DESTINO.iterdir()))


if __name__ == "__main__":
    main()
