from typing import Any
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docx.oxml import OxmlElement

def add_title(doc: Any, text: str, level: int = 1) -> None:
    """
    Adiciona um título formatado ao documento Word.

    Força a fonte Verdana, estilo negrito e desenha uma linha inferior personalizada 
    (underline azul) para títulos de Nível 1.

    Args:
        doc (docx.document.Document): O objeto do documento Word (python-docx).
        text (str): O texto do título.
        level (int, opcional): O nível do título (1 para principal, 2 para subtítulo, etc.). O padrão é 1.

    Returns:
        None
    """
    p = doc.add_heading(level=level)
    run = p.add_run(text)
    run.font.name = 'Verdana'
    run.font.size = Pt(11) if level == 1 else Pt(10)
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.font.bold = True
    
    if level == 1:
        # Manipulação de XML personalizada para inserir uma borda inferior (linha azul)
        pPr = p._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '12') # Espessura da borda
        bottom.set(qn('w:space'), '4') 
        bottom.set(qn('w:color'), '3083A3') # Cor azul claro do tema
        pBdr.append(bottom)
        pPr.append(pBdr)