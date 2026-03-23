from docx.oxml.ns import qn
from docx.shared import Pt
from docx.shared import RGBColor
from docx.oxml import OxmlElement

def add_title(doc, text, level=1):
    """
    Adds a formatted heading to the Word document.
    Forces Verdana font, bold styling, and draws a custom blue underline for Level 1 headings.
    """
    p = doc.add_heading(level=level)
    run = p.add_run(text)
    run.font.name = 'Verdana'
    run.font.size = Pt(11) if level == 1 else Pt(10)
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.font.bold = True
    
    if level == 1:
        # Custom XML manipulation to insert a bottom border (underline) without template dependency
        pPr = p._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '12') # Border thickness
        bottom.set(qn('w:space'), '4') 
        bottom.set(qn('w:color'), '3083A3') # Theme Light Blue
        pBdr.append(bottom)
        pPr.append(pBdr)