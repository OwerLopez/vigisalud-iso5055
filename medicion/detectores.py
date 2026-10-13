"""Detectores estaticos (AST) de debilidades ISO/IEC 5055 que Pylint y Bandit no cubren.

Cada detector recibe el arbol sintactico de un modulo y devuelve hallazgos
(linea, cwe, regla, mensaje). Son heuristicas documentadas y verificables,
como exige la clausula 2 de la norma (automatizado, objetivo, transparente,
verificable).
"""

import ast
import re
import textwrap

BUCLES = (ast.For, ast.AsyncFor, ast.While, ast.ListComp, ast.SetComp, ast.DictComp,
          ast.GeneratorExp)
PATRON_HOST = re.compile(
    r"^([a-z][a-z0-9+.-]*://\S+|(\d{1,3}\.){3}\d{1,3}|[a-z0-9-]+(\.[a-z0-9-]+)*"
    r"\.(org|com|net|pe|gob|edu|local|io)(:\d+)?)$", re.IGNORECASE)
LLAMADAS_RED_CON_TIMEOUT = {"SMTP", "SMTP_SSL", "urlopen", "get", "post", "HTTPConnection",
                            "HTTPSConnection", "create_connection"}
APERTURAS = {"open": 775, "connect": 772, "SMTP": 772, "SMTP_SSL": 772, "socket": 772}


def _nombre_llamada(nodo):
    if isinstance(nodo.func, ast.Name):
        return nodo.func.id
    if isinstance(nodo.func, ast.Attribute):
        return nodo.func.attr
    return ""


def _padres(arbol):
    padres = {}
    for padre in ast.walk(arbol):
        for hijo in ast.iter_child_nodes(padre):
            padres[hijo] = padre
    return padres


def _dentro_de_bucle(nodo, padres):
    actual = padres.get(nodo)
    while actual is not None and not isinstance(actual, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if isinstance(actual, BUCLES):
            return True
        actual = padres.get(actual)
    return False


def _funcion_contenedora(nodo, padres):
    actual = padres.get(nodo)
    while actual is not None and not isinstance(actual, (ast.FunctionDef, ast.AsyncFunctionDef)):
        actual = padres.get(actual)
    return actual


def _es_texto(expr):
    return any(isinstance(n, ast.JoinedStr) or (isinstance(n, ast.Constant) and isinstance(n.value, str))
               or (isinstance(n, ast.Call) and _nombre_llamada(n) == "str") for n in ast.walk(expr))


def error_sin_accion(arbol, padres):
    """CWE-390: bloque except cuyo cuerpo solo contiene pass."""
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ExceptHandler) and all(isinstance(s, ast.Pass) for s in nodo.body):
            yield nodo.lineno, 390, "except-pass", "Excepcion capturada sin ninguna accion"


def concatenacion_en_bucle(arbol, padres):
    """CWE-1046: construccion de texto con += dentro de un bucle."""
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.AugAssign) and isinstance(nodo.op, ast.Add)
                and _es_texto(nodo.value) and _dentro_de_bucle(nodo, padres)):
            yield nodo.lineno, 1046, "str-concat-loop", "Texto concatenado con += dentro de un bucle"


def _listas_locales(funcion):
    nombres = set()
    for nodo in ast.walk(funcion):
        if isinstance(nodo, ast.Assign) and (
                isinstance(nodo.value, ast.List)
                or (isinstance(nodo.value, ast.Call) and _nombre_llamada(nodo.value) == "list")):
            nombres.update(t.id for t in nodo.targets if isinstance(t, ast.Name))
    return nombres


def busqueda_secuencial(arbol, padres):
    """CWE-1067: pertenencia sobre listas dentro de bucles y busquedas lineales."""
    for funcion in ast.walk(arbol):
        if not isinstance(funcion, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        listas = _listas_locales(funcion)
        for nodo in ast.walk(funcion):
            if (isinstance(nodo, ast.Compare) and isinstance(nodo.ops[0], (ast.In, ast.NotIn))
                    and isinstance(nodo.comparators[0], ast.Name)
                    and nodo.comparators[0].id in listas and _dentro_de_bucle(nodo, padres)):
                yield (nodo.lineno, 1067, "list-membership-loop",
                       f"Busqueda 'in' sobre la lista '{nodo.comparators[0].id}' dentro de un bucle")
            if (isinstance(nodo, ast.For) and len(nodo.body) == 1 and isinstance(nodo.body[0], ast.If)
                    and isinstance(nodo.body[0].test, ast.Compare)
                    and isinstance(nodo.body[0].test.ops[0], ast.Eq)
                    and isinstance(nodo.body[0].body[-1], (ast.Return, ast.Break))):
                yield nodo.lineno, 1067, "linear-search", "Busqueda lineal por igualdad sobre una coleccion"


def acceso_datos_en_bucle(arbol, padres):
    """CWE-1050 / CWE-1060: sentencias SQL o llamadas al repositorio dentro de bucles."""
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call) or not _dentro_de_bucle(nodo, padres):
            continue
        nombre = _nombre_llamada(nodo)
        if nombre in {"execute", "connect", "open"}:
            yield nodo.lineno, 1050, "resource-in-loop", f"Llamada '{nombre}' dentro de un bucle"
        elif (isinstance(nodo.func, ast.Attribute) and isinstance(nodo.func.value, ast.Name)
              and nodo.func.value.id == "repositorio"):
            yield nodo.lineno, 1060, "query-in-loop", f"Consulta repositorio.{nombre} dentro de un bucle"


def acceso_datos_fuera_de_gestor(arbol, padres, modulo):
    """CWE-1057: sentencias SQL fuera del modulo gestor de datos (repositorio)."""
    if modulo.endswith("repositorio"):
        return
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call) and _nombre_llamada(nodo) == "execute":
            yield nodo.lineno, 1057, "data-access-outside-dal", "SQL ejecutado fuera de repositorio"


def recursos_no_liberados(arbol, padres):
    """CWE-772 / CWE-775: recursos abiertos fuera de 'with' y nunca cerrados."""
    for funcion in ast.walk(arbol):
        if not isinstance(funcion, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        cerrados = {n.func.value.id for n in ast.walk(funcion)
                    if isinstance(n, ast.Call) and _nombre_llamada(n) == "close"
                    and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)}
        for nodo in ast.walk(funcion):
            if (isinstance(nodo, ast.Assign) and isinstance(nodo.value, ast.Call)
                    and _nombre_llamada(nodo.value) in APERTURAS
                    and isinstance(nodo.targets[0], ast.Name)
                    and nodo.targets[0].id not in cerrados):
                cwe = APERTURAS[_nombre_llamada(nodo.value)]
                yield (nodo.lineno, cwe, "resource-not-released",
                       f"'{nodo.targets[0].id}' se abre sin 'with' y no se cierra")


def red_sin_tiempo_limite(arbol, padres):
    """CWE-1088: acceso sincrono a un recurso remoto sin timeout."""
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Call) and _nombre_llamada(nodo) in LLAMADAS_RED_CON_TIMEOUT
                and isinstance(nodo.func, ast.Attribute)
                and isinstance(nodo.func.value, ast.Name)
                and nodo.func.value.id in {"smtplib", "request", "requests", "http", "socket"}
                and not any(k.arg == "timeout" for k in nodo.keywords)):
            yield nodo.lineno, 1088, "remote-no-timeout", "Conexion remota sin tiempo limite"


def red_codificada(arbol, padres):
    """CWE-1051: direcciones de red escritas directamente en el codigo."""
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Constant) and isinstance(nodo.value, str)
                and PATRON_HOST.match(nodo.value.strip())):
            yield nodo.lineno, 1051, "hardcoded-network", f"Direccion de red fija '{nodo.value}'"


def credencial_codificada(arbol, padres):
    """CWE-798: credenciales escritas en el codigo (nombres en espanol e ingles)."""
    patron = re.compile(r"(clave|contrasena|password|passwd|secreto|token)", re.IGNORECASE)
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Assign) and isinstance(nodo.value, ast.Constant)
                and isinstance(nodo.value.value, str) and nodo.value.value
                and any(isinstance(t, ast.Name) and patron.search(t.id) for t in nodo.targets)):
            yield nodo.lineno, 798, "hardcoded-credential", "Credencial escrita en el codigo fuente"


def division_sin_control(arbol, padres):
    """CWE-369: division cuyo denominador variable no se compara antes con cero."""
    for nodo in ast.walk(arbol):
        if not (isinstance(nodo, ast.BinOp) and isinstance(nodo.op, (ast.Div, ast.FloorDiv, ast.Mod))):
            continue
        if isinstance(nodo.right, ast.Constant):
            continue
        funcion = _funcion_contenedora(nodo, padres)
        denominador = ast.unparse(nodo.right)
        guardas = [ast.unparse(n) for n in ast.walk(funcion or arbol)
                   if isinstance(n, (ast.Compare, ast.If, ast.IfExp))]
        if not any(denominador in guarda for guarda in guardas):
            yield nodo.lineno, 369, "unchecked-division", f"Division entre '{denominador}' sin control de cero"


def conexiones_sin_reutilizar(arboles):
    """CWE-1072: varias rutas del codigo abren su propia conexion a la base de datos."""
    sitios = [(modulo, nodo.lineno) for modulo, arbol in arboles.items() for nodo in ast.walk(arbol)
              if isinstance(nodo, ast.Call) and _nombre_llamada(nodo) == "connect"]
    if len(sitios) > 1:
        for modulo, linea in sitios:
            yield modulo, linea, 1072, "no-connection-reuse", (
                f"Conexion nueva por operacion ({len(sitios)} puntos de conexion en el codigo)")


def codigo_comentado(fuente):
    """CWE-1085: bloques de comentarios que son codigo Python valido."""
    bloque, inicio = [], 0
    lineas = fuente.splitlines() + [""]
    for numero, linea in enumerate(lineas, start=1):
        texto = linea.strip()
        if texto.startswith("#") and not texto.startswith("#!"):
            if not bloque:
                inicio = numero
            bloque.append(linea.split("#", 1)[1][1:] if "# " in linea else linea.split("#", 1)[1])
            continue
        if bloque:
            codigo = textwrap.dedent("\n".join(bloque))
            if any(simbolo in codigo for simbolo in "(=:"):
                try:
                    ast.parse(codigo)
                    yield inicio, 1085, "commented-out-code", f"{len(bloque)} lineas de codigo comentado"
                except SyntaxError:
                    pass
            bloque = []


def analizar_modulo(modulo, fuente):
    """Aplica todos los detectores por modulo y devuelve la lista de hallazgos."""
    arbol = ast.parse(fuente)
    padres = _padres(arbol)
    detectores = [error_sin_accion, concatenacion_en_bucle, busqueda_secuencial,
                  acceso_datos_en_bucle, recursos_no_liberados, red_sin_tiempo_limite,
                  red_codificada, credencial_codificada, division_sin_control]
    hallazgos = [h for detector in detectores for h in detector(arbol, padres)]
    hallazgos += list(acceso_datos_fuera_de_gestor(arbol, padres, modulo))
    hallazgos += list(codigo_comentado(fuente))
    return arbol, hallazgos
