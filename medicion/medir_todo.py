"""Ejecuta la medicion completa (calidad + eficiencia + consolidacion) de todas las versiones.

Uso: python medicion/medir_todo.py
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VERSIONES = ("v0.1", "v0.2")


def paso(*argumentos):
    print(">", " ".join(argumentos))
    subprocess.run([sys.executable, *argumentos], cwd=RAIZ, check=True)


if __name__ == "__main__":
    for version in VERSIONES:
        paso("medicion/medir_calidad.py", f"codigo/{version}", f"resultados/calidad_{version}.json")
        paso("medicion/medir_eficiencia.py", f"codigo/{version}", f"resultados/eficiencia_{version}.json")
    paso("medicion/consolidar.py")
    print("Listo: resultados/indicadores.json (abrir web/index.html para ver el dashboard)")
