from docx.shared import Pt, RGBColor

def add_paragraph(doc, text, bold=False):
    """
    Adds a paragraph to the document using the standard project style:
    Verdana font, size 9, and black color.
    """
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Verdana'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0, 0, 0)
    if bold: run.font.bold = True
    return p