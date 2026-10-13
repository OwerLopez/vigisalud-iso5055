"""Ejecuta una vez el pipeline de una version en un proceso aislado.

Uso interno de medir_eficiencia.py:
    python _ejecutor.py <raiz_version> <csv> <bd> <reporte> <modo: tiempo|memoria|perfil>
Imprime un JSON con la medida y el resumen funcional (para verificar que ambas
versiones producen el mismo resultado).
"""

import cProfile
import gc
import json
import os
import pstats
import sys
import time
import tracemalloc


def _eliminar(bd):
    """Borra la base de datos; devuelve True si quedo bloqueada por conexiones abiertas."""
    try:
        os.remove(bd)
        return False
    except PermissionError:
        gc.collect()  # libera las conexiones que el codigo dejo sin cerrar (CWE-772)
        os.remove(bd)
        return True


def main():
    raiz, csv, bd, reporte, modo = sys.argv[1:6]
    sys.path.insert(0, raiz)
    from vigisalud import pipeline  # pylint: disable=import-outside-toplevel

    if os.path.exists(bd):
        os.remove(bd)
    medida = {}
    if modo == "tiempo":
        inicio = time.perf_counter()
        resumen = pipeline.ejecutar(csv, bd, reporte)
        medida["segundos"] = time.perf_counter() - inicio
    elif modo == "memoria":
        tracemalloc.start()
        resumen = pipeline.ejecutar(csv, bd, reporte)
        medida["pico_mb"] = tracemalloc.get_traced_memory()[1] / 1_048_576
        tracemalloc.stop()
    else:
        perfil = cProfile.Profile()
        resumen = perfil.runcall(pipeline.ejecutar, csv, bd, reporte)
        estadisticas = pstats.Stats(perfil)
        total = estadisticas.total_tt
        funciones = sorted(estadisticas.stats.items(), key=lambda kv: -kv[1][2])[:5]
        medida["total_s"] = total
        medida["top"] = [{"funcion": f"{os.path.basename(archivo)}:{linea}({nombre})",
                          "tiempo_propio_s": round(datos[2], 4),
                          "porcentaje": round(datos[2] / total * 100, 1)}
                         for (archivo, linea, nombre), datos in funciones]
    medida["bd_bloqueada"] = _eliminar(bd)
    print(json.dumps({"medida": medida, "resumen": resumen}, default=str))


if __name__ == "__main__":
    main()
