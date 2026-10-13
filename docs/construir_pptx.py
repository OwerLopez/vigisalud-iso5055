"""Genera docs/TP5_VigiSalud_slides.pptx (en ingles) con el mismo contenido de construir_slides.py.

Uso: python docs/construir_pptx.py
Las imagenes (logo UNSA y graficos) se insertan despues en Google Slides por URL;
sus posiciones quedan en docs/imagenes_slides.json.
"""

import copy
import json
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

sys.path.insert(0, str(Path(__file__).parent))
import construir_slides as cs  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ALIGN = {"START": PP_ALIGN.LEFT, "CENTER": PP_ALIGN.CENTER, "END": PP_ALIGN.RIGHT}
ANCHOR = {"TOP": MSO_ANCHOR.TOP, "MIDDLE": MSO_ANCHOR.MIDDLE, "BOTTOM": MSO_ANCHOR.BOTTOM}
KIND = {"RECTANGLE": MSO_SHAPE.RECTANGLE, "ROUND_RECTANGLE": MSO_SHAPE.ROUNDED_RECTANGLE,
        "ELLIPSE": MSO_SHAPE.OVAL}
NO_STYLE_NO_GRID = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"

NOTES = {
    1: "Good morning. We are team [N] and we will show how we applied ISO/IEC 20246 and ISO/IEC 5055 to our "
       "public-health project, VigiSalud Arequipa. Each of the five members presents one part.",
    2: "This is our agenda. Member 1 introduces the project and the indicator structure, Members 2 and 3 cover "
       "quality and efficiency indicators, Member 4 the tool, and Member 5 the measured results.",
    3: "VigiSalud receives weekly notifications from health facilities, validates them, computes incidence and "
       "case fatality, and compares each week against a five-year endemic channel to raise outbreak alerts. "
       "Because it stores health data, security and reliability are acceptance criteria, not extras.",
    4: "ISO 20246 defines five review activities. We plug ISO 5055 into each one: thresholds become exit "
       "criteria, the CWE list becomes the checklist, tools produce the findings, and re-measurement closes the "
       "loop. ISO 5055 scores each characteristic by counting severe CWE weaknesses: 29, 18, 74 and 73 of them.",
    5: "Point 1. Every indicator sits in the same five levels, from the ISO 25010 characteristic down to the "
       "tool rule. Inside, we follow the ISO 15939 measurement model: base measures, a function, the indicator "
       "and a decision criterion.",
    6: "Each indicator is documented in a sheet with twelve fields. The decision criterion is a traffic light: "
       "green meets the target, amber is accepted with a plan, red blocks acceptance in the review.",
    7: "Point 1, quality indicators. IC-01 to IC-03 are the three ISO 5055 structural measures as densities per "
       "thousand lines. IC-04 to IC-06 explain maintainability: complexity, the maintainability index and "
       "duplication. Security must be zero because the system handles sensitive data.",
    8: "These are real weaknesses from our baseline. An except clause that silently passes hides data errors; "
       "an SQL string built with f-strings allows injection; and one validation function had complexity 21.",
    9: "Point 2. ISO 5055 lists 18 efficiency weaknesses. These six appear in typical Python: concatenation in "
       "loops, list lookups inside loops, one query per iteration, new connections everywhere, unreleased "
       "resources and SQL outside the data layer.",
    10: "Static findings are causes; runtime indicators show their effect. We measure processing time at 20,000 "
        "notifications, throughput, peak memory, how time scales with load and where the time goes, always "
        "with seeded synthetic data and the median of repeated runs.",
    11: "Point 3. We compared SonarQube, CAST and our own toolchain. Only the toolchain covers static and "
        "runtime indicators, costs nothing and documents every calculation, which ISO 5055 requires.",
    12: "QMeter captures data with Radon, Pylint, Bandit, thirteen AST detectors and Python's profilers; maps "
        "each rule to its CWE and ISO 5055 measure; and presents JSON, a web dashboard and the issue log. "
        "One command measures both versions.",
    13: "Results. The baseline missed nine of twelve targets. After fixing the findings, version 0.2 meets all "
        "thirteen, including the 100 percent resolution rate that closes the review.",
    14: "The review found 44 occurrences of 20 CWE types. Unreleased resources and missing connection reuse "
        "lead. The runtime confirmed it: the baseline left the database locked in every benchmark run.",
    15: "Fixing those weaknesses made weekly processing 21 times faster at 20,000 notifications and 58 times "
        "faster at 40,000, with exactly the same outputs. The baseline grew quadratically because of list "
        "lookups.",
    16: "To conclude: the two standards complement each other, one indicator sheet keeps us consistent, and a "
        "free documented toolchain is enough for a course project. The live dashboard has all the details. "
        "Thank you.",
}


def color(h):
    return RGBColor.from_string(h.lstrip("#"))


class PptxDeck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(10), Inches(5.625)
        self.blank = self.prs.slide_layouts[6]
        self.imagenes = []
        self.num = 0

    def slide(self, sid, bg=cs.BG):
        self.s = self.prs.slides.add_slide(self.blank)
        self.num += 1
        fill = self.s.background.fill
        fill.solid()
        fill.fore_color.rgb = color(bg)
        self.s.notes_slide.notes_text_frame.text = NOTES.get(self.num, "")

    def shape(self, x, y, w, h, kind="TEXT_BOX", fill=None, outline=None, valign=None):
        if kind == "TEXT_BOX":
            sh = self.s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        else:
            sh = self.s.shapes.add_shape(KIND[kind], Inches(x), Inches(y), Inches(w), Inches(h))
            sh.shadow.inherit = False
            if kind == "ROUND_RECTANGLE":
                sh.adjustments[0] = 0.08
            if fill:
                sh.fill.solid()
                sh.fill.fore_color.rgb = color(fill)
            else:
                sh.fill.background()
            if outline:
                sh.line.color.rgb = color(outline)
                sh.line.width = Pt(1)
            else:
                sh.line.fill.background()
        tf = sh.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.vertical_anchor = ANCHOR[valign or "TOP"]
        if kind != "TEXT_BOX":
            for lado in ("margin_left", "margin_right"):
                setattr(tf, lado, Inches(0.14))
        return sh

    def text(self, x, y, w, h, runs, size=16, color_=None, font=cs.BODY_FONT, align="START", bold=False,
             kind="TEXT_BOX", fill=None, outline=None, valign="TOP", bullets=False, space_below=None,
             line_spacing=None, link=None, **kw):
        col = kw.get("color", color_) or cs.INK
        sh = self.shape(x, y, w, h, kind, fill, outline, valign)
        if isinstance(runs, str):
            runs = [(runs, {})]
        # Divide las corridas en parrafos por saltos de linea.
        parrafos, actual = [], []
        for t, st in runs:
            partes = t.split("\n")
            for i, parte in enumerate(partes):
                if i > 0:
                    parrafos.append(actual)
                    actual = []
                if parte:
                    actual.append((parte, st))
        parrafos.append(actual)
        tf = sh.text_frame
        for i, corridas in enumerate(parrafos):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = ALIGN[align]
            if space_below is not None:
                p.space_after = Pt(space_below)
            if bullets:
                pPr = p._p.get_or_add_pPr()
                pPr.set("marL", str(Inches(0.22)))
                pPr.set("indent", str(-Inches(0.2)))
                bu = etree.SubElement(pPr, qn("a:buChar"))
                bu.set("char", "•")
            for t, st in corridas:
                r = p.add_run()
                r.text = t
                f = r.font
                f.size = Pt(st.get("size", size))
                f.name = st.get("font", font)
                f.bold = st.get("bold", bold)
                f.italic = st.get("italic", False)
                f.color.rgb = color(st.get("color", col))
                if link:
                    r.hyperlink.address = link
        return sh

    def image(self, url, x, y, w, h):
        locales = {cs.LOGO: "logo_unsa.png", cs.G["cwe_en"]: "cwe_en.png",
                   cs.G["escalabilidad_en"]: "escalabilidad_en.png"}
        ruta = RAIZ / "docs" / "graficos" / locales[url]
        self.s.shapes.add_picture(str(ruta), Inches(x), Inches(y), Inches(w), Inches(h))
        self.imagenes.append({"slide": self.num, "archivo": ruta.name})

    def arrow(self, x1, y1, x2, y2, color_=cs.MUTED):
        ln = self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        ln.line.color.rgb = color(color_)
        ln.line.width = Pt(1.5)
        lnxml = ln.line._get_or_add_ln()
        tail = etree.SubElement(lnxml, qn("a:tailEnd"))
        tail.set("type", "triangle")

    def table(self, x, y, widths, rows, size=14, row_h=0.4, header=True, align=None, colors=None,
              tint_col=None, bold_first_col=True):
        nr, nc = len(rows), len(rows[0])
        gf = self.s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * nr))
        tbl = gf.table
        tblPr = tbl._tbl.tblPr
        for attr in ("firstRow", "bandRow"):
            tblPr.set(attr, "0")
        style = tblPr.find(qn("a:tableStyleId"))
        if style is None:
            style = etree.SubElement(tblPr, qn("a:tableStyleId"))
        style.text = NO_STYLE_NO_GRID
        for c, cw in enumerate(widths):
            tbl.columns[c].width = Inches(cw)
        for r in range(nr):
            tbl.rows[r].height = Inches(row_h)
            for c in range(nc):
                cell = tbl.cell(r, c)
                val = rows[r][c]
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf = cell.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = ALIGN[(align or ["START"] * nc)[c]]
                run = p.add_run()
                run.text = "" if val is None else str(val)
                f = run.font
                f.size = Pt(size)
                f.name = cs.BODY_FONT
                f.bold = (header and r == 0) or (bold_first_col and c == 0 and r > 0)
                f.color.rgb = color(cs.MUTED if header and r == 0 else (colors or {}).get((r, c), cs.INK))
                tcPr = cell._tc.get_or_add_tcPr()
                for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
                    ln = etree.SubElement(tcPr, qn(tag))
                    if tag == "a:lnB" or (tag == "a:lnT" and r == 0):
                        ln.set("w", str(Pt(1)))
                        sf = etree.SubElement(ln, qn("a:solidFill"))
                        etree.SubElement(sf, qn("a:srgbClr")).set("val", cs.LINE.lstrip("#"))
                    else:
                        etree.SubElement(ln, qn("a:noFill"))
                if tint_col is not None and c == tint_col:
                    sf = etree.SubElement(tcPr, qn("a:solidFill"))
                    etree.SubElement(sf, qn("a:srgbClr")).set("val", cs.TEAL_TINT.lstrip("#"))
                else:
                    etree.SubElement(tcPr, qn("a:noFill"))
        return gf

    def header(self, label, title):
        self.text(0.5, 0.28, 9, 0.3, label, size=11, color=cs.MAROON, bold=True)
        self.text(0.5, 0.52, 9, 0.95, title, size=26, color=cs.INK, bold=True, font=cs.TITLE_FONT)

    def footer(self, num, note=None):
        self.text(0.5, 5.2, 7.4, 0.3, note or "VigiSalud Arequipa · Software Quality · Partial Assignment 5",
                  size=10, color=cs.MUTED)
        self.text(8.9, 5.2, 0.6, 0.3, str(num), size=10, color=cs.MUTED, align="END")


if __name__ == "__main__":
    d = cs.construir(PptxDeck())
    usado = d.blank
    for layout in list(d.prs.slide_layouts):
        if layout is not usado:
            d.prs.slide_layouts.remove(layout)
    destino = RAIZ / "docs" / "TP5_VigiSalud_slides.pptx"
    d.prs.save(destino)
    (RAIZ / "docs" / "imagenes_slides.json").write_text(json.dumps(d.imagenes, indent=1), encoding="utf-8")
    print(destino, destino.stat().st_size, d.imagenes)
