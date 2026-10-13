"""Consolida las mediciones en resultados/indicadores.json (fuente del dashboard).

Uso: python medicion/consolidar.py
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fichas  # noqa: E402
import iso5055  # noqa: E402

RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"
VERSIONES = ("v0.1", "v0.2")

# CWE que la cadena de herramientas puede detectar (Pylint + Bandit + Radon + detectores AST).
CUBIERTOS = {369, 390, 561, 570, 703, 772, 775, 798, 1041, 1046, 1047, 1050, 1051, 1057,
             1060, 1064, 1067, 1072, 1074, 1080, 1085, 1088, 1121, 22, 78, 89, 259, 502, 732}


def _cargar(nombre):
    return json.loads((RESULTADOS / nombre).read_text(encoding="utf-8"))


def _valores(calidad, eficiencia):
    densidades = calidad["densidades_5055"]
    return {
        "IC-01": densidades["ASCMM"], "IC-02": densidades["ASCRM"], "IC-03": densidades["ASCSM"],
        "IC-04": calidad["complejidad"]["porcentaje_sobre_limite"],
        "IC-05": calidad["mantenibilidad_mi"]["promedio_ponderado"],
        "IC-06": calidad["duplicacion"]["porcentaje"],
        "IE-01": densidades["ASCPEM"], "IE-02": eficiencia["tiempo_s"],
        "IE-03": eficiencia["throughput"], "IE-04": eficiencia["memoria_pico_mb"],
        "IE-05": eficiencia["exponente_escalabilidad"], "IE-06": eficiencia["hotspot_pct"],
    }


def _resolucion(antes, despues):
    """IR-01: ocurrencias por (modulo, CWE) que desaparecen en la nueva version."""
    previos = Counter((h["modulo"], h["cwe"]) for h in antes["hallazgos"])
    actuales = Counter((h["modulo"], h["cwe"]) for h in despues["hallazgos"])
    resueltos = sum(max(0, n - actuales[clave]) for clave, n in previos.items())
    total = sum(previos.values())
    return round(resueltos / total * 100, 1) if total else None, resueltos, total


def main():
    calidad = {v: _cargar(f"calidad_{v}.json") for v in VERSIONES}
    eficiencia = {v: _cargar(f"eficiencia_{v}.json") for v in VERSIONES}
    if eficiencia["v0.1"]["resumen_funcional"] != eficiencia["v0.2"]["resumen_funcional"]:
        raise SystemExit("Las versiones no producen el mismo resultado funcional")

    valores = {v: _valores(calidad[v], eficiencia[v]) for v in VERSIONES}
    tasa, resueltos, identificados = _resolucion(calidad["v0.1"], calidad["v0.2"])
    valores["v0.2"]["IR-01"] = tasa
    valores["v0.1"]["IR-01"] = None

    indicadores = []
    for ficha in fichas.FICHAS:
        fila = dict(ficha)
        for v in VERSIONES:
            fila[v] = valores[v].get(ficha["codigo"])
            fila[f"semaforo_{v}"] = fichas.semaforo(ficha, fila[v])
        indicadores.append(fila)

    cobertura = {clave: {"medida": nombre, "total_cwe": len(conjunto),
                         "cubiertos": len(conjunto & CUBIERTOS)}
                 for clave, (nombre, conjunto) in iso5055.MEDIDAS.items()}
    por_cwe = Counter(h["cwe"] for h in calidad["v0.1"]["hallazgos"])

    salida = {
        "proyecto": "VigiSalud Arequipa",
        "fecha_medicion": date.today().isoformat(),
        "herramientas": calidad["v0.1"]["herramientas"],
        "entorno": eficiencia["v0.1"]["entorno"],
        "tamano": {v: calidad[v]["tamano"] for v in VERSIONES},
        "conteos_5055": {v: calidad[v]["conteos_5055"] for v in VERSIONES},
        "indicadores": indicadores,
        "resolucion": {"resueltos": resueltos, "identificados": identificados},
        "cobertura_5055": cobertura,
        "hallazgos_por_cwe_v0.1": [
            {"cwe": cwe, "debilidad": iso5055.NOMBRES_CWE.get(cwe, f"CWE-{cwe}"),
             "medidas": iso5055.medidas_de(cwe), "ocurrencias": n}
            for cwe, n in por_cwe.most_common()],
        "issue_log_v0.1": calidad["v0.1"]["hallazgos"],
        "complejidad_top_v0.1": calidad["v0.1"]["complejidad"]["top"],
        "curvas": {v: eficiencia[v]["curva"] for v in VERSIONES},
        "hotspots": {v: eficiencia[v]["hotspot"][:3] for v in VERSIONES},
        "bd_bloqueada": {v: eficiencia[v]["corridas_con_bd_bloqueada"] for v in VERSIONES},
        "resumen_funcional": eficiencia["v0.2"]["resumen_funcional"],
    }
    destino = RESULTADOS / "indicadores.json"
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    for fila in indicadores:
        print(f'{fila["codigo"]:6} {fila["nombre"][:42]:42} {str(fila["v0.1"]):>9} '
              f'{fila["semaforo_v0.1"]:8} {str(fila["v0.2"]):>9} {fila["semaforo_v0.2"]}')
    print("cobertura", {k: f'{c["cubiertos"]}/{c["total_cwe"]}' for k, c in cobertura.items()})
    print("IR-01", resueltos, "/", identificados, "| por CWE:", dict(por_cwe))


if __name__ == "__main__":
    main()
