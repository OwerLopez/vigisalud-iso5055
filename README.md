# VigiSalud Arequipa · ISO/IEC 20246 + ISO/IEC 5055

Trabajo Parcial 5 del curso **Calidad de Software** (UNSA, Escuela Profesional de Ingeniería de Sistemas, 2026-B).

VigiSalud Arequipa es un prototipo de vigilancia epidemiológica y alerta temprana (dengue, IRA y EDA) para
establecimientos del primer nivel de atención. Este repositorio aplica al código del proyecto:

- **ISO/IEC 20246:2017** como proceso de revisión del código (planificación, inicio, revisión individual,
  análisis de hallazgos, corrección y reporte).
- **ISO/IEC 5055:2021** como fuente de indicadores automatizados (debilidades CWE de mantenibilidad,
  eficiencia, fiabilidad y seguridad).

**Dashboard en vivo:** https://vigisalud-iso5055.vercel.app (inglés) · https://vigisalud-iso5055.vercel.app/?lang=es (español)

## Resultados

| Indicador | v0.1 (línea base) | v0.2 (tras la revisión) |
|---|---:|---:|
| Debilidades ISO 5055 detectadas | 44 | 0 |
| Tiempo con 20 000 notificaciones (IE-02) | 3,94 s | 0,18 s |
| Rendimiento (IE-03) | 5 076 notif./s | 108 284 notif./s |
| Exponente de escalabilidad (IE-05) | 1,33 | 0,73 |
| Tasa de resolución de hallazgos (IR-01) | — | 100 % |

Ambas versiones producen exactamente los mismos resultados funcionales.

## Estructura

```
codigo/v0.1, codigo/v0.2   Prototipo antes y después de la revisión
medicion/                  Herramienta QMeter: fichas, mapeo CWE, detectores AST, benchmark
resultados/                Mediciones en JSON (por versión, consolidado y datos del dashboard)
site/                      Dashboard estático desplegado en Vercel
docs/                      Generadores del informe, gráficos y diapositivas
```

## Cómo medir

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python medicion\medir_todo.py
.venv\Scripts\python medicion\exportar_dashboard.py
.venv\Scripts\python web\construir_sitio.py
```

La herramienta combina Radon, Pylint y Bandit (reglas mapeadas a CWE de la ISO 5055), 13 detectores propios
sobre el árbol sintáctico de Python, y `time.perf_counter`, `tracemalloc` y `cProfile` para la eficiencia.
Los datos de prueba son sintéticos y reproducibles; no contienen información de pacientes.

## Indicadores

- **Calidad (IC-01 a IC-06):** densidades ASCMM, ASCRM y ASCSM por KSLOC, funciones con CC > 10, índice de
  mantenibilidad y código duplicado.
- **Eficiencia (IE-01 a IE-06):** densidad ASCPEM, tiempo de procesamiento, rendimiento, memoria pico,
  exponente de escalabilidad y concentración del costo.
- **Proceso (IR-01):** tasa de resolución de hallazgos de la revisión.

Las fichas completas (fórmula, unidad, umbrales, interpretación y responsable) están en
[`medicion/fichas.py`](medicion/fichas.py).
