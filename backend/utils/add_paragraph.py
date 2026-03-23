from docx.shared import Pt, RGBColor

def add_paragraph(doc, texto, bold=False):
    """Ensures normal text is formatted as Verdana 9 Black."""
    p = doc.add_paragraph()
    run = p.add_run(texto)
    run.font.name = 'Verdana'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0, 0, 0)
    if bold: run.font.bold = True
    return p