"""Construye docs/informe_TP5.html (informe en espanol) a partir de los resultados medidos.

Uso: python docs/construir_informe.py
El HTML se sube a Google Drive y se convierte en Google Docs.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "medicion"))
import fichas as F  # noqa: E402

D = json.loads((RAIZ / "resultados" / "indicadores.json").read_text(encoding="utf-8"))
G = json.loads((RAIZ / "resultados" / "graficos.json").read_text(encoding="utf-8"))
C1 = json.loads((RAIZ / "resultados" / "calidad_v0.1.json").read_text(encoding="utf-8"))
C2 = json.loads((RAIZ / "resultados" / "calidad_v0.2.json").read_text(encoding="utf-8"))
E1 = json.loads((RAIZ / "resultados" / "eficiencia_v0.1.json").read_text(encoding="utf-8"))
E2 = json.loads((RAIZ / "resultados" / "eficiencia_v0.2.json").read_text(encoding="utf-8"))

GUINDA = "#7A1F2B"
TABLA = 'style="border-collapse:collapse;width:100%;margin:4pt 0 4pt 0"'
TH = 'class="h"'
TD = 'class="c"'
TDN = 'class="n"'
ESTILOS = (f"<style>th.h{{background-color:{GUINDA};color:#FFFFFF;font-weight:bold;border:1px solid #BFBFBF;"
           "padding:4pt;font-size:9.5pt;text-align:left;vertical-align:top}"
           "td.c{border:1px solid #BFBFBF;padding:4pt;font-size:9.5pt;vertical-align:top}"
           "td.n{border:1px solid #BFBFBF;padding:4pt;font-size:9.5pt;vertical-align:top;text-align:right}</style>")
COLOR = {"VERDE": "#1B7F3B", "AMBAR": "#A15C00", "ROJO": "#B3261E", "SIN DATO": "#6B7280"}
ESTADO = {"VERDE": "Verde", "AMBAR": "Ámbar", "ROJO": "Rojo", "SIN DATO": "Sin dato"}


def es(numero, decimales=2):
    """Formato numerico peruano: coma decimal y espacio de miles."""
    if numero is None:
        return "—"
    texto = f"{numero:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return texto


def tabla(encabezados, filas, numericas=()):
    html = [f"<table {TABLA}><tr>"] + [f"<th {TH}>{h}</th>" for h in encabezados] + ["</tr>"]
    for fila in filas:
        html.append("<tr>")
        for i, celda in enumerate(fila):
            html.append(f"<td {TDN if i in numericas else TD}>{celda}</td>")
        html.append("</tr>")
    html.append("</table>")
    return "".join(html)


def estado(semaforo):
    return f'<span style="color:{COLOR[semaforo]};font-weight:bold">{ESTADO[semaforo]}</span>'


def figura(url, ancho, texto):
    return (f'<p style="text-align:center"><img src="{url}" width="{ancho}"></p>'
            f'<p style="text-align:center;font-size:9pt;color:#555555"><i>{texto}</i></p>')


def fuente(texto):
    return f'<p style="font-size:9pt;color:#555555">{texto}</p>'


IND = {i["codigo"]: i for i in D["indicadores"]}


def valor(codigo, version):
    v = IND[codigo][version]
    decimales = {"IE-03": 0, "IE-05": 2, "IE-06": 1, "IR-01": 1}.get(codigo, 2)
    return es(v, decimales)


def umbral(ficha):
    if ficha["verde"] == 0:
        return f"Verde = 0; ámbar ≤ {es(ficha['ambar'], 0)}; rojo fuera de esos límites"
    signo = "≤" if ficha["sentido"] == F.MENOR_MEJOR else "≥"
    dec = 0 if ficha["codigo"] == "IE-03" else (1 if ficha["verde"] % 1 else 0)
    return (f"Verde {signo} {es(ficha['verde'], dec)}; ámbar {signo} {es(ficha['ambar'], dec)}; "
            f"rojo fuera de esos límites")


ficha_ic01 = next(f for f in F.FICHAS if f["codigo"] == "IC-01")
calidad = [f for f in F.FICHAS if f["grupo"] == "Calidad"]
eficiencia = [f for f in F.FICHAS if f["grupo"] == "Eficiencia"]

t1, t2 = E1["tiempo_s"], E2["tiempo_s"]
curva1 = {p["n"]: p["mediana_s"] for p in E1["curva"]}
curva2 = {p["n"]: p["mediana_s"] for p in E2["curva"]}
total_hallazgos = len(D["issue_log_v0.1"])
cwe_distintos = len(D["hallazgos_por_cwe_v0.1"])
tam1, tam2 = D["tamano"]["v0.1"], D["tamano"]["v0.2"]
cob = D["cobertura_5055"]

html = []
w = html.append

# ---------------------------------------------------------------- Caratula
w('<html><head><meta charset="utf-8">' + ESTILOS + '</head><body style="font-family:Arial;font-size:11pt">')
w('<p style="text-align:center"><img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/LOGO_UNSA.png" width="430"></p>')
w('<p style="text-align:center;font-size:13pt;color:#7A1F2B"><b>FACULTAD DE INGENIERÍA DE PRODUCCIÓN Y SERVICIOS</b></p>')
w('<p style="text-align:center;font-size:12pt;color:#4B5563"><b>ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS</b></p>')
w('<p style="text-align:center;font-size:11pt">&nbsp;</p>')
w('<p style="text-align:center;font-size:12pt">Curso: <b>CALIDAD DE SOFTWARE</b> (Teoría)</p>')
w('<p style="text-align:center;font-size:12pt">TRABAJO PARCIAL N.° 5</p>')
w('<p style="text-align:center;font-size:11pt">&nbsp;</p>')
w('<p style="text-align:center;font-size:17pt;color:#7A1F2B"><b>Aplicación de las normas ISO/IEC 20246:2017 e ISO/IEC 5055:2021 '
  'al proyecto de salud pública VigiSalud Arequipa</b></p>')
w('<p style="text-align:center;font-size:12pt;color:#4B5563">Indicadores de calidad y eficiencia del código, '
  'y herramienta para su captura, proceso y presentación</p>')
w('<p style="text-align:center;font-size:11pt">&nbsp;</p>')
w('<p style="text-align:center;font-size:11pt"><b>Docente:</b> [Nombre del docente]</p>')
w('<p style="text-align:center;font-size:11pt"><b>Integrantes:</b></p>')
w(f'<table style="border-collapse:collapse;width:80%;margin-left:auto;margin-right:auto"><tr>'
  f'<th {TH}>N.°</th><th {TH}>Apellidos y nombres</th><th {TH}>CUI</th><th {TH}>Responsabilidad en el TP5</th></tr>'
  + "".join(f'<tr><td {TD}>{n}</td><td {TD}>[Apellidos y nombres]</td><td {TD}>[CUI]</td><td {TD}>{r}</td></tr>'
            for n, r in enumerate(["Estructura de indicadores de calidad", "Indicadores de calidad del código",
                                   "Indicadores de eficiencia del código", "Herramienta de medición",
                                   "Presentación de resultados"], start=1))
  + '</table>')
w('<p style="text-align:center;font-size:11pt">&nbsp;</p>')
w('<p style="text-align:center;font-size:11pt">Semestre 2026-B · Grupo [ ]</p>')
w('<p style="text-align:center;font-size:11pt">Arequipa, Perú · octubre de 2026</p>')

# ---------------------------------------------------------------- Contenido
w('<h1 style="page-break-before:always">Contenido</h1>')
w("<ol>" + "".join(f"<li>{s}</li>" for s in [
    "Resumen ejecutivo", "Introducción", "El proyecto VigiSalud Arequipa", "Marco normativo",
    "Adopción de la ISO/IEC 20246 en el proyecto",
    "Punto 1: Estructura de indicadores para medir la calidad del código",
    "Punto 2: Indicadores de eficiencia del código",
    "Punto 3: Herramienta para la captura, el proceso y la presentación de indicadores",
    "Resultados de la aplicación", "Limitaciones", "Conclusiones y recomendaciones",
    "Distribución del trabajo en el equipo", "Referencias", "Anexos"]) + "</ol>")
w('<p style="font-size:9pt;color:#555555">Para un índice con números de página: Insertar &gt; Tabla de contenido.</p>')

# ---------------------------------------------------------------- Resumen
w('<h1 style="page-break-before:always">Resumen ejecutivo</h1>')
w("<p>Proponemos que el proyecto VigiSalud Arequipa revise su código fuente durante todo el curso con una "
  "<b>revisión técnica basada en la ISO/IEC 20246</b>, cuyos criterios de entrada y salida dependan de "
  "<b>13 indicadores</b>: seis de calidad y uno de eficiencia derivados de las medidas automatizadas de la "
  "<b>ISO/IEC 5055</b>, cinco indicadores de eficiencia medidos en ejecución y uno del propio proceso de "
  "revisión. La medición se automatiza con una cadena de herramientas libre (Radon, Pylint, Bandit, detectores "
  "propios sobre el árbol sintáctico de Python, cProfile y tracemalloc) que deja los resultados en un archivo JSON "
  "y los presenta en un dashboard web.</p>")
w(f"<p>Aplicamos la propuesta al prototipo inicial del sistema (v0.1, {tam1['sloc']} líneas de código fuente). "
  f"La revisión registró <b>{total_hallazgos} ocurrencias de debilidades ISO 5055</b> de {cwe_distintos} tipos CWE "
  f"distintos: recursos que no se liberan, consultas SQL armadas por concatenación, consultas dentro de bucles y "
  f"búsquedas secuenciales, entre otras. Procesar 20 000 notificaciones tomaba {es(t1)} s, por encima del "
  f"requisito de 2 s, y el tiempo crecía más rápido que la carga ({es(curva1[40000])} s con 40 000). Tras "
  f"corregir los hallazgos, la versión v0.2 no presenta debilidades detectables por la herramienta, procesa la "
  f"misma carga en <b>{es(t2)} s ({round(t1 / t2)} veces más rápido)</b> con resultados funcionales idénticos, "
  f"y sus 13 indicadores quedan en verde.</p>")
w("<p>El valor cero se refiere a las debilidades que la cadena de herramientas puede detectar: cubre "
  f"{cob['ASCMM']['cubiertos']} de los 29 CWE de mantenibilidad, {cob['ASCPEM']['cubiertos']} de 18 de eficiencia, "
  f"{cob['ASCRM']['cubiertos']} de 74 de fiabilidad y {cob['ASCSM']['cubiertos']} de 73 de seguridad. Gran parte de "
  "los CWE no cubiertos describen fallas de memoria propias de C y C++ que no ocurren en Python. Recomendamos "
  "ejecutar la medición en cada entrega del proyecto y ampliar los detectores conforme crezca el sistema.</p>")

# ---------------------------------------------------------------- Introduccion
w("<h1>Introducción</h1>")
w("<p>El docente del curso pidió desarrollar, durante todo el semestre, un proyecto de software orientado a la "
  "salud pública. Este Trabajo Parcial 5 es el primer paso de ese proyecto en materia de calidad del producto: "
  "antes de que el código crezca, el equipo define cómo lo va a revisar, qué va a medir y con qué herramienta.</p>")
w("<p>La ISO/IEC 20246:2017 establece un marco genérico para revisar productos de trabajo, como el código fuente, "
  "en cualquier fase del ciclo de vida. La ISO/IEC 5055:2021 define cuatro medidas automatizadas de la calidad "
  "estructural del código fuente a partir del conteo de debilidades graves catalogadas en la Common Weakness "
  "Enumeration (CWE). Usadas juntas, la primera aporta el proceso y la segunda la evidencia objetiva con la que "
  "ese proceso toma decisiones.</p>")
w("<h2>Objetivo general</h2>")
w("<p>Revisar, seleccionar y adoptar las características de las normas ISO/IEC 20246:2017 e ISO/IEC 5055:2021 "
  "en el proyecto VigiSalud Arequipa para medir la calidad y la eficiencia de su código fuente.</p>")
w("<h2>Objetivos específicos</h2>")
w("<ol><li>Seleccionar una estructura de indicadores para medir la calidad del código y definir con ella los "
  "indicadores de calidad.</li><li>Revisar y adoptar indicadores para medir la eficiencia del código.</li>"
  "<li>Seleccionar una herramienta para capturar la información, procesarla y presentar los indicadores, y "
  "aplicarla al prototipo del proyecto.</li></ol>")
w("<h2>Alcance</h2>")
w("<p>El trabajo cubre el código Python del núcleo de procesamiento de VigiSalud (lectura, validación, "
  "almacenamiento, indicadores epidemiológicos, alertas y reportes). No cubre la interfaz web ni la "
  "infraestructura, que se construirán en etapas posteriores. Los datos usados para medir la eficiencia son "
  "sintéticos y no contienen información de pacientes.</p>")

# ---------------------------------------------------------------- Proyecto
w("<h1>El proyecto VigiSalud Arequipa</h1>")
w("<p>La vigilancia epidemiológica depende de que los establecimientos de salud notifiquen cada semana los casos "
  "de enfermedades de notificación obligatoria y de que esa información se convierta a tiempo en alertas. En el "
  "primer nivel de atención este trabajo todavía se apoya en hojas de cálculo y consolidados manuales, lo que "
  "retrasa la detección de brotes de dengue, infecciones respiratorias agudas (IRA) y enfermedades diarreicas "
  "agudas (EDA).</p>")
w("<p><b>VigiSalud Arequipa</b> es un sistema que recibe las notificaciones semanales de los establecimientos de "
  "una red de salud, las valida, calcula indicadores epidemiológicos (tasa de incidencia por 100 000 habitantes, "
  "letalidad y distribución por etapa de vida), construye el canal endémico de cada distrito con los cinco años "
  "anteriores y genera alertas cuando los casos de la semana superan el tercer cuartil histórico. Sus usuarios "
  "son el personal de epidemiología de la red y de los establecimientos.</p>")
w(tabla(["Módulo", "Responsabilidad"], [
    ["datos", "Lectura del archivo de notificaciones y datos de población por distrito"],
    ["validacion", "Reglas de calidad del dato: catálogos, rangos, fechas y duplicados"],
    ["repositorio", "Almacenamiento y consultas en la base de datos SQLite"],
    ["indicadores", "Incidencia, letalidad y distribución por etapa de vida"],
    ["alertas", "Canal endémico (cuartiles de 5 años) y alertas tempranas; envío por correo"],
    ["reportes", "Reporte semanal en HTML"],
    ["pipeline", "Orquesta el procesamiento semanal completo"],
    ["config, modelos", "Configuración y entidades del dominio (Notificación, Alerta)"],
]))
w(fuente("Tabla 1. Módulos del prototipo de VigiSalud (Python 3.12, biblioteca estándar y SQLite)."))
w("<p>El sistema maneja datos personales de salud, que la Ley N.° 29733 de Protección de Datos Personales "
  "clasifica como datos sensibles. Por eso la seguridad del código y la fiabilidad de las alertas forman parte de "
  "los criterios de aceptación del producto, junto con la mantenibilidad y la eficiencia.</p>")

# ---------------------------------------------------------------- Marco normativo
w("<h1>Marco normativo</h1>")
w("<h2>ISO/IEC 20246:2017, revisiones de productos de trabajo</h2>")
w("<p>La norma define un proceso genérico de revisión que puede aplicarse de manera formal o informal a "
  "cualquier producto de trabajo, desde un plan de proyecto hasta el código fuente. Su propósito es ofrecer un "
  "marco estructurado pero flexible, que cada organización configura según el objetivo de la revisión (cláusula "
  "6.2). El proceso tiene cinco actividades:</p>")
w(tabla(["Actividad (cláusula)", "Tareas principales"], [
    ["Planificación (6.4.1)", "Definir alcance, producto a revisar, características de calidad a evaluar, "
     "criterios de salida, esfuerzo y plazos; acordar las características de la revisión y los participantes."],
    ["Inicio de la revisión (6.4.2)", "Distribuir materiales (producto, listas de verificación, guías) y "
     "comunicar alcance, roles y responsabilidades."],
    ["Revisión individual (6.4.3)", "Cada revisor identifica problemas en el producto y los registra."],
    ["Comunicación y análisis de problemas (6.4.4)", "Comunicar los problemas, asignarles estado y responsable, "
     "evaluar las características de calidad y tomar la decisión de la revisión."],
    ["Corrección y reporte (6.4.5)", "Corregir, confirmar las correcciones, aceptar el producto cuando se cumple "
     "la decisión y reportar los resultados."],
]))
w(fuente("Tabla 2. Actividades del proceso de revisión de la ISO/IEC 20246:2017."))
w("<p>La norma reconoce nueve tipos de revisión (verificación del autor, verificación por un colega, revisión "
  "grupal informal, inspección, revisión de hito, revisión en pareja, verificación de escritorio, revisión técnica "
  "y recorrido o <i>walkthrough</i>) y técnicas de revisión individual: ad hoc, basada en listas de verificación, "
  "basada en escenarios, lectura basada en perspectivas y basada en roles. Los productos de información que exige "
  "son el registro de problemas (<i>Issue Log</i>), el informe de incidentes y el informe de revisión (cláusula "
  "6.5). Admite conformidad completa o adaptada; en la adaptada se registran y justifican las decisiones de "
  "adaptación (cláusula 4.3).</p>")
w("<h2>ISO/IEC 5055:2021, medidas automatizadas de calidad del código fuente</h2>")
w("<p>La norma mide cuatro características de la ISO/IEC 25010 directamente en el código fuente. Cada medida "
  "se calcula contando las ocurrencias de debilidades graves (CWE) que afectan a esa característica y sumándolas; "
  "una misma debilidad puede pertenecer a varias medidas. La norma aclara que son medidas correlacionadas y no "
  "absolutas: no cuentan todas las debilidades posibles, sino las que un grupo internacional de expertos consideró "
  "más severas.</p>")
w(tabla(["Medida", "Característica ISO/IEC 25010", "Debilidades CWE", "Ejemplos"], [
    ["ASCMM", "Mantenibilidad", "29", "CWE-1121 complejidad de McCabe excesiva, CWE-1041 código duplicado, CWE-561 código muerto"],
    ["ASCPEM", "Eficiencia de desempeño", "18", "CWE-1046 concatenación de texto, CWE-1067 búsquedas secuenciales, CWE-772 recurso no liberado"],
    ["ASCRM", "Fiabilidad", "74", "CWE-703 manejo incorrecto de excepciones, CWE-369 división por cero, CWE-1088 sin tiempo límite"],
    ["ASCSM", "Seguridad", "73", "CWE-89 inyección SQL, CWE-798 credenciales en el código, CWE-22 recorrido de rutas"],
], numericas=(2,)))
w(fuente("Tabla 3. Medidas de la ISO/IEC 5055:2021 (cláusula 7). Conteos tomados de la lista de debilidades de la norma."))
w("<p>Para declarar conformidad, una implementación debe ser <b>automatizada</b> (el análisis y el conteo no "
  "requieren intervención humana), <b>objetiva</b> (repite los mismos resultados sobre el mismo código), "
  "<b>transparente</b> (lista el código y los artefactos analizados) y <b>verificable</b> (documenta sus supuestos y "
  "heurísticas para que un tercero pueda comprobar el cálculo). La norma complementa a la ISO/IEC 25023, cuyas "
  "medidas son mayormente de comportamiento externo.</p>")
w("<h2>Cómo se complementan</h2>")
w("<p>La ISO/IEC 20246 indica que, como resultado de una revisión, las características de calidad del producto "
  "quedan evaluadas y remite a la serie ISO/IEC 25000. La ISO/IEC 5055 aporta, para el código fuente, la forma "
  "objetiva de hacer esa evaluación. En VigiSalud los indicadores se usan dentro de las actividades de la revisión:</p>")
w(tabla(["Actividad ISO/IEC 20246", "Uso de los indicadores ISO/IEC 5055 en VigiSalud"], [
    ["Planificación", "Las características a evaluar son las cuatro medidas de la ISO 5055; los criterios de salida son umbrales de los indicadores."],
    ["Inicio", "La lista de verificación es el catálogo de CWE mapeado a reglas de las herramientas; se entregan las fichas de indicadores."],
    ["Revisión individual", "La herramienta detecta las debilidades y mide la eficiencia; el revisor confirma o descarta cada hallazgo."],
    ["Comunicación y análisis", "El Issue Log se analiza por CWE y severidad; el semáforo de los indicadores sustenta la decisión."],
    ["Corrección y reporte", "Se vuelve a medir la versión corregida; el indicador IR-01 confirma el cierre y se emite el informe de revisión."],
]))
w(fuente("Tabla 4. Integración de ambas normas en el proceso de revisión del proyecto."))

# ---------------------------------------------------------------- Adopcion 20246
w("<h1>Adopción de la ISO/IEC 20246 en el proyecto</h1>")
w("<p>Elegimos una <b>revisión técnica</b> (revisión formal por personal técnicamente calificado que examina si "
  "el producto es adecuado para su uso y detecta discrepancias con especificaciones y estándares), con dos técnicas "
  "de revisión individual: <b>basada en listas de verificación</b>, donde la lista es el conjunto de CWE de la "
  "ISO 5055 que la herramienta detecta, y <b>basada en roles</b>, donde cada revisor examina el código desde una "
  "característica de calidad. Se descartó la inspección porque exige un proceso de mejora y métricas del propio "
  "proceso que el equipo aún no tiene, y el recorrido porque lo conduce el autor y favorece la comprensión antes "
  "que la detección.</p>")
w(tabla(["Rol ISO/IEC 20246", "Integrante", "Función en VigiSalud"], [
    ["Líder de revisión", "Integrante 1", "Planifica, define la estructura de indicadores y los criterios de salida"],
    ["Revisor de calidad", "Integrante 2", "Revisa mantenibilidad, fiabilidad y seguridad (IC-01 a IC-06)"],
    ["Revisor de eficiencia", "Integrante 3", "Revisa eficiencia estática y dinámica (IE-01 a IE-06)"],
    ["Responsable de la herramienta", "Integrante 4", "Opera la herramienta y mantiene el mapeo regla-CWE"],
    ["Registrador (escriba)", "Integrante 5", "Mantiene el Issue Log, el informe de revisión y el dashboard"],
    ["Autor", "Equipo de desarrollo", "Corrige los hallazgos con estado «a corregir»"],
]))
w(fuente("Tabla 5. Roles de la revisión y su asignación en el equipo."))
w("<p><b>Criterios de entrada:</b> el código compila, la versión está etiquetada y existen las fichas de "
  "indicadores. <b>Criterios de salida:</b> ningún indicador en rojo; IC-03 (seguridad) igual a cero; IE-02 dentro "
  "del requisito de 2 s; IR-01 de al menos 90 %. Las salidas posibles de la decisión son las que propone la norma: "
  "usar tal cual, actualizar y usar, rehacer y volver a revisar, o descartar.</p>")
w("<p><b>Conformidad declarada:</b> conformidad adaptada (cláusula 4.3). Se aplican las cinco actividades y se "
  "producen el Issue Log y el informe de revisión. El informe de incidentes se emite solo cuando un hallazgo exige "
  "cambiar un artefacto distinto del código revisado; en este ciclo hubo un caso: el requisito no funcional de "
  "tiempo de respuesta, que se documentó como incidente sobre la especificación de requisitos.</p>")

# ---------------------------------------------------------------- Punto 1
w("<h1>Punto 1: Estructura de indicadores para medir la calidad del código</h1>")
w("<h2>Modelo jerárquico</h2>")
w("<p>La estructura sigue el modelo de información de medición de la ISO/IEC 15939, que también usa la serie "
  "ISO/IEC 25000: las <b>medidas base</b> se obtienen del código, una <b>función de medición</b> las combina, el "
  "resultado es un <b>indicador</b> y un <b>criterio de decisión</b> lo interpreta. Sobre ese modelo se agregan "
  "los niveles de las normas del trabajo:</p>")
w("<ol><li><b>Característica de calidad</b> (ISO/IEC 25010): mantenibilidad, fiabilidad, seguridad, eficiencia de desempeño.</li>"
  "<li><b>Medida ISO/IEC 5055</b>: ASCMM, ASCRM, ASCSM o ASCPEM.</li>"
  "<li><b>Indicador</b> del proyecto, con código (IC para calidad, IE para eficiencia, IR para el proceso de revisión).</li>"
  "<li><b>Medida base</b>: ocurrencias de un CWE, líneas de código, tiempo, memoria.</li>"
  "<li><b>Fuente</b>: herramienta y regla que captura la medida base.</li></ol>")
w("<h2>Ficha de indicador</h2>")
w("<p>Cada indicador se documenta en una ficha con los mismos campos. La ficha vive como dato en el archivo "
  "<i>medicion/fichas.py</i>, de modo que la herramienta, el dashboard y este informe usan exactamente la misma "
  "definición.</p>")
w(tabla(["Campo", "Contenido"], [
    ["Código y nombre", "Identificador único y nombre corto"],
    ["Característica y medida ISO 5055", "Característica ISO/IEC 25010 y medida automatizada a la que aporta"],
    ["CWE asociados", "Debilidades de la norma que alimentan el indicador"],
    ["Pregunta", "Qué decisión ayuda a tomar (enfoque objetivo-pregunta-métrica)"],
    ["Medidas base", "Datos crudos que se capturan"],
    ["Función de medición", "Fórmula que produce el indicador"],
    ["Unidad y escala", "Unidad de medida y tipo de escala (razón, intervalo)"],
    ["Herramienta", "Herramienta y regla que capturan las medidas base"],
    ["Momento", "Actividad de la ISO/IEC 20246 en la que se usa"],
    ["Sentido y umbrales", "Si es mejor menor o mayor; límites verde y ámbar"],
    ["Interpretación", "Qué significa un valor alto o bajo en VigiSalud"],
    ["Responsable", "Rol que vigila el indicador"],
]))
w(fuente("Tabla 6. Campos de la ficha de indicador."))
w("<h2>Criterio de decisión</h2>")
w("<p>Todos los indicadores usan un semáforo de tres niveles: <span style=\"color:#1B7F3B;font-weight:bold\">verde</span> "
  "cumple el objetivo; <span style=\"color:#A15C00;font-weight:bold\">ámbar</span> es aceptable con justificación y "
  "plan de mejora; <span style=\"color:#B3261E;font-weight:bold\">rojo</span> bloquea la aceptación del producto en la "
  "revisión. Las densidades se normalizan por mil líneas de código fuente (KSLOC) para comparar versiones de "
  "distinto tamaño; la ISO 5055 permite normalizar por tamaño y sugiere los puntos de función automatizados, que "
  "reemplazamos por KSLOC por simplicidad.</p>")
w("<h2>Indicadores de calidad seleccionados</h2>")
w("<p>Se adoptaron las tres medidas de la ISO 5055 que corresponden a la calidad estructural (mantenibilidad, "
  "fiabilidad y seguridad) expresadas como densidades, y tres indicadores que explican por qué cambia la "
  "mantenibilidad. Cada uno responde a una pregunta del equipo:</p>")
w(tabla(["Código", "Indicador", "Función de medición", "Unidad", "Umbrales", "Herramienta"],
        [[f["codigo"], f["nombre"], f["formula"], f["unidad"], umbral(f), f["herramienta"]] for f in calidad]))
w(fuente("Tabla 7. Indicadores de calidad del código (IC). SLOC: líneas de código fuente sin comentarios ni líneas en blanco."))
w("<p><b>Por qué estos indicadores.</b> IC-01 a IC-03 son las medidas de la norma y permiten comparar VigiSalud "
  "con cualquier otro sistema medido con la ISO 5055. IC-04 apunta a CWE-1121, la debilidad con más impacto en la "
  "capacidad de prueba: una función con complejidad ciclomática mayor que 10 necesita más de diez casos de prueba "
  "para cubrir sus caminos (McCabe, 1976). IC-05 resume la mantenibilidad de cada módulo con el índice de "
  "Oman y Hagemeister (1992) escalado de 0 a 100 por Radon; sus umbrales de 50 y 38 equivalen a los clásicos 85 y "
  "65 de la escala original. IC-06 mide CWE-1041, porque el código duplicado hace que un error corregido en un "
  "lugar siga presente en otro. Se fijó IC-03 en cero porque el sistema maneja datos sensibles.</p>")
w("<h2>Ejemplo de ficha completa: IC-01</h2>")
w(tabla(["Campo", "Valor"], [[k, ficha_ic01[c]] for k, c in [
    ("Código", "codigo"), ("Nombre", "nombre"), ("Característica", "caracteristica"),
    ("Medida ISO 5055", "medida_5055"), ("CWE asociados", "cwe"), ("Pregunta", "pregunta"),
    ("Medidas base", "medidas_base"), ("Función de medición", "formula"), ("Unidad", "unidad"),
    ("Escala", "escala"), ("Herramienta", "herramienta"), ("Momento ISO 20246", "momento"),
    ("Sentido", "sentido"), ("Interpretación", "interpretacion"), ("Responsable", "responsable")]]
    + [["Umbrales", umbral(ficha_ic01)]]))
w(fuente("Tabla 8. Ficha del indicador IC-01."))

# ---------------------------------------------------------------- Punto 2
w("<h1>Punto 2: Indicadores de eficiencia del código</h1>")
w("<p>La eficiencia se mide desde dos lados. La ISO 5055 mide la causa: patrones de código que desperdician "
  "tiempo o recursos (medida ASCPEM, 18 CWE). La ISO/IEC 25010 describe el efecto en sus subcaracterísticas "
  "comportamiento temporal, utilización de recursos y capacidad, que solo pueden observarse ejecutando el "
  "sistema. Adoptamos ambos para que cada hallazgo estático tenga una consecuencia medible.</p>")
w("<h2>Debilidades de eficiencia de la ISO 5055 aplicables a Python</h2>")
w(tabla(["CWE", "Debilidad", "Cómo aparece en Python", "Corrección típica"], [
    ["CWE-1046", "Texto inmutable creado por concatenación", "<i>html += ...</i> dentro de un bucle", "Acumular en una lista y unir con <i>\"\".join()</i>"],
    ["CWE-1067", "Búsquedas secuenciales excesivas", "<i>if x in lista</i> dentro de un bucle; búsqueda lineal en listas de diccionarios", "Usar <i>set</i> o <i>dict</i> (acceso promedio constante)"],
    ["CWE-1050", "Consumo de recursos de plataforma dentro de un bucle", "<i>execute()</i> o <i>open()</i> en cada iteración", "Operaciones por lote (<i>executemany</i>)"],
    ["CWE-1060", "Exceso de accesos a datos en el servidor", "Una consulta por distrito, enfermedad y semana", "Una consulta agregada con <i>GROUP BY</i> e índice"],
    ["CWE-1072", "Acceso a datos sin reutilizar conexiones", "<i>sqlite3.connect()</i> en cada función", "Una conexión gestionada por el repositorio"],
    ["CWE-772 / 775", "Recurso o archivo no liberado", "Conexión o archivo abiertos sin <i>with</i> ni <i>close()</i>", "Gestores de contexto (<i>with</i>)"],
    ["CWE-1057", "Acceso a datos fuera del gestor de datos", "SQL ejecutado en el módulo de reportes", "Concentrar el SQL en el repositorio"],
]))
w(fuente("Tabla 9. Debilidades ASCPEM detectadas por la herramienta y su forma en Python."))
w("<h2>Indicadores de eficiencia seleccionados</h2>")
w(tabla(["Código", "Indicador", "Función de medición", "Unidad", "Umbrales", "Herramienta"],
        [[f["codigo"], f["nombre"], f["formula"], f["unidad"], umbral(f), f["herramienta"]] for f in eficiencia]))
w(fuente("Tabla 10. Indicadores de eficiencia del código (IE)."))
w("<p><b>Qué significan sus valores.</b> IE-01 es la densidad de causas estáticas y debería moverse junto con los "
  "indicadores dinámicos. IE-02 se compara con el requisito no funcional del proyecto: el reporte y las alertas de "
  "la semana deben estar listos en 2 s para la carga de referencia de 20 000 notificaciones. IE-03 expresa lo mismo "
  "como capacidad y sirve para dimensionar picos durante un brote. IE-04 vigila la memoria, escasa en los "
  "servidores del primer nivel. IE-05 es el exponente <i>b</i> del ajuste t = a·N<sup>b</sup>: un valor cercano a 1 "
  "indica crecimiento lineal, y uno cercano a 2, un costo cuadrático relacionado con CWE-407 (complejidad "
  "algorítmica). IE-06 dice qué parte del tiempo consume la función más costosa: sobre 50 % hay un único punto a "
  "corregir primero.</p>")
w("<h2>Protocolo de medición</h2>")
w("<ol><li>Datos sintéticos reproducibles (semilla fija) de 2021 a 2026, con estacionalidad por enfermedad, un brote "
  "simulado de dengue, 2 % de filas con errores y 1 % de duplicados.</li>"
  "<li>Cargas de 2 500, 5 000, 10 000, 20 000 y 40 000 notificaciones; la de 20 000 es la de referencia.</li>"
  "<li>Cada ejecución corre en un proceso nuevo y con la base de datos recreada; se informa la mediana de 5 "
  "ejecuciones para la carga de referencia y de 3 para las demás.</li>"
  "<li>La memoria se mide en una ejecución separada con <i>tracemalloc</i> y el perfil con <i>cProfile</i>, porque "
  "ambos alteran el tiempo.</li>"
  f"<li>Entorno: Python {E1['entorno']['python']} sobre Windows 11, procesador Intel de 64 bits. Los valores "
  "absolutos dependen del equipo; las comparaciones entre versiones se hacen siempre en el mismo equipo.</li>"
  "<li>Antes de comparar, se verifica que ambas versiones producen el mismo resumen funcional (casos válidos, "
  "rechazados, alertas, letalidad y grupos de edad).</li></ol>")
ir = next(f for f in F.FICHAS if f["codigo"] == "IR-01")
w("<h2>Indicador del proceso de revisión</h2>")
w(f"<p>Para cerrar el ciclo de la ISO/IEC 20246 se agrega <b>{ir['codigo']} {ir['nombre']}</b>: "
  f"{ir['formula']}. Un hallazgo se considera resuelto cuando su CWE ya no aparece en el mismo módulo de la nueva "
  f"versión. Es el criterio de salida de la actividad de corrección y reporte ({umbral(ir).lower()}).</p>")

# ---------------------------------------------------------------- Punto 3
w("<h1>Punto 3: Herramienta para la captura, el proceso y la presentación de indicadores</h1>")
w("<h2>Criterios y alternativas evaluadas</h2>")
w("<p>La herramienta debía analizar Python, relacionar cada hallazgo con un CWE de la ISO 5055, medir también la "
  "eficiencia en ejecución, ser gratuita, poder automatizarse en integración continua y cumplir los cuatro "
  "requisitos de conformidad de la norma (automatizada, objetiva, transparente y verificable).</p>")
w(tabla(["Criterio", "SonarQube Community Build", "CAST AIP / Highlight", "Cadena propuesta (QMeter VigiSalud)"], [
    ["Soporte de Python", "Sí", "Sí", "Sí"],
    ["Relación con CWE de la ISO 5055", "Reglas etiquetadas con CWE, centradas en seguridad", "Implementa las medidas CISQ/ISO 5055", "Mapeo explícito regla-CWE en <i>iso5055.py</i>"],
    ["Eficiencia en ejecución", "No", "No (análisis estático)", "Sí: tiempo, memoria, escalabilidad y perfil"],
    ["Costo", "Libre", "Comercial", "Libre"],
    ["Integración continua", "Sí (requiere servidor)", "Sí", "Sí (un comando; GitHub Actions)"],
    ["Presentación", "Portal web propio", "Portal web propio", "JSON, dashboard web e Issue Log"],
    ["Transparencia del cálculo", "Parcial", "Parcial (propietario)", "Total: código, mapeo y supuestos documentados"],
    ["Esfuerzo de puesta en marcha", "Medio (Java, base de datos o Docker)", "Alto (licencia y despliegue)", "Bajo (pip install)"],
]))
w(fuente("Tabla 11. Comparación de alternativas de herramienta."))
w("<p><b>Herramienta seleccionada:</b> una cadena de herramientas libres orquestada por scripts del proyecto, a la "
  "que llamamos <b>QMeter VigiSalud</b>. Se eligió porque es la única alternativa que cubre los indicadores "
  "estáticos y dinámicos, porque su cálculo es completamente verificable (requisito de la cláusula 2 de la ISO "
  "5055) y porque no exige servidores. SonarQube queda como complemento recomendado cuando el proyecto tenga un "
  "servidor de integración continua.</p>")
w("<h2>Arquitectura: captura, proceso y presentación</h2>")
w(tabla(["Etapa", "Componentes", "Salida"], [
    ["Captura estática", "Radon 6.0.1 (complejidad, índice de mantenibilidad, tamaño), Pylint 4.1.3 y Bandit 1.9.4 "
     "con reglas mapeadas a CWE, y 13 detectores propios sobre el árbol sintáctico (<i>detectores.py</i>)",
     "Hallazgos por módulo, línea y regla"],
    ["Captura dinámica", "Generador de datos sintéticos, <i>time.perf_counter</i>, <i>tracemalloc</i> y <i>cProfile</i> "
     "en procesos aislados (<i>medir_eficiencia.py</i>)", "Tiempos por carga, memoria pico y funciones más costosas"],
    ["Proceso", "Mapeo regla-CWE-medida, eliminación de duplicados por (módulo, línea, CWE), densidades por KSLOC, "
     "regresión log-log, semáforo según fichas (<i>medir_calidad.py</i>, <i>consolidar.py</i>)", "<i>resultados/indicadores.json</i>"],
    ["Presentación", "Dashboard web con scorecard, gráficos e Issue Log; tablas y gráficos de este informe",
     "Dashboard publicado e informe"],
]))
w(fuente("Tabla 12. Etapas de la herramienta."))
w("<p>Los detectores propios cubren debilidades de la norma que Pylint y Bandit no detectan en Python: excepción "
  "capturada sin acción (CWE-390), concatenación en bucle (CWE-1046), búsquedas secuenciales (CWE-1067), "
  "consultas y recursos dentro de bucles (CWE-1050 y CWE-1060), recursos sin liberar (CWE-772 y CWE-775), "
  "conexiones sin reutilizar (CWE-1072), SQL fuera del repositorio (CWE-1057), red sin tiempo límite (CWE-1088), "
  "direcciones de red y credenciales en el código (CWE-1051 y CWE-798, reconociendo nombres en español como "
  "<i>CLAVE</i>), división sin control de cero (CWE-369) y código comentado (CWE-1085). El Anexo A lista el mapeo "
  "completo.</p>")
w("<h2>Ejecución</h2>")
w('<p style="font-family:Courier New;font-size:9.5pt;background-color:#F3F4F6">python -m venv .venv<br>'
  ".venv\\Scripts\\pip install -r requirements.txt<br>"
  ".venv\\Scripts\\python medicion\\medir_todo.py</p>")
w("<p>El último comando mide las dos versiones, verifica que producen los mismos resultados funcionales y deja el "
  "consolidado en <i>resultados/indicadores.json</i>. La medición completa tarda unos tres minutos, casi todo en el "
  "benchmark de la versión v0.1.</p>")

# ---------------------------------------------------------------- Resultados
w("<h1>Resultados de la aplicación</h1>")
w(f"<p>La herramienta se aplicó al prototipo inicial v0.1 ({tam1['sloc']} SLOC, {tam1['funciones']} funciones, "
  f"{tam1['modulos']} módulos) y, tras corregir los hallazgos, a la versión v0.2 ({tam2['sloc']} SLOC, "
  f"{tam2['funciones']} funciones, {tam2['modulos']} módulos).</p>")
w("<h2>Indicadores de la línea base y de la versión corregida</h2>")
w(tabla(["Código", "Indicador", "Unidad", "v0.1", "Estado", "v0.2", "Estado"],
        [[i["codigo"], i["nombre"], i["unidad"], valor(i["codigo"], "v0.1"), estado(i["semaforo_v0.1"]),
          valor(i["codigo"], "v0.2"), estado(i["semaforo_v0.2"])] for i in D["indicadores"]],
        numericas=(3, 5)))
w(fuente("Tabla 13. Valores medidos y semáforo de los 13 indicadores."))
w("<h2>Hallazgos de la revisión</h2>")
w(f"<p>La revisión de v0.1 registró {total_hallazgos} ocurrencias únicas de {cwe_distintos} CWE distintos. "
  f"Como una debilidad puede pertenecer a varias medidas, la eficiencia sumó "
  f"{D['conteos_5055']['v0.1']['ASCPEM']} ocurrencias, la fiabilidad {D['conteos_5055']['v0.1']['ASCRM']}, la "
  f"seguridad {D['conteos_5055']['v0.1']['ASCSM']} y la mantenibilidad {D['conteos_5055']['v0.1']['ASCMM']}. "
  "La eficiencia concentró más hallazgos porque el prototipo se escribió priorizando que funcione, con una "
  "conexión y una consulta por cada operación.</p>")
w(figura(G["medidas_es"], 520, "Figura 1. Ocurrencias de debilidades por medida ISO 5055 en v0.1 y v0.2."))
w(figura(G["cwe_es"], 520, "Figura 2. Hallazgos de v0.1 agrupados por CWE."))
w(f"<p>El efecto de CWE-772 se observó también en ejecución: v0.1 dejó la base de datos bloqueada en "
  f"{D['bd_bloqueada']['v0.1']} ejecuciones del benchmark, porque las conexiones quedaban abiertas al terminar; v0.2 "
  f"no la bloqueó en ninguna ({D['bd_bloqueada']['v0.2']}). La función más compleja de v0.1 era "
  f"<i>validar_notificacion</i>, con complejidad ciclomática {C1['complejidad']['maxima']}.</p>")
w("<h2>Correcciones aplicadas</h2>")
w(tabla(["Hallazgo (CWE)", "Corrección en v0.2"], [
    ["Recursos sin liberar y sin reutilizar conexiones (772, 775, 1072)", "Clase <i>Repositorio</i> con gestor de contexto y una sola conexión; archivos abiertos con <i>with</i>"],
    ["Inyección SQL (89)", "Consultas parametrizadas con marcadores <i>?</i>"],
    ["Consultas y operaciones dentro de bucles (1050, 1060)", "Una consulta agregada con <i>GROUP BY</i> e índice; inserción con <i>executemany</i>"],
    ["Búsquedas secuenciales (1067)", "Conjunto para detectar duplicados y diccionario para la población"],
    ["Concatenación de texto en bucle (1046)", "Lista de fragmentos unida con <i>\"\".join()</i>"],
    ["SQL fuera del repositorio (1057)", "Consulta de totales trasladada al repositorio"],
    ["Excepciones sin acción (390, 703)", "Captura de <i>TypeError</i> y <i>ValueError</i> con valor nulo y mensaje de error"],
    ["Complejidad excesiva y exceso de parámetros (1121, 1064)", "Reglas de validación en tablas; construcción con <i>Notificacion(**campos)</i>"],
    ["Código duplicado (1041)", "Clasificación del canal endémico en el módulo compartido <i>canal.py</i>"],
    ["Red, credenciales y tiempo límite (1051, 798, 1088)", "Configuración por variables de entorno, tiempo límite de 10 s y STARTTLS"],
    ["División sin control de cero (369)", "Guardas antes de cada división"],
    ["Código muerto y comentado (561, 1085)", "Eliminado"],
]))
w(fuente("Tabla 14. Correcciones derivadas del Issue Log."))
w("<h2>Eficiencia antes y después</h2>")
w(f"<p>Con la carga de referencia, v0.1 tardó {es(t1)} s y v0.2 {es(t2)} s. La diferencia crece con la carga: con "
  f"40 000 notificaciones v0.1 tardó {es(curva1[40000])} s y v0.2 {es(curva2[40000])} s. Entre 20 000 y 40 000 "
  f"notificaciones el tiempo de v0.1 se multiplicó por {es(curva1[40000] / curva1[20000], 1)} al duplicarse la carga, "
  "el comportamiento cuadrático de la búsqueda de duplicados en una lista (CWE-1067). En v0.1 el 51,6 % del tiempo se "
  "iba en ejecutar sentencias SQL una por una; en v0.2 la función más costosa es la propia validación, con el 21 %.</p>")
w(figura(G["escalabilidad_es"], 520, "Figura 3. Tiempo de procesamiento según la carga (escalas logarítmicas)."))
w("<h2>Análisis</h2>")
w("<ul>"
  f"<li>La memoria pico subió de {es(E1['memoria_pico_mb'])} MB a {es(E2['memoria_pico_mb'])} MB porque v0.2 carga "
  "las filas en lista para validarlas por lote. El aumento es menor al 10 % y queda dentro del umbral verde.</li>"
  f"<li>El exponente de v0.2 ({es(E2['exponente_escalabilidad'])}) es menor que 1 porque, con cargas pequeñas, "
  "pesan los costos fijos (crear la tabla y el índice). Con cargas mayores tiende a 1, es decir, a crecimiento lineal.</li>"
  f"<li>El índice de mantenibilidad global mejoró de {es(IND['IC-05']['v0.1'])} a {es(IND['IC-05']['v0.2'])}, "
  f"pero el módulo de validación sigue con {es(C2['mantenibilidad_mi']['por_modulo']['vigisalud.validacion']['mi'])} "
  "puntos, en ámbar a nivel de módulo. Es el primer candidato a simplificar en la siguiente iteración.</li>"
  "<li>Ambas versiones generan exactamente los mismos casos válidos, rechazos, alertas, letalidad y grupos de edad: "
  "las mejoras no cambiaron el comportamiento funcional.</li></ul>")
w("<p>El dashboard web presenta estos resultados con el scorecard de indicadores, los gráficos y el Issue Log "
  "filtrable: https://vigisalud-iso5055.vercel.app</p>")

# ---------------------------------------------------------------- Limitaciones
w("<h1>Limitaciones</h1>")
w("<ul><li>La herramienta no es una implementación certificada de la ISO 5055; mide un subconjunto de sus CWE "
  "con heurísticas documentadas. Un valor cero significa que no se detectaron debilidades de ese subconjunto.</li>"
  "<li>Algunos detectores pueden dar falsos positivos (por ejemplo, una división cuyo denominador nunca es cero "
  "pero no está protegida); por eso la revisión individual confirma cada hallazgo antes de darle estado.</li>"
  "<li>El prototipo es pequeño. Las densidades por KSLOC cambian mucho con pocas ocurrencias y se estabilizarán "
  "cuando el sistema crezca.</li>"
  "<li>Los tiempos dependen del equipo; los umbrales de IE-02 e IE-03 deben recalibrarse en el servidor de "
  "producción.</li></ul>")

# ---------------------------------------------------------------- Conclusiones
w("<h1>Conclusiones y recomendaciones</h1>")
w("<ol>"
  "<li>La ISO/IEC 20246 y la ISO/IEC 5055 se complementan: la primera da al equipo un proceso de revisión con "
  "roles, actividades y registros, y la segunda le da criterios objetivos y automatizables para decidir en ese "
  "proceso.</li>"
  "<li>La estructura de indicadores basada en el modelo de medición (medida base, función, indicador, criterio de "
  "decisión) y en fichas con umbrales permite que cualquier integrante calcule e interprete un indicador de la "
  "misma forma.</li>"
  "<li>Los indicadores de eficiencia funcionan mejor en pares: la densidad ASCPEM señala la causa y las medidas "
  f"dinámicas confirman el efecto. Corregir 22 ocurrencias de eficiencia redujo el tiempo de {es(t1)} s a {es(t2)} s.</li>"
  "<li>Una cadena de herramientas libres con mapeo explícito a CWE cumple los requisitos de automatización, "
  "objetividad, transparencia y verificabilidad de la ISO 5055 a bajo costo, y se ajusta a un proyecto de curso.</li>"
  "<li>Recomendamos ejecutar <i>medir_todo.py</i> en cada entrega, incorporarlo a la integración continua cuando el "
  "proyecto tenga repositorio remoto, simplificar el módulo de validación y ampliar los detectores a la capa web.</li>"
  "</ol>")

# ---------------------------------------------------------------- Distribucion
w("<h1>Distribución del trabajo en el equipo</h1>")
w(tabla(["Integrante", "Tema", "Sección del informe", "Entregable", "Diapositivas"], [
    ["Integrante 1", "Estructura de indicadores de calidad", "Punto 1: modelo, ficha y criterio de decisión", "Plantilla de ficha (<i>fichas.py</i>)", "1 a 6"],
    ["Integrante 2", "Indicadores de calidad del código", "Punto 1: indicadores IC-01 a IC-06", "Fichas IC", "7 y 8"],
    ["Integrante 3", "Indicadores de eficiencia del código", "Punto 2", "Fichas IE y protocolo de medición", "9 y 10"],
    ["Integrante 4", "Herramienta de medición", "Punto 3: selección y arquitectura", "QMeter VigiSalud", "11 y 12"],
    ["Integrante 5", "Presentación de resultados", "Resultados de la aplicación", "Dashboard web y tablas de resultados", "13 a 16"],
]))
w(fuente("Tabla 15. Responsabilidades. Las diapositivas 1 a 4 (portada, agenda, proyecto y normas) las presenta el Integrante 1 como introducción."))

# ---------------------------------------------------------------- Referencias
w("<h1>Referencias</h1>")
w("<ul>"
  "<li>International Organization for Standardization. (2017). <i>ISO/IEC 20246:2017 Software and systems engineering. Work product reviews</i>. ISO.</li>"
  "<li>International Organization for Standardization. (2021). <i>ISO/IEC 5055:2021 Information technology. Software measurement. Software quality measurement. Automated source code quality measures</i>. ISO.</li>"
  "<li>International Organization for Standardization. (2011). <i>ISO/IEC 25010:2011 Systems and software engineering. Systems and software Quality Requirements and Evaluation (SQuaRE). System and software quality models</i>. ISO.</li>"
  "<li>International Organization for Standardization. (2016). <i>ISO/IEC 25023:2016 Systems and software engineering. SQuaRE. Measurement of system and software product quality</i>. ISO.</li>"
  "<li>International Organization for Standardization. (2017). <i>ISO/IEC/IEEE 15939:2017 Systems and software engineering. Measurement process</i>. ISO.</li>"
  "<li>McCabe, T. J. (1976). A complexity measure. <i>IEEE Transactions on Software Engineering, SE-2</i>(4), 308-320.</li>"
  "<li>Oman, P., y Hagemeister, J. (1992). Metrics for assessing a software system's maintainability. En <i>Proceedings of the Conference on Software Maintenance</i> (pp. 337-344). IEEE.</li>"
  "<li>The MITRE Corporation. (s. f.). <i>Common Weakness Enumeration (CWE)</i>. https://cwe.mitre.org</li>"
  "<li>Congreso de la República del Perú. (2011). <i>Ley N.° 29733, Ley de Protección de Datos Personales</i>.</li>"
  "<li>Documentación de Radon (https://radon.readthedocs.io), Pylint (https://pylint.readthedocs.io), Bandit (https://bandit.readthedocs.io) y de los módulos cProfile y tracemalloc de Python (https://docs.python.org/3/library/).</li>"
  "</ul>")

# ---------------------------------------------------------------- Anexos
w("<h1>Anexos</h1>")
w("<h2>Anexo A. Mapeo de reglas de la herramienta a CWE de la ISO 5055</h2>")
w(tabla(["Herramienta y regla", "CWE", "Medidas"], [
    ["Radon: complejidad ciclomática mayor que 10", "1121", "ASCMM"],
    ["Pylint R0913 / R0917 (más de 7 parámetros)", "1064", "ASCMM"],
    ["Pylint R0801 duplicate-code (6 o más líneas)", "1041", "ASCMM"],
    ["Pylint W0101 unreachable", "561", "ASCMM"],
    ["Pylint W0125 using-constant-test", "570", "ASCMM, ASCSM"],
    ["Pylint R0401 cyclic-import", "1047", "ASCMM"],
    ["Pylint C0302 too-many-lines (más de 1000)", "1080", "ASCMM"],
    ["Pylint R0901 too-many-ancestors", "1074", "ASCMM"],
    ["Pylint W0702 / W0718 (except genérico); Bandit B110", "703", "ASCRM"],
    ["Pylint R1713 consider-using-join", "1046", "ASCPEM"],
    ["Bandit B608 (SQL armado con texto)", "89", "ASCSM"],
    ["Bandit B105 a B107 (contraseña en el código)", "259", "ASCSM"],
    ["Bandit B602 a B607 (comandos del sistema)", "78", "ASCSM"],
    ["Bandit B301 (pickle)", "502", "ASCSM"],
    ["Bandit B103 (permisos de archivo) / B310 (urlopen)", "732 / 22", "ASCSM"],
    ["Detector except-pass", "390", "ASCRM"],
    ["Detector str-concat-loop", "1046", "ASCPEM"],
    ["Detectores list-membership-loop y linear-search", "1067", "ASCPEM"],
    ["Detector resource-in-loop", "1050", "ASCPEM"],
    ["Detector query-in-loop", "1060", "ASCPEM"],
    ["Detector data-access-outside-dal", "1057", "ASCPEM, ASCSM"],
    ["Detector resource-not-released", "772 / 775", "ASCPEM, ASCRM, ASCSM"],
    ["Detector no-connection-reuse", "1072", "ASCPEM"],
    ["Detector remote-no-timeout", "1088", "ASCRM"],
    ["Detector hardcoded-network", "1051", "ASCMM, ASCRM"],
    ["Detector hardcoded-credential", "798", "ASCSM"],
    ["Detector unchecked-division", "369", "ASCRM, ASCSM"],
    ["Detector commented-out-code", "1085", "ASCMM"],
]))
w("<h2>Anexo B. Extracto del Issue Log de la revisión de v0.1</h2>")
w(tabla(["ID", "Módulo", "Línea", "CWE", "Herramienta", "Estado"],
        [[f"F-{n:02d}", h["modulo"].replace("vigisalud.", ""), h["linea"], h["cwe"], h["herramienta"],
          "Resuelto en v0.2"] for n, h in enumerate(D["issue_log_v0.1"], start=1)][:20], numericas=(2, 3)))
w(fuente(f"Se muestran 20 de {total_hallazgos} hallazgos. El registro completo está en el dashboard y en "
         "resultados/calidad_v0.1.json."))
w("<h2>Anexo C. Estructura del repositorio</h2>")
w(tabla(["Carpeta o archivo", "Contenido"], [
    ["codigo/v0.1, codigo/v0.2", "Prototipo de VigiSalud antes y después de la revisión"],
    ["medicion/fichas.py", "Fichas de los 13 indicadores (estructura del Punto 1)"],
    ["medicion/iso5055.py", "Listas de CWE por medida y mapeo de reglas"],
    ["medicion/detectores.py", "Detectores propios sobre el árbol sintáctico"],
    ["medicion/medir_calidad.py, medir_eficiencia.py", "Captura y proceso de las medidas"],
    ["medicion/consolidar.py, medir_todo.py", "Consolidación y ejecución completa"],
    ["resultados/", "JSON de cada versión, consolidado y datos del dashboard"],
]))
w("</body></html>")

salida = RAIZ / "docs" / "informe_TP5.html"
salida.write_text("\n".join(html), encoding="utf-8")
print(salida, len(salida.read_text(encoding="utf-8")))
