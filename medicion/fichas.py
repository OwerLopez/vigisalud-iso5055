"""Fichas de indicadores de VigiSalud (estructura de indicadores del TP5).

Cada ficha sigue el modelo de informacion de medicion (ISO/IEC 15939 / ISO/IEC 25020):
medidas base -> funcion de medicion -> indicador -> criterio de decision, y
se vincula a la medida ISO/IEC 5055 y a la actividad de revision ISO/IEC 20246
en la que se usa.
"""

MENOR_MEJOR = "menor es mejor"
MAYOR_MEJOR = "mayor es mejor"

FICHAS = [
    {
        "codigo": "IC-01", "grupo": "Calidad", "nombre": "Densidad de debilidades de mantenibilidad",
        "caracteristica": "Mantenibilidad (ISO/IEC 25010)", "medida_5055": "ASCMM",
        "cwe": "29 CWE de la cláusula 7.1 (p. ej. 561, 1041, 1064, 1085, 1121)",
        "pregunta": "¿Cuántas debilidades graves de mantenibilidad hay por cada mil líneas?",
        "medidas_base": "Ocurrencias de CWE de mantenibilidad; SLOC",
        "formula": "IC-01 = (suma de ocurrencias CWE de mantenibilidad / SLOC) × 1000",
        "unidad": "debilidades/KSLOC", "escala": "Razón (0 a infinito)",
        "herramienta": "Pylint + Radon + detectores AST", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 2.0, "ambar": 5.0,
        "interpretacion": "Valores altos anticipan mayor costo y riesgo al modificar el código.",
        "responsable": "Líder técnico",
    },
    {
        "codigo": "IC-02", "grupo": "Calidad", "nombre": "Densidad de debilidades de fiabilidad",
        "caracteristica": "Fiabilidad (ISO/IEC 25010)", "medida_5055": "ASCRM",
        "cwe": "74 CWE de la cláusula 7.3 (p. ej. 369, 390, 703, 772, 1088)",
        "pregunta": "¿Cuántas debilidades que pueden provocar fallas o caídas hay por KSLOC?",
        "medidas_base": "Ocurrencias de CWE de fiabilidad; SLOC",
        "formula": "IC-02 = (suma de ocurrencias CWE de fiabilidad / SLOC) × 1000",
        "unidad": "debilidades/KSLOC", "escala": "Razón (0 a infinito)",
        "herramienta": "Pylint + Bandit + detectores AST", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 1.0, "ambar": 3.0,
        "interpretacion": "Un sistema de alertas sanitarias no debe fallar en silencio; se espera un valor cercano a 0.",
        "responsable": "Líder técnico",
    },
    {
        "codigo": "IC-03", "grupo": "Calidad", "nombre": "Densidad de debilidades de seguridad",
        "caracteristica": "Seguridad (ISO/IEC 25010)", "medida_5055": "ASCSM",
        "cwe": "73 CWE de la cláusula 7.4 (p. ej. 89, 259, 798, 772, 1057)",
        "pregunta": "¿Cuántas debilidades explotables hay por KSLOC en un sistema que guarda datos de salud?",
        "medidas_base": "Ocurrencias de CWE de seguridad; SLOC",
        "formula": "IC-03 = (suma de ocurrencias CWE de seguridad / SLOC) × 1000",
        "unidad": "debilidades/KSLOC", "escala": "Razón (0 a infinito)",
        "herramienta": "Bandit + detectores AST", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 0.0, "ambar": 2.0,
        "interpretacion": "Por tratarse de datos personales de salud (Ley 29733), la meta es 0.",
        "responsable": "Responsable de seguridad",
    },
    {
        "codigo": "IC-04", "grupo": "Calidad", "nombre": "Funciones con complejidad excesiva",
        "caracteristica": "Mantenibilidad: analizabilidad y capacidad de prueba", "medida_5055": "ASCMM",
        "cwe": "CWE-1121",
        "pregunta": "¿Qué proporción de funciones supera la complejidad ciclomática de 10?",
        "medidas_base": "Complejidad ciclomática (CC) por función; número de funciones",
        "formula": "IC-04 = (funciones con CC > 10 / total de funciones) × 100",
        "unidad": "%", "escala": "Razón (0 a 100)",
        "herramienta": "Radon (cc)", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 5.0, "ambar": 10.0,
        "interpretacion": "Cada función sobre el límite necesita más casos de prueba y es difícil de revisar.",
        "responsable": "Desarrollador autor",
    },
    {
        "codigo": "IC-05", "grupo": "Calidad", "nombre": "Índice de mantenibilidad",
        "caracteristica": "Mantenibilidad: modificabilidad", "medida_5055": "Complementario",
        "cwe": "No aplica (combina Halstead, CC y SLOC)",
        "pregunta": "¿Qué tan fácil es entender y modificar cada módulo?",
        "medidas_base": "Volumen de Halstead, CC, SLOC y comentarios por módulo",
        "formula": "MI = max(0, (171 - 5.2 ln V - 0.23 CC - 16.2 ln SLOC) × 100 / 171), promedio ponderado por SLOC",
        "unidad": "puntos (0-100)", "escala": "Intervalo (0 a 100)",
        "herramienta": "Radon (mi)", "momento": "Análisis de hallazgos (6.4.4)",
        "sentido": MAYOR_MEJOR, "verde": 50.0, "ambar": 38.0,
        "interpretacion": "Sobre 50 la mantenibilidad es alta; bajo 38, el módulo es candidato a reestructurarse.",
        "responsable": "Líder técnico",
    },
    {
        "codigo": "IC-06", "grupo": "Calidad", "nombre": "Código duplicado",
        "caracteristica": "Mantenibilidad: reusabilidad", "medida_5055": "ASCMM",
        "cwe": "CWE-1041",
        "pregunta": "¿Qué porcentaje del código está copiado y pegado?",
        "medidas_base": "Líneas en bloques duplicados (6 o más líneas); SLOC",
        "formula": "IC-06 = (líneas duplicadas / SLOC) × 100",
        "unidad": "%", "escala": "Razón (0 a 100)",
        "herramienta": "Pylint (duplicate-code)", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 3.0, "ambar": 5.0,
        "interpretacion": "La duplicación obliga a corregir el mismo error en varios lugares.",
        "responsable": "Desarrollador autor",
    },
    {
        "codigo": "IE-01", "grupo": "Eficiencia", "nombre": "Densidad de debilidades de eficiencia",
        "caracteristica": "Eficiencia de desempeño (ISO/IEC 25010)", "medida_5055": "ASCPEM",
        "cwe": "18 CWE de la cláusula 7.2 (p. ej. 772, 775, 1046, 1050, 1057, 1060, 1067, 1072)",
        "pregunta": "¿Cuántos patrones de código que desperdician tiempo o recursos hay por KSLOC?",
        "medidas_base": "Ocurrencias de CWE de eficiencia; SLOC",
        "formula": "IE-01 = (suma de ocurrencias CWE de eficiencia / SLOC) × 1000",
        "unidad": "debilidades/KSLOC", "escala": "Razón (0 a infinito)",
        "herramienta": "Detectores AST + Pylint", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 1.0, "ambar": 3.0,
        "interpretacion": "Es la causa estática; IE-02 a IE-05 muestran su efecto medido en ejecución.",
        "responsable": "Líder técnico",
    },
    {
        "codigo": "IE-02", "grupo": "Eficiencia", "nombre": "Tiempo de procesamiento semanal",
        "caracteristica": "Eficiencia: comportamiento temporal", "medida_5055": "Medida dinámica (ISO/IEC 25023)",
        "cwe": "Efecto de CWE-1050, 1060, 1067",
        "pregunta": "¿Cuánto tarda el sistema en procesar la carga de referencia?",
        "medidas_base": "Tiempo de reloj de 5 ejecuciones con N = 20 000 notificaciones",
        "formula": "IE-02 = mediana(t1..t5)",
        "unidad": "segundos", "escala": "Razón",
        "herramienta": "time.perf_counter", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 2.0, "ambar": 5.0,
        "interpretacion": "El requisito no funcional fija 2 s para emitir el reporte y las alertas de la semana.",
        "responsable": "Tester de desempeño",
    },
    {
        "codigo": "IE-03", "grupo": "Eficiencia", "nombre": "Rendimiento (throughput)",
        "caracteristica": "Eficiencia: capacidad", "medida_5055": "Medida dinámica (ISO/IEC 25023)",
        "cwe": "No aplica",
        "pregunta": "¿Cuántas notificaciones procesa el sistema por segundo?",
        "medidas_base": "N procesadas; tiempo IE-02",
        "formula": "IE-03 = N / IE-02",
        "unidad": "notificaciones/s", "escala": "Razón",
        "herramienta": "time.perf_counter", "momento": "Revisión individual (6.4.3)",
        "sentido": MAYOR_MEJOR, "verde": 10000.0, "ambar": 4000.0,
        "interpretacion": "Permite dimensionar picos de notificación durante un brote.",
        "responsable": "Tester de desempeño",
    },
    {
        "codigo": "IE-04", "grupo": "Eficiencia", "nombre": "Memoria pico",
        "caracteristica": "Eficiencia: utilización de recursos", "medida_5055": "Medida dinámica (ISO/IEC 25023)",
        "cwe": "Efecto de CWE-401, 772, 775",
        "pregunta": "¿Cuánta memoria necesita el procesamiento de la carga de referencia?",
        "medidas_base": "Pico de memoria asignada con N = 20 000",
        "formula": "IE-04 = pico de tracemalloc / 1 048 576",
        "unidad": "MB", "escala": "Razón",
        "herramienta": "tracemalloc", "momento": "Revisión individual (6.4.3)",
        "sentido": MENOR_MEJOR, "verde": 50.0, "ambar": 100.0,
        "interpretacion": "Los servidores del primer nivel de atención tienen poca memoria disponible.",
        "responsable": "Tester de desempeño",
    },
    {
        "codigo": "IE-05", "grupo": "Eficiencia", "nombre": "Exponente de escalabilidad",
        "caracteristica": "Eficiencia: capacidad", "medida_5055": "Relacionado con CWE-407",
        "cwe": "CWE-407 (complejidad algorítmica)",
        "pregunta": "¿Cómo crece el tiempo cuando crece el volumen de notificaciones?",
        "medidas_base": "Tiempos con N = 2 500, 5 000, 10 000, 20 000 y 40 000",
        "formula": "b en t = a × N^b (regresión lineal de log t contra log N)",
        "unidad": "adimensional", "escala": "Razón",
        "herramienta": "Script de benchmark", "momento": "Análisis de hallazgos (6.4.4)",
        "sentido": MENOR_MEJOR, "verde": 1.2, "ambar": 1.5,
        "interpretacion": "b cercano a 1 es crecimiento lineal; b cercano a 2 indica un costo cuadrático.",
        "responsable": "Tester de desempeño",
    },
    {
        "codigo": "IE-06", "grupo": "Eficiencia", "nombre": "Concentración del costo (hotspot)",
        "caracteristica": "Eficiencia: comportamiento temporal", "medida_5055": "Diagnóstico",
        "cwe": "Orienta la corrección de CWE de eficiencia",
        "pregunta": "¿Qué parte del tiempo consume la función más costosa?",
        "medidas_base": "Tiempo propio por función (cProfile) con N = 20 000",
        "formula": "IE-06 = (tiempo propio de la función más costosa / tiempo total) × 100",
        "unidad": "%", "escala": "Razón (0 a 100)",
        "herramienta": "cProfile", "momento": "Análisis de hallazgos (6.4.4)",
        "sentido": MENOR_MEJOR, "verde": 30.0, "ambar": 50.0,
        "interpretacion": "Sobre 50 % un solo punto domina el costo y es la primera corrección a priorizar.",
        "responsable": "Líder técnico",
    },
    {
        "codigo": "IR-01", "grupo": "Proceso de revisión", "nombre": "Tasa de resolución de hallazgos",
        "caracteristica": "Proceso de revisión ISO/IEC 20246", "medida_5055": "Sobre hallazgos ASCMM/ASCPEM/ASCRM/ASCSM",
        "cwe": "Todos los CWE registrados en el Issue Log",
        "pregunta": "¿Qué proporción de los hallazgos de la revisión fue corregida?",
        "medidas_base": "Hallazgos de la versión revisada; hallazgos que siguen en la nueva versión",
        "formula": "IR-01 = (hallazgos resueltos / hallazgos identificados) × 100",
        "unidad": "%", "escala": "Razón (0 a 100)",
        "herramienta": "Issue Log generado por la herramienta", "momento": "Corrección y reporte (6.4.5)",
        "sentido": MAYOR_MEJOR, "verde": 90.0, "ambar": 70.0,
        "interpretacion": "Es el criterio de salida: con 90 % o más el producto se acepta.",
        "responsable": "Líder de revisión",
    },
]


def semaforo(ficha, valor):
    """Devuelve VERDE, AMBAR o ROJO segun los umbrales de la ficha."""
    if valor is None:
        return "SIN DATO"
    if ficha["sentido"] == MENOR_MEJOR:
        if valor <= ficha["verde"]:
            return "VERDE"
        return "AMBAR" if valor <= ficha["ambar"] else "ROJO"
    if valor >= ficha["verde"]:
        return "VERDE"
    return "AMBAR" if valor >= ficha["ambar"] else "ROJO"
