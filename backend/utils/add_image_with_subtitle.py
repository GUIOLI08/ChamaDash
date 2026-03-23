from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_image_with_subtitle(doc, img_stream, caption, width_inches):
    """
    Centers an image in the document and adds a formatted 
    Verdana 9 caption directly below it.
    """
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_img = p_img.add_run()
    run_img.add_picture(img_stream, width=Inches(width_inches))
    
    p_leg = doc.add_paragraph()
    p_leg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_leg = p_leg.add_run(caption)
    run_leg.font.name = 'Verdana'
    run_leg.font.size = Pt(9)
    run_leg.font.color.rgb = RGBColor(0, 0, 0)