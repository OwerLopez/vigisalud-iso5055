"""Benchmark de eficiencia (IE-02 a IE-06) para una version de VigiSalud.

Uso: python medicion/medir_eficiencia.py codigo/v0.1 resultados/eficiencia_v0.1.json
Cada medicion corre en un proceso nuevo, con la base de datos recreada, sobre
datos sinteticos generados con semilla fija (reproducibles).
"""

import json
import math
import platform
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import generar_datos  # noqa: E402

TAMANOS = (2500, 5000, 10000, 20000, 40000)
N_REFERENCIA = 20000
REPETICIONES_REFERENCIA = 5
REPETICIONES = 3
EJECUTOR = Path(__file__).with_name("_ejecutor.py")


def _correr(raiz, csv, carpeta, modo):
    salida = subprocess.run(
        [sys.executable, str(EJECUTOR), str(Path(raiz).resolve()), str(csv),
         str(Path(carpeta) / "bench.db"), str(Path(carpeta) / "reporte.html"), modo],
        capture_output=True, text=True, check=True)
    return json.loads(salida.stdout)


def _pendiente_loglog(puntos):
    xs = [math.log(n) for n, _ in puntos]
    ys = [math.log(t) for _, t in puntos]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def medir(raiz):
    """Devuelve las medidas dinamicas de eficiencia de una version."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as carpeta:
        archivos = {}
        for n in TAMANOS:
            archivos[n] = Path(carpeta) / f"notificaciones_{n}.csv"
            generar_datos.escribir_csv(archivos[n], generar_datos.generar(n))

        curva, resumen, bloqueos, corridas = [], None, 0, 0
        for n in TAMANOS:
            reps = REPETICIONES_REFERENCIA if n == N_REFERENCIA else REPETICIONES
            tiempos = []
            for _ in range(reps):
                corrida = _correr(raiz, archivos[n], carpeta, "tiempo")
                tiempos.append(corrida["medida"]["segundos"])
                bloqueos += corrida["medida"]["bd_bloqueada"]
                corridas += 1
                if n == N_REFERENCIA:
                    resumen = corrida["resumen"]
            curva.append({"n": n, "mediana_s": round(statistics.median(tiempos), 4),
                          "tiempos_s": [round(t, 4) for t in tiempos]})

        referencia = next(p for p in curva if p["n"] == N_REFERENCIA)
        memoria = _correr(raiz, archivos[N_REFERENCIA], carpeta, "memoria")["medida"]
        perfil = _correr(raiz, archivos[N_REFERENCIA], carpeta, "perfil")["medida"]

    return {
        "version": Path(raiz).name,
        "entorno": {"python": platform.python_version(), "sistema": platform.platform(),
                    "procesador": platform.processor()},
        "n_referencia": N_REFERENCIA,
        "tiempo_s": referencia["mediana_s"],
        "throughput": round(N_REFERENCIA / referencia["mediana_s"], 1),
        "memoria_pico_mb": round(memoria["pico_mb"], 2),
        "exponente_escalabilidad": round(_pendiente_loglog([(p["n"], p["mediana_s"]) for p in curva]), 3),
        "hotspot": perfil["top"],
        "hotspot_pct": perfil["top"][0]["porcentaje"],
        "corridas_con_bd_bloqueada": f"{bloqueos}/{corridas}",
        "curva": curva,
        "resumen_funcional": resumen,
    }


if __name__ == "__main__":
    resultado = medir(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in resultado.items() if k not in ("curva", "resumen_funcional")},
                     indent=1))
