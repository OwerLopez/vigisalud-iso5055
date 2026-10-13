"""Captura y procesa las medidas estaticas ISO/IEC 5055 de una version de VigiSalud.

Uso: python medicion/medir_calidad.py codigo/v0.1 resultados/calidad_v0.1.json
"""

import json
import re
import subprocess
import sys
from collections import Counter
from importlib import metadata
from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

sys.path.insert(0, str(Path(__file__).parent))
import detectores  # noqa: E402
import iso5055  # noqa: E402

LIMITE_CC = 10
MENSAJES_PYLINT = ",".join(iso5055.PYLINT_A_CWE)
PATRON_DUPLICADO = re.compile(r"==([\w.]+):\[(\d+):(\d+)\]")


def _python():
    return sys.executable


def _modulos(raiz):
    paquete = Path(raiz) / "vigisalud"
    return {f"vigisalud.{p.stem}": p for p in sorted(paquete.glob("*.py"))}


def ejecutar_pylint(raiz):
    """Ejecuta Pylint solo con las reglas mapeadas a CWE de la norma."""
    salida = subprocess.run(
        [_python(), "-m", "pylint", "vigisalud", "--disable=all", f"--enable={MENSAJES_PYLINT}",
         "--max-args=7", "--max-positional-arguments=7", "--min-similarity-lines=6",
         "--output-format=json", "--score=n"],
        cwd=raiz, capture_output=True, text=True, check=False)
    return json.loads(salida.stdout or "[]")


def ejecutar_bandit(raiz):
    """Ejecuta Bandit sobre el paquete y devuelve sus resultados."""
    salida = subprocess.run([_python(), "-m", "bandit", "-r", "vigisalud", "-f", "json", "-q"],
                            cwd=raiz, capture_output=True, text=True, check=False)
    return json.loads(salida.stdout)["results"]


def _hallazgo(modulo, linea, cwe, herramienta, regla, mensaje):
    return {"modulo": modulo, "linea": linea, "cwe": cwe,
            "debilidad": iso5055.NOMBRES_CWE.get(cwe, f"CWE-{cwe}"),
            "medidas": iso5055.medidas_de(cwe), "herramienta": herramienta,
            "regla": regla, "mensaje": mensaje}


def _lineas_duplicadas(mensajes):
    lineas = 0
    for mensaje in mensajes:
        rangos = PATRON_DUPLICADO.findall(mensaje["message"])
        # La primera copia es el original; las demas se cuentan como duplicadas.
        lineas += sum(int(fin) - int(inicio) for _, inicio, fin in rangos[1:])
    return lineas


def medir(raiz):
    """Devuelve el diccionario completo de medidas estaticas para una version."""
    modulos = _modulos(raiz)
    fuentes = {m: p.read_text(encoding="utf-8") for m, p in modulos.items()}
    hallazgos, arboles, tamano, funciones, mi = [], {}, Counter(), [], {}

    for modulo, fuente in fuentes.items():
        crudo = analyze(fuente)
        tamano.update(loc=crudo.loc, sloc=crudo.sloc, lloc=crudo.lloc,
                      comentarios=crudo.comments, modulos=1)
        mi[modulo] = {"mi": round(mi_visit(fuente, multi=True), 2), "sloc": crudo.sloc}
        for bloque in cc_visit(fuente):
            for item in [bloque] + list(getattr(bloque, "methods", [])):
                if item.letter in ("F", "M"):
                    funciones.append({"modulo": modulo, "funcion": item.name,
                                      "linea": item.lineno, "cc": item.complexity})
                    if item.complexity > LIMITE_CC:
                        hallazgos.append(_hallazgo(modulo, item.lineno, 1121, "Radon", "cc>10",
                                                   f"{item.name}: CC = {item.complexity}"))
        arbol, propios = detectores.analizar_modulo(modulo, fuente)
        arboles[modulo] = arbol
        hallazgos += [_hallazgo(modulo, l, c, "Detector AST", r, m) for l, c, r, m in propios]
    hallazgos += [_hallazgo(m, l, c, "Detector AST", r, t)
                  for m, l, c, r, t in detectores.conexiones_sin_reutilizar(arboles)]

    pylint = ejecutar_pylint(raiz)
    for mensaje in pylint:
        cwe = iso5055.PYLINT_A_CWE.get(mensaje["symbol"])
        if cwe == 1041:
            # Pylint informa la duplicacion en un modulo cualquiera; se ubica en la copia.
            copia = PATRON_DUPLICADO.findall(mensaje["message"])[-1]
            mensaje = dict(mensaje, module=copia[0], line=int(copia[1]) + 1)
        if cwe:
            hallazgos.append(_hallazgo(mensaje["module"], mensaje["line"], cwe, "Pylint",
                                       f"{mensaje['message-id']} {mensaje['symbol']}",
                                       mensaje["message"].splitlines()[0]))

    fuera_de_norma = []
    for resultado in ejecutar_bandit(raiz):
        cwe = resultado.get("issue_cwe", {}).get("id")
        modulo = "vigisalud." + Path(resultado["filename"]).stem
        if cwe and iso5055.medidas_de(cwe):
            hallazgos.append(_hallazgo(modulo, resultado["line_number"], cwe, "Bandit",
                                       f"{resultado['test_id']} {resultado['test_name']}",
                                       resultado["issue_text"]))
        else:
            fuera_de_norma.append({"modulo": modulo, "regla": resultado["test_id"], "cwe": cwe})

    # Una ocurrencia = (modulo, linea, CWE); si dos herramientas la detectan, cuenta una vez.
    unicos = {}
    for h in hallazgos:
        clave = (h["modulo"], h["linea"], h["cwe"])
        if clave in unicos:
            unicos[clave]["herramienta"] += " + " + h["herramienta"]
        else:
            unicos[clave] = h
    hallazgos = sorted(unicos.values(), key=lambda h: (h["modulo"], h["linea"], h["cwe"]))

    ksloc = tamano["sloc"] / 1000
    conteos = {clave: sum(1 for h in hallazgos if clave in h["medidas"]) for clave in iso5055.MEDIDAS}
    duplicadas = _lineas_duplicadas([m for m in pylint if m["symbol"] == "duplicate-code"])
    complejas = [f for f in funciones if f["cc"] > LIMITE_CC]
    mi_ponderado = sum(v["mi"] * v["sloc"] for v in mi.values()) / max(1, tamano["sloc"])

    return {
        "version": Path(raiz).name,
        "herramientas": {p: metadata.version(p) for p in ("radon", "pylint", "bandit")},
        "tamano": dict(tamano, funciones=len(funciones), ksloc=round(ksloc, 3)),
        "conteos_5055": conteos,
        "densidades_5055": {k: round(v / ksloc, 2) for k, v in conteos.items()},
        "complejidad": {
            "promedio": round(sum(f["cc"] for f in funciones) / max(1, len(funciones)), 2),
            "maxima": max((f["cc"] for f in funciones), default=0),
            "funciones_sobre_limite": len(complejas),
            "porcentaje_sobre_limite": round(len(complejas) / max(1, len(funciones)) * 100, 2),
            "top": sorted(funciones, key=lambda f: -f["cc"])[:5],
        },
        "mantenibilidad_mi": {"promedio_ponderado": round(mi_ponderado, 2), "por_modulo": mi},
        "duplicacion": {"lineas": duplicadas,
                        "porcentaje": round(duplicadas / max(1, tamano["sloc"]) * 100, 2)},
        "hallazgos": hallazgos,
        "bandit_fuera_de_norma": fuera_de_norma,
    }


if __name__ == "__main__":
    resultado = medir(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("tamano", "conteos_5055", "densidades_5055")},
                     indent=1))
