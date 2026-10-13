"""Genera los lotes de peticiones de Google Slides para la presentacion (en ingles).

Uso: python docs/construir_slides.py <revisionId>
Escribe docs/slides_lote1.json, slides_lote2.json y slides_lote3.json.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
D = json.loads((RAIZ / "resultados" / "indicadores.json").read_text(encoding="utf-8"))
G = json.loads((RAIZ / "resultados" / "graficos.json").read_text(encoding="utf-8"))
IND = {i["codigo"]: i for i in D["indicadores"]}

EMU = 914400
BG, INK, MUTED, LINE = "#FAFAFA", "#1F2937", "#6B7280", "#E0E0E0"
MAROON, MAROON_TINT, TEAL, TEAL_TINT, CARD = "#7A1F2B", "#F4E9EB", "#2E7D74", "#E3F1EF", "#EFF0F2"
STATUS = {"VERDE": "#1B7F3B", "AMBAR": "#A15C00", "ROJO": "#B3261E", "SIN DATO": MUTED}
TITLE_FONT, BODY_FONT, MONO = "Montserrat", "Lato", "Roboto Mono"
LOGO = "https://upload.wikimedia.org/wikipedia/commons/3/3a/LOGO_UNSA.png"
DASHBOARD = "https://vigisalud-iso5055.vercel.app"


def rgb(h):
    h = h.lstrip("#")
    return {"red": round(int(h[0:2], 16) / 255, 3), "green": round(int(h[2:4], 16) / 255, 3),
            "blue": round(int(h[4:6], 16) / 255, 3)}


def props(page, x, y, w, h):
    return {"pageObjectId": page,
            "size": {"width": {"magnitude": round(w * EMU), "unit": "EMU"},
                     "height": {"magnitude": round(h * EMU), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": round(x * EMU),
                          "translateY": round(y * EMU), "unit": "EMU"}}


class Deck:
    def __init__(self):
        self.reqs = []
        self.ids = set()

    def _id(self, oid):
        assert oid not in self.ids, oid
        self.ids.add(oid)
        return oid

    def slide(self, sid, bg=BG):
        sid = sid[:3]
        self.page = self._id(sid)
        self.n = 0
        self.reqs.append({"createSlide": {"objectId": sid, "slideLayoutReference": {"predefinedLayout": "BLANK"}}})
        self.reqs.append({"updatePageProperties": {"objectId": sid, "pageProperties": {
            "pageBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(bg)}}}}, "fields": "pageBackgroundFill"}})

    def _oid(self):
        self.n += 1
        return self._id(f"{self.page}e{self.n:02d}")

    def shape(self, x, y, w, h, kind="TEXT_BOX", fill=None, outline=None, valign=None):
        oid = self._oid()
        self.reqs.append({"createShape": {"objectId": oid, "shapeType": kind,
                                          "elementProperties": props(self.page, x, y, w, h)}})
        sp, fields = {}, []
        if fill:
            sp["shapeBackgroundFill"] = {"solidFill": {"color": {"rgbColor": rgb(fill)}}}
            fields.append("shapeBackgroundFill.solidFill.color")
        if kind != "TEXT_BOX":
            if outline:
                sp["outline"] = {"outlineFill": {"solidFill": {"color": {"rgbColor": rgb(outline)}}},
                                 "weight": {"magnitude": 1, "unit": "PT"}}
                fields += ["outline.outlineFill.solidFill.color", "outline.weight"]
            else:
                sp["outline"] = {"propertyState": "NOT_RENDERED"}
                fields.append("outline.propertyState")
        if valign and valign != "TOP":
            sp["contentAlignment"] = valign
            fields.append("contentAlignment")
        if fields:
            self.reqs.append({"updateShapeProperties": {"objectId": oid, "shapeProperties": sp,
                                                        "fields": ",".join(fields)}})
        return oid

    def text(self, x, y, w, h, runs, size=16, color=INK, font=BODY_FONT, align="START", bold=False,
             kind="TEXT_BOX", fill=None, outline=None, valign="TOP", bullets=False, space_below=None,
             line_spacing=None, link=None):
        """runs: str, or list of (texto, estilo) donde estilo puede tener bold/color/size/font/italic."""
        oid = self.shape(x, y, w, h, kind, fill, outline, valign)
        if isinstance(runs, str):
            runs = [(runs, {})]
        full = "".join(t for t, _ in runs)
        self.reqs.append({"insertText": {"objectId": oid, "text": full}})
        base = {"fontSize": {"magnitude": size, "unit": "PT"},
                "foregroundColor": {"opaqueColor": {"rgbColor": rgb(color)}}}
        if font != "Arial":
            base["fontFamily"] = font
        if bold:
            base["bold"] = True
        if link:
            base["link"] = {"url": link}
        self.reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "style": base,
                                              "fields": ",".join(base)}})
        pos = 0
        for t, st in runs:
            if st and t:
                style, fields = {}, []
                for k, v in st.items():
                    if k == "color":
                        style["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb(v)}}
                        fields.append("foregroundColor")
                    elif k == "size":
                        style["fontSize"] = {"magnitude": v, "unit": "PT"}
                        fields.append("fontSize")
                    elif k == "font":
                        style["fontFamily"] = v
                        fields.append("fontFamily")
                    else:
                        style[k] = v
                        fields.append(k)
                self.reqs.append({"updateTextStyle": {"objectId": oid, "textRange": {
                    "type": "FIXED_RANGE", "startIndex": pos, "endIndex": pos + len(t)},
                    "style": style, "fields": ",".join(fields)}})
            pos += len(t)
        para = {"alignment": align} if align != "START" else {}
        if space_below is not None:
            para["spaceBelow"] = {"magnitude": space_below, "unit": "PT"}
        if line_spacing:
            para["lineSpacing"] = line_spacing
        if para:
            self.reqs.append({"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                                       "style": para, "fields": ",".join(para)}})
        if bullets:
            self.reqs.append({"createParagraphBullets": {"objectId": oid, "textRange": {"type": "ALL"},
                                                         "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        return oid

    def image(self, url, x, y, w, h):
        oid = self._oid()
        self.reqs.append({"createImage": {"objectId": oid, "url": url,
                                          "elementProperties": props(self.page, x, y, w, h)}})

    def arrow(self, x1, y1, x2, y2, color=MUTED):
        oid = self._oid()
        self.reqs.append({"createLine": {"objectId": oid, "category": "STRAIGHT",
                                         "elementProperties": props(self.page, x1, y1, max(x2 - x1, 0.001),
                                                                    max(y2 - y1, 0.001))}})
        self.reqs.append({"updateLineProperties": {"objectId": oid, "lineProperties": {
            "lineFill": {"solidFill": {"color": {"rgbColor": rgb(color)}}},
            "weight": {"magnitude": 1.5, "unit": "PT"}, "endArrow": "FILL_ARROW"},
            "fields": "lineFill,weight,endArrow"}})

    def table(self, x, y, widths, rows, size=14, row_h=0.4, header=True, align=None, colors=None,
              tint_col=None, bold_first_col=True):
        oid = self._oid()
        nr, nc = len(rows), len(rows[0])
        self.reqs.append({"createTable": {"objectId": oid, "rows": nr, "columns": nc,
                                          "elementProperties": props(self.page, x, y, sum(widths), row_h * nr)}})
        for c, cw in enumerate(widths):
            self.reqs.append({"updateTableColumnProperties": {"objectId": oid, "columnIndices": [c],
                "tableColumnProperties": {"columnWidth": {"magnitude": round(cw * EMU), "unit": "EMU"}},
                "fields": "columnWidth"}})
        for r, fila in enumerate(rows):
            for c, val in enumerate(fila):
                if val in ("", None):
                    continue
                loc = {"rowIndex": r, "columnIndex": c}
                self.reqs.append({"insertText": {"objectId": oid, "cellLocation": loc, "text": str(val)}})
                es_header = header and r == 0
                bold = es_header or (bold_first_col and c == 0 and r > 0)
                color = MUTED if es_header else (colors or {}).get((r, c))
                style, fields = {}, []
                if bold:
                    style["bold"] = True
                    fields.append("bold")
                if color:
                    style["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb(color)}}
                    fields.append("foregroundColor")
                if size != 14:
                    style["fontSize"] = {"magnitude": size, "unit": "PT"}
                    fields.append("fontSize")
                if style:
                    self.reqs.append({"updateTextStyle": {"objectId": oid, "cellLocation": loc,
                        "textRange": {"type": "ALL"}, "style": style, "fields": ",".join(fields)}})
                if align and align[c] != "START":
                    self.reqs.append({"updateParagraphStyle": {"objectId": oid, "cellLocation": loc,
                        "textRange": {"type": "ALL"}, "style": {"alignment": align[c]}, "fields": "alignment"}})
        self.reqs.append({"updateTableCellProperties": {"objectId": oid, "tableRange": {
            "location": {"rowIndex": 0, "columnIndex": 0}, "rowSpan": nr, "columnSpan": nc},
            "tableCellProperties": {"tableCellBackgroundFill": {"propertyState": "NOT_RENDERED"},
                                    "contentAlignment": "MIDDLE"},
            "fields": "tableCellBackgroundFill.propertyState,contentAlignment"}})
        self.reqs.append({"updateTableBorderProperties": {"objectId": oid, "tableRange": {
            "location": {"rowIndex": 0, "columnIndex": 0}, "rowSpan": nr, "columnSpan": nc},
            "borderPosition": "ALL", "tableBorderProperties": {
                "tableBorderFill": {"solidFill": {"color": {"rgbColor": rgb(LINE)}}},
                "weight": {"magnitude": 1, "unit": "PT"}}, "fields": "tableBorderFill,weight"}})
        for pos in ("LEFT", "RIGHT", "INNER_VERTICAL"):
            self.reqs.append({"updateTableBorderProperties": {"objectId": oid, "tableRange": {
                "location": {"rowIndex": 0, "columnIndex": 0}, "rowSpan": nr, "columnSpan": nc},
                "borderPosition": pos, "tableBorderProperties": {
                    "tableBorderFill": {"solidFill": {"color": {"rgbColor": rgb(BG)}}},
                    "weight": {"magnitude": 0.5, "unit": "PT"}}, "fields": "tableBorderFill,weight"}})
        if tint_col is not None:
            self.reqs.append({"updateTableCellProperties": {"objectId": oid, "tableRange": {
                "location": {"rowIndex": 0, "columnIndex": tint_col}, "rowSpan": nr, "columnSpan": 1},
                "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(TEAL_TINT)}}}},
                "fields": "tableCellBackgroundFill.solidFill.color"}})
        return oid

    # ---- piezas comunes
    def header(self, label, title):
        self.text(0.5, 0.28, 9, 0.3, label, size=11, color=MAROON, bold=True, font=BODY_FONT)
        self.text(0.5, 0.52, 9, 0.95, title, size=26, color=INK, bold=True, font=TITLE_FONT, valign="TOP")

    def footer(self, num, note=None):
        self.text(0.5, 5.2, 7.4, 0.3, note or "VigiSalud Arequipa · Software Quality · Partial Assignment 5",
                  size=10, color=MUTED)
        self.text(8.9, 5.2, 0.6, 0.3, str(num), size=10, color=MUTED, align="END")


def fmt(codigo, v):
    if v is None:
        return "—"
    if codigo == "IE-03":
        return f"{v:,.0f}"
    if codigo in ("IE-06", "IR-01"):
        return f"{v:.1f}" if codigo == "IE-06" else f"{v:.0f}"
    return f"{v:.2f}"


def construir(d=None):
    d = d or Deck()
    t1 = IND["IE-02"]["v0.1"]
    t2 = IND["IE-02"]["v0.2"]
    c1 = {p["n"]: p["mediana_s"] for p in D["curvas"]["v0.1"]}
    c2 = {p["n"]: p["mediana_s"] for p in D["curvas"]["v0.2"]}
    total = len(D["issue_log_v0.1"])
    conteos = D["conteos_5055"]["v0.1"]

    # 1 ---------------------------------------------------------------- title
    d.slide("s01_title", bg=MAROON)
    d.shape(0.5, 0.45, 3.7, 1.42, "ROUND_RECTANGLE", fill="#FFFFFF")
    d.image(LOGO, 0.68, 0.6, 3.34, 1.12)
    d.text(0.5, 2.1, 9, 0.35, "Software Quality  ·  Partial Assignment 5", size=14, color="#F4E9EB", bold=True)
    d.text(0.5, 2.45, 9, 1.2, "Applying ISO/IEC 20246 and ISO/IEC 5055 to VigiSalud Arequipa",
           size=34, color="#FFFFFF", bold=True, font=TITLE_FONT)
    d.text(0.5, 3.7, 9, 0.5, "Code-quality and efficiency indicators for a public-health surveillance system",
           size=16, color="#F4E9EB")
    d.text(0.5, 4.75, 9, 0.5, "Team: [Member 1] · [Member 2] · [Member 3] · [Member 4] · [Member 5]   |   "
           "School of Systems Engineering, UNSA · Arequipa, October 2026", size=11, color="#F4E9EB")

    # 2 ---------------------------------------------------------------- agenda
    d.slide("s02_agenda")
    d.header("AGENDA", "Agenda and speakers")
    filas = [("Introduction and indicator structure", "The project, both standards and the five-level indicator model", "Slides 1–6"),
             ("Code-quality indicators", "Six indicators built on ISO 5055 maintainability, reliability and security", "Slides 7–8"),
             ("Efficiency indicators", "Static ISO 5055 weaknesses plus runtime time, memory and scaling", "Slides 9–10"),
             ("Measurement tool", "Tool selection and the capture, process and present pipeline", "Slides 11–12"),
             ("Results", "Measured indicators, findings and the web dashboard", "Slides 13–16")]
    for i, (tit, desc, sl) in enumerate(filas):
        y = 1.45 + i * 0.73
        d.text(0.5, y + 0.08, 0.5, 0.5, str(i + 1), size=16, bold=True, color="#FFFFFF", align="CENTER",
               kind="ELLIPSE", fill=MAROON, valign="MIDDLE", font=TITLE_FONT)
        d.text(1.2, y, 6.6, 0.68, [(f"Member {i + 1} · {tit}\n", {"bold": True}), (desc, {"color": MUTED, "size": 14})],
               size=16, valign="MIDDLE")
        d.text(7.9, y, 1.6, 0.68, sl, size=14, color=MUTED, align="END", valign="MIDDLE")
    d.footer(2)

    # 3 ---------------------------------------------------------------- project
    d.slide("s03_project")
    d.header("INTRODUCTION · MEMBER 1", "VigiSalud turns weekly disease reports into early outbreak alerts")
    pasos = [("Weekly reports", "CSV from health facilities"), ("Validation", "catalogs, ranges, duplicates"),
             ("Storage", "SQLite repository"), ("Indicators", "incidence, case fatality, age"),
             ("Endemic channel", "5-year quartiles → alerts and report")]
    for i, (a, b) in enumerate(pasos):
        x = 0.5 + i * 1.87
        d.text(x, 1.6, 1.62, 1.15, [(a + "\n", {"bold": True, "color": MAROON if i == 4 else INK}), (b, {"color": MUTED, "size": 14})],
               size=15, kind="ROUND_RECTANGLE", fill=MAROON_TINT if i == 4 else CARD, valign="MIDDLE", align="CENTER")
        if i < 4:
            d.arrow(x + 1.64, 2.175, x + 1.85, 2.176)
    tarjetas = [("3", "notifiable diseases: dengue, ARI and ADD"), ("10", "districts of an Arequipa health network"),
                (str(D["tamano"]["v0.1"]["sloc"]), "source lines in the Python 3.12 baseline (v0.1)")]
    for i, (num, lab) in enumerate(tarjetas):
        x = 0.5 + i * 3.075
        d.text(x, 3.1, 2.85, 1.35, [(num + "\n", {"size": 30, "bold": True, "color": MAROON, "font": TITLE_FONT}), (lab, {})],
               size=14, color=INK, kind="ROUND_RECTANGLE", fill="#FFFFFF", outline=LINE, valign="MIDDLE")
    d.text(0.5, 4.62, 9, 0.4, "The system stores sensitive health data, protected by Peru's Personal Data Protection Law (Law 29733).",
           size=14, color=MUTED)
    d.footer(3)

    # 4 ---------------------------------------------------------------- standards
    d.slide("s04_standards")
    d.header("INTRODUCTION · MEMBER 1", "ISO 20246 gives the review process; ISO 5055 gives the evidence")
    act = [("Planning", "Exit criteria are indicator thresholds"), ("Initiate review", "Checklist is the mapped CWE list"),
           ("Individual review", "Tools detect CWEs and time the code"), ("Issue analysis", "Issue Log and traffic lights decide"),
           ("Fixing and reporting", "Re-measure; IR-01 confirms closure")]
    for i, (a, b) in enumerate(act):
        x = 0.5 + i * 1.86
        d.text(x, 1.5, 1.68, 0.62, f"{i + 1}  {a}", size=14, bold=True, color="#FFFFFF", kind="ROUND_RECTANGLE",
               fill=MAROON, valign="MIDDLE", align="CENTER")
        d.text(x, 2.18, 1.68, 0.85, b, size=14, color=INK, align="CENTER")
    d.text(0.5, 3.12, 9, 0.35, "ISO/IEC 5055 measures: weakness occurrences counted per characteristic",
           size=14, bold=True, color=TEAL)
    medidas = [("29", "Maintainability (ASCMM)"), ("18", "Performance efficiency (ASCPEM)"),
               ("74", "Reliability (ASCRM)"), ("73", "Security (ASCSM)")]
    for i, (num, lab) in enumerate(medidas):
        x = 0.5 + i * 2.3
        d.text(x, 3.5, 2.1, 1.05, [(num, {"size": 26, "bold": True, "color": TEAL, "font": TITLE_FONT}),
                                   (" CWEs\n", {"color": MUTED}), (lab, {})],
               size=14, kind="ROUND_RECTANGLE", fill=TEAL_TINT, valign="MIDDLE", align="CENTER")
    d.footer(4, "Source: ISO/IEC 20246:2017, clause 6.4; ISO/IEC 5055:2021, clause 7.")

    # 5 ---------------------------------------------------------------- hierarchy
    d.slide("s05_structure")
    d.header("POINT 1 · MEMBER 1 · INDICATOR STRUCTURE", "Every indicator follows the same five-level structure")
    niveles = [("Quality characteristic", "ISO/IEC 25010"), ("ISO 5055 measure", "ASCMM, ASCRM, ASCSM, ASCPEM"),
               ("Project indicator", "IC quality, IE efficiency, IR review"), ("Base measure", "CWE count, SLOC, seconds, MB"),
               ("Source", "tool and rule that captures it")]
    for i, (a, b) in enumerate(niveles):
        x = 0.5 + i * 0.22
        d.text(x, 1.5 + i * 0.66, 4.6 - i * 0.22, 0.56, [(a + "  ", {"bold": True, "color": MAROON}), (b, {})],
               size=14, kind="ROUND_RECTANGLE", fill=CARD, valign="MIDDLE")
    d.text(5.6, 1.5, 3.9, 0.35, "ISO/IEC 15939 measurement model", size=15, bold=True, color=TEAL)
    modelo = ["Base measures", "Measurement function", "Indicator", "Decision criterion (traffic light)"]
    for i, m in enumerate(modelo):
        y = 1.95 + i * 0.68
        d.text(5.6, y, 3.9, 0.46, m, size=14, kind="ROUND_RECTANGLE", fill=TEAL_TINT, valign="MIDDLE", align="CENTER")
        if i < 3:
            d.arrow(7.55, y + 0.47, 7.551, y + 0.67)
    d.text(5.6, 4.7, 3.9, 0.4, "IC-01 = maintainability CWEs ÷ SLOC × 1000", size=14, color=MUTED, font=MONO)
    d.footer(5)

    # 6 ---------------------------------------------------------------- sheet
    d.slide("s06_sheet")
    d.header("POINT 1 · MEMBER 1 · INDICATOR STRUCTURE", "Each indicator sheet has 12 fields and a traffic-light rule")
    campos = ["Code and name", "Characteristic and ISO 5055 measure", "Related CWEs", "Question it answers",
              "Base measures", "Measurement function", "Unit and scale", "Tool and rule",
              "ISO 20246 activity", "Direction and thresholds", "Interpretation", "Owner"]
    filas = [[f"{i + 1}. {campos[i]}", f"{i + 7}. {campos[i + 6]}"] for i in range(6)]
    d.table(0.5, 1.5, [2.75, 2.45], filas, size=14, row_h=0.46, header=False, bold_first_col=False)
    luces = [("VERDE", "Green", "meets the target"), ("AMBAR", "Amber", "accepted with a plan"),
             ("ROJO", "Red", "blocks acceptance")]
    for i, (k, a, b) in enumerate(luces):
        y = 1.55 + i * 0.62
        d.shape(6.0, y + 0.08, 0.36, 0.36, "ELLIPSE", fill=STATUS[k])
        d.text(6.5, y, 3.0, 0.52, [(a + "  ", {"bold": True}), (b, {"color": MUTED})], size=15, valign="MIDDLE")
    d.text(6.0, 3.55, 3.5, 1.1, [("Example  ", {"bold": True, "color": MAROON}),
                                 ("IC-01 maintainability density: green ≤ 2, amber ≤ 5, red above 5 weaknesses per KSLOC", {})],
           size=14, kind="ROUND_RECTANGLE", fill=MAROON_TINT, valign="MIDDLE")
    d.footer(6, "Fields stored as data in medicion/fichas.py, shared by the tool, the dashboard and the report.")

    # 7 ---------------------------------------------------------------- quality indicators
    d.slide("s07_quality")
    d.header("POINT 1 · MEMBER 2 · CODE-QUALITY INDICATORS", "Six indicators measure the structural quality of the code")
    filas = [["Code", "Indicator", "How it is computed", "Green", "Amber"],
             ["IC-01", "Maintainability weakness density", "ASCMM CWEs per KSLOC", "≤ 2", "≤ 5"],
             ["IC-02", "Reliability weakness density", "ASCRM CWEs per KSLOC", "≤ 1", "≤ 3"],
             ["IC-03", "Security weakness density", "ASCSM CWEs per KSLOC", "0", "≤ 2"],
             ["IC-04", "Overly complex functions (CWE-1121)", "% of functions with CC > 10", "≤ 5%", "≤ 10%"],
             ["IC-05", "Maintainability index", "Radon MI, 0–100, SLOC-weighted", "≥ 50", "≥ 38"],
             ["IC-06", "Duplicated code (CWE-1041)", "duplicated lines ÷ SLOC", "≤ 3%", "≤ 5%"]]
    d.table(0.5, 1.45, [0.85, 3.45, 3.0, 0.85, 0.85], filas, size=14, row_h=0.45,
            align=["START", "START", "START", "END", "END"])
    d.footer(7, "KSLOC: thousand source lines. The security target is 0 because VigiSalud stores sensitive health data.")

    # 8 ---------------------------------------------------------------- code examples
    d.slide("s08_examples")
    d.header("POINT 1 · MEMBER 2 · CODE-QUALITY INDICATORS", "Each quality indicator traces back to real weaknesses in our code")
    ejemplos = [("Reliability · IC-02", "CWE-390 / 703", "try:\n    edad = int(x)\nexcept:\n    pass", "Catch ValueError and record the error"),
                ("Security · IC-03", "CWE-89", "execute(f\"...WHERE\n  distrito='{d}'\")", "Parameterized query with ?"),
                ("Maintainability · IC-04", "CWE-1121", "validar_notificacion()\n17 decisions\nCC = 21", "Rules as data tables: CC = 7")]
    for i, (tit, cwe, code, fix) in enumerate(ejemplos):
        x = 0.5 + i * 3.075
        d.text(x, 1.5, 2.85, 0.6, [(tit + "\n", {"bold": True, "color": MAROON}), (cwe, {"color": MUTED, "size": 14})],
               size=15)
        d.text(x, 2.2, 2.85, 1.5, code, size=14, font=MONO, kind="RECTANGLE", fill="#F3F4F6", valign="MIDDLE")
        d.text(x, 3.85, 2.85, 0.8, [("Fix  ", {"bold": True, "color": TEAL}), (fix, {})], size=14)
    d.footer(8, "Snippets from the VigiSalud v0.1 baseline.")

    # 9 ---------------------------------------------------------------- efficiency weaknesses
    d.slide("s09_effweak")
    d.header("POINT 2 · MEMBER 3 · EFFICIENCY INDICATORS", "ISO 5055 efficiency weaknesses take familiar shapes in Python")
    filas = [["ISO 5055 weakness", "Pattern in Python", "Fix"],
             ["CWE-1046 String concatenation", "html += ... inside a loop", "list + \"\".join()"],
             ["CWE-1067 Sequential searches", "if x in a list, inside a loop", "set or dict lookup"],
             ["CWE-1050/1060 Queries in loops", "one SELECT per district and week", "one GROUP BY query + index"],
             ["CWE-1072 No connection reuse", "sqlite3.connect() in every function", "one managed connection"],
             ["CWE-772/775 Unreleased resources", "open() or connect() without with", "context managers (with)"],
             ["CWE-1057 SQL outside data layer", "SQL inside the report module", "SQL only in the repository"]]
    d.table(0.5, 1.45, [3.2, 3.2, 2.6], filas, size=14, row_h=0.45)
    d.footer(9)

    # 10 --------------------------------------------------------------- efficiency indicators
    d.slide("s10_effind")
    d.header("POINT 2 · MEMBER 3 · EFFICIENCY INDICATORS", "Runtime indicators confirm what the static scan predicts")
    filas = [["Code", "Indicator", "Green"],
             ["IE-01", "Efficiency weakness density (ASCPEM)", "≤ 1 / KSLOC"],
             ["IE-02", "Weekly processing time, N = 20,000", "≤ 2 s"],
             ["IE-03", "Throughput", "≥ 10,000 /s"],
             ["IE-04", "Peak memory (tracemalloc)", "≤ 50 MB"],
             ["IE-05", "Scalability exponent b, t = a·Nᵇ", "≤ 1.2"],
             ["IE-06", "Hotspot share of time (cProfile)", "≤ 30%"]]
    d.table(0.5, 1.45, [0.85, 3.6, 1.55], filas, size=14, row_h=0.45, align=["START", "START", "END"])
    d.text(6.85, 1.45, 2.65, 3.2, [("Measurement protocol\n", {"bold": True, "color": TEAL}),
                                   ("Seeded synthetic data, no patients\nN from 2,500 to 40,000\nMedian of 5 runs, fresh process\n"
                                    "Memory and profile run apart\nOutputs must match across versions", {})],
           size=14, kind="ROUND_RECTANGLE", fill=TEAL_TINT, space_below=6)
    d.footer(10)

    # 11 --------------------------------------------------------------- tool selection
    d.slide("s11_tool")
    d.header("POINT 3 · MEMBER 4 · MEASUREMENT TOOL", "We chose a free Python toolchain over SonarQube and CAST")
    filas = [["Criterion", "SonarQube Community", "CAST AIP", "QMeter (chosen)"],
             ["Python support", "Yes", "Yes", "Yes"],
             ["Link to ISO 5055 CWEs", "CWE-tagged rules", "Implements ISO 5055", "Explicit rule→CWE map"],
             ["Runtime efficiency", "No", "No", "Time, memory, scaling"],
             ["Cost", "Free", "Commercial", "Free"],
             ["Setup", "Server and database", "License, deployment", "pip install"],
             ["Calculation transparency", "Partial", "Proprietary", "Fully documented"]]
    d.table(0.5, 1.45, [2.55, 2.15, 2.15, 2.15], filas, size=14, row_h=0.45, tint_col=3)
    d.footer(11, "SonarQube stays as a complement once the project has a continuous-integration server.")

    # 12 --------------------------------------------------------------- pipeline
    d.slide("s12_pipeline")
    d.header("POINT 3 · MEMBER 4 · MEASUREMENT TOOL", "QMeter captures, processes and presents every indicator in one command")
    cols = [("Capture", MAROON, MAROON_TINT, "Radon: complexity, MI, size\nPylint and Bandit rules mapped to CWE\n13 own AST detectors\nperf_counter, tracemalloc, cProfile"),
            ("Process", TEAL, TEAL_TINT, "Rule → CWE → ISO 5055 measure\nDeduplicate by module, line, CWE\nDensities per KSLOC\nlog-log fit and traffic lights"),
            ("Present", INK, CARD, "indicadores.json\nWeb dashboard\nISO 20246 Issue Log\nReport tables and charts")]
    for i, (tit, col, tint, body) in enumerate(cols):
        x = 0.5 + i * 3.1
        d.text(x, 1.5, 2.8, 0.45, tit, size=17, bold=True, color="#FFFFFF", kind="RECTANGLE", fill=col,
               valign="MIDDLE", align="CENTER", font=TITLE_FONT)
        d.text(x, 1.95, 2.8, 2.25, body, size=14, kind="RECTANGLE", fill=tint, bullets=True, space_below=6)
        if i < 2:
            d.arrow(x + 2.82, 3.05, x + 3.08, 3.051)
    d.text(0.5, 4.38, 9, 0.5, [("python medicion/medir_todo.py", {"font": MONO, "color": "#FFFFFF"}),
                               ("    measures both versions in about 3 minutes", {"color": "#D1D5DB"})],
           size=14, kind="RECTANGLE", fill=INK, valign="MIDDLE")
    d.footer(12)

    # 13 --------------------------------------------------------------- results table
    d.slide("s13_results")
    d.header("RESULTS · MEMBER 5", "The baseline missed 9 of 12 targets; the fixed version meets all 13")
    izq = ["IC-01", "IC-02", "IC-03", "IC-04", "IC-05", "IC-06", "IR-01"]
    der = ["IE-01", "IE-02", "IE-03", "IE-04", "IE-05", "IE-06"]
    nombres = {"IC-01": "Maintainability density", "IC-02": "Reliability density", "IC-03": "Security density",
               "IC-04": "Complex functions %", "IC-05": "Maintainability index", "IC-06": "Duplicated code %",
               "IR-01": "Findings resolved %", "IE-01": "Efficiency density", "IE-02": "Time, N = 20k (s)",
               "IE-03": "Throughput (/s)", "IE-04": "Peak memory (MB)", "IE-05": "Scaling exponent b",
               "IE-06": "Hotspot share %"}
    for x, codigos in ((0.5, izq), (5.15, der)):
        filas = [["Indicator", "v0.1", "v0.2"]]
        colores = {}
        for r, c in enumerate(codigos, start=1):
            i = IND[c]
            filas.append([f"{c} {nombres[c]}", fmt(c, i["v0.1"]), fmt(c, i["v0.2"])])
            colores[(r, 1)] = STATUS[i["semaforo_v0.1"]]
            colores[(r, 2)] = STATUS[i["semaforo_v0.2"]]
        d.table(x, 1.45, [2.65, 0.85, 0.85], filas, size=14, row_h=0.42, align=["START", "END", "END"],
                colors=colores, bold_first_col=False)
    d.footer(13, "Number color = status: green meets target, amber acceptable with a plan, red blocks acceptance.")

    # 14 --------------------------------------------------------------- findings chart
    d.slide("s14_findings")
    d.header("RESULTS · MEMBER 5", f"{total} weaknesses in v0.1, led by unreleased resources and SQL issues")
    d.image(G["cwe_en"], 0.5, 1.45, 5.25, 3.68)
    d.text(6.1, 1.5, 3.4, 1.0, [(str(total), {"size": 40, "bold": True, "color": MAROON, "font": TITLE_FONT}),
                                (f"  occurrences of {len(D['hallazgos_por_cwe_v0.1'])} CWE types", {})],
           size=15, valign="MIDDLE")
    d.text(6.1, 2.6, 3.4, 1.3, [("By ISO 5055 measure\n", {"bold": True, "color": TEAL}),
                                (f"Efficiency {conteos['ASCPEM']}  ·  Reliability {conteos['ASCRM']}\n"
                                 f"Security {conteos['ASCSM']}  ·  Maintainability {conteos['ASCMM']}", {})],
           size=14, kind="ROUND_RECTANGLE", fill=TEAL_TINT, valign="MIDDLE")
    d.text(6.1, 4.05, 3.4, 0.95, [("Runtime evidence  ", {"bold": True, "color": MAROON}),
                                  (f"v0.1 left the database locked in {D['bd_bloqueada']['v0.1']} benchmark runs (CWE-772)", {})],
           size=14, kind="ROUND_RECTANGLE", fill=MAROON_TINT, valign="MIDDLE")
    d.footer(14, "One weakness can count in several measures, as ISO/IEC 5055 defines.")

    # 15 --------------------------------------------------------------- scaling
    d.slide("s15_scaling")
    d.header("RESULTS · MEMBER 5", f"Fixing them made weekly processing {round(t1 / t2)}× faster with identical outputs")
    d.image(G["escalabilidad_en"], 0.5, 1.5, 5.8, 3.05)
    datos = [(f"{t1:.2f} s → {t2:.2f} s", "processing 20,000 notifications"),
             (f"{c1[40000]:.1f} s → {c2[40000]:.2f} s", "processing 40,000 notifications"),
             (f"{IND['IE-05']['v0.1']:.2f} → {IND['IE-05']['v0.2']:.2f}", "scalability exponent b")]
    for i, (num, lab) in enumerate(datos):
        d.text(6.6, 1.5 + i * 1.05, 2.9, 0.95, [(num + "\n", {"size": 22, "bold": True, "color": TEAL, "font": TITLE_FONT}),
                                                 (lab, {"color": MUTED})], size=14, valign="MIDDLE")
    d.footer(15, "Median of 5 runs at N = 20,000 and 3 runs elsewhere; same machine, Python 3.12.")

    # 16 --------------------------------------------------------------- conclusions
    d.slide("s16_close")
    d.header("CONCLUSIONS · MEMBER 5", "Conclusions and next steps")
    d.text(0.5, 1.45, 5.3, 3.2, "ISO 20246 supplies the review process; ISO 5055 supplies objective exit criteria\n"
           "One indicator sheet keeps all 13 indicators consistent across the team\n"
           f"Static findings predicted the runtime gain: {conteos['ASCPEM']} efficiency fixes, {round(t1 / t2)}× faster\n"
           "A free, documented toolchain meets ISO 5055's automated, objective, transparent and verifiable requirements",
           size=15, bullets=True, space_below=10)
    d.text(6.15, 1.45, 3.35, 2.05, [("Next steps\n", {"bold": True, "color": MAROON}),
                                    ("Measure every delivery\nAdd the web layer and CI\nSimplify validation (MI 43)\nExtend the detectors", {})],
           size=14, kind="ROUND_RECTANGLE", fill=MAROON_TINT, space_below=6)
    d.text(6.15, 3.65, 3.35, 1.0, [("Live dashboard\n", {"bold": True, "color": "#FFFFFF"}),
                                   ("Open the indicators, charts and issue log", {"color": "#E5E7EB"})],
           size=14, kind="ROUND_RECTANGLE", fill=TEAL, valign="MIDDLE", link=DASHBOARD)
    d.text(0.5, 4.75, 9, 0.4, "Thank you. Questions?", size=16, bold=True, color=MAROON, font=TITLE_FONT)
    d.footer(16)
    return d


if __name__ == "__main__":
    reqs = construir().reqs
    cortes = [i for i, r in enumerate(reqs) if "createSlide" in r]
    lotes = [(cortes[0], cortes[5]), (cortes[5], cortes[10]), (cortes[10], len(reqs))]
    for n, (a, b) in enumerate(lotes, start=1):
        lote = reqs[a:b]
        if n == 1:
            lote = [{"deleteObject": {"objectId": "p"}}] + lote
        destino = RAIZ / "docs" / f"slides_lote{n}.json"
        destino.write_text(json.dumps(lote, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(destino.name, len(lote), destino.stat().st_size)
