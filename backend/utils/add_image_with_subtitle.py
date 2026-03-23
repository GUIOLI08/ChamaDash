from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_image_with_subtitle(doc, img_stream, legenda, largura_inches):
    """Centers an image and adds a formatted caption below it."""
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_img = p_img.add_run()
    run_img.add_picture(img_stream, width=Inches(largura_inches))
    
    p_leg = doc.add_paragraph()
    p_leg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_leg = p_leg.add_run(legenda)
    run_leg.font.name = 'Verdana'
    run_leg.font.size = Pt(9)
    run_leg.font.color.rgb = RGBColor(0, 0, 0)