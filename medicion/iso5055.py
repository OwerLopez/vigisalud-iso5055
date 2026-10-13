"""Catalogo ISO/IEC 5055:2021 y mapeo de reglas de las herramientas a CWE.

Las listas de CWE por caracteristica se tomaron de la clausula 7 de la norma
(7.1 Mantenibilidad, 7.2 Eficiencia de desempeno, 7.3 Fiabilidad, 7.4 Seguridad).
Una misma debilidad puede pertenecer a varias medidas (p. ej. CWE-772) y, como
indica la norma, se cuenta en cada medida a la que pertenece.
"""

MANTENIBILIDAD = frozenset({
    407, 478, 480, 484, 561, 570, 571, 783, 1041, 1045, 1047, 1048, 1051, 1052, 1054,
    1055, 1062, 1064, 1074, 1075, 1079, 1080, 1084, 1085, 1086, 1087, 1090, 1095, 1121})

EFICIENCIA = frozenset({
    401, 404, 424, 772, 775, 1042, 1043, 1046, 1049, 1050, 1057, 1060, 1067, 1072, 1073,
    1089, 1091, 1094})

FIABILIDAD = frozenset({
    119, 120, 123, 125, 130, 131, 170, 194, 195, 196, 197, 248, 252, 366, 369, 390, 391,
    392, 394, 401, 404, 415, 416, 424, 456, 457, 459, 476, 480, 484, 543, 562, 567, 595,
    597, 662, 665, 667, 672, 681, 682, 703, 704, 758, 764, 772, 775, 786, 787, 788, 805,
    820, 821, 822, 823, 824, 825, 833, 835, 908, 1045, 1051, 1058, 1066, 1070, 1077, 1079,
    1082, 1083, 1087, 1088, 1096, 1097, 1098})

SEGURIDAD = frozenset({
    22, 23, 36, 77, 78, 79, 88, 89, 90, 91, 99, 119, 120, 123, 125, 129, 130, 131, 134,
    194, 195, 196, 197, 252, 259, 321, 366, 369, 401, 404, 415, 416, 424, 434, 456, 457,
    477, 480, 502, 543, 564, 567, 570, 571, 606, 611, 643, 652, 662, 665, 667, 672, 681,
    682, 732, 772, 775, 778, 783, 786, 787, 788, 789, 798, 805, 820, 821, 822, 823, 824,
    825, 835, 1057})

MEDIDAS = {
    "ASCMM": ("Mantenibilidad", MANTENIBILIDAD),
    "ASCPEM": ("Eficiencia de desempeno", EFICIENCIA),
    "ASCRM": ("Fiabilidad", FIABILIDAD),
    "ASCSM": ("Seguridad", SEGURIDAD),
}

NOMBRES_CWE = {
    561: "Codigo muerto",
    570: "Expresion siempre falsa",
    571: "Expresion siempre verdadera",
    1041: "Codigo redundante (copiar y pegar)",
    1047: "Modulos con dependencias circulares",
    1051: "Configuracion de red codificada en el fuente",
    1064: "Firma con numero excesivo de parametros",
    1074: "Herencia excesivamente profunda",
    1080: "Archivo con exceso de lineas",
    1085: "Volumen excesivo de codigo comentado",
    1121: "Complejidad ciclomatica de McCabe excesiva",
    369: "Division por cero",
    390: "Condicion de error detectada sin accion",
    703: "Manejo incorrecto de condiciones excepcionales",
    1088: "Acceso sincrono a recurso remoto sin tiempo limite",
    89: "Inyeccion SQL",
    259: "Contrasena codificada en el fuente",
    798: "Credenciales codificadas en el fuente",
    78: "Inyeccion de comandos del SO",
    502: "Deserializacion de datos no confiables",
    22: "Recorrido de rutas (path traversal)",
    772: "Recurso no liberado tras su vida util",
    775: "Descriptor de archivo no liberado",
    1046: "Texto inmutable creado por concatenacion",
    1050: "Consumo excesivo de recursos de plataforma dentro de un bucle",
    1057: "Acceso a datos fuera del componente gestor de datos",
    1067: "Busquedas secuenciales excesivas",
    1072: "Acceso a datos sin reutilizacion de conexiones (pool)",
}

# Mensajes de Pylint -> CWE de la norma.
PYLINT_A_CWE = {
    "too-many-arguments": 1064,          # R0913 (max-args = 7)
    "too-many-positional-arguments": 1064,
    "duplicate-code": 1041,              # R0801
    "unreachable": 561,                  # W0101
    "using-constant-test": 570,          # W0125
    "cyclic-import": 1047,               # R0401
    "too-many-lines": 1080,              # C0302 (max 1000)
    "too-many-ancestors": 1074,          # R0901
    "bare-except": 703,                  # W0702
    "broad-exception-caught": 703,       # W0718
    "consider-using-join": 1046,         # R1713
}
# Los recursos no liberados (CWE-772/775) los detecta detectores.py, que distingue
# archivos (775) de conexiones y sockets (772).

# Bandit ya informa el CWE de cada hallazgo; solo se cuentan los que pertenecen
# a alguna medida ISO 5055. Los demas se informan como "fuera de la norma".


def medidas_de(cwe):
    """Devuelve las medidas ISO 5055 a las que pertenece un CWE."""
    return [clave for clave, (_, conjunto) in MEDIDAS.items() if cwe in conjunto]
