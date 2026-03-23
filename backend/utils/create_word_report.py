import os
import io
import datetime
import base64
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from .consult_ia import consult_ia
from .generate_image_graphic import generate_image_graphic
from .add_title import add_title
from .add_paragraph import add_paragraph
from .add_image_with_subtitle import add_image_with_subtitle

def shade_cell(cell, fill_color):
    """Injects XML to set the background fill color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def format_cell(cell, text, bold=False, color=None, font_size=7):
    """Writes text into a cell, centering it and applying Verdana styling."""
    cell.text = str(text)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.runs[0]
    run.font.name = 'Verdana'
    run.font.size = Pt(font_size)
    if bold: run.font.bold = True
    if color: run.font.color.rgb = color

def create_word_report(dados_dashboard):
    """
    Main function to construct the Word report.
    Handles styles, footer generation, cover page, and all data sections.
    """
    caminho_template = "template_netra.docx"
    doc = Document(caminho_template) if os.path.exists(caminho_template) else Document()

    if 'Normal' in doc.styles:
        doc.styles['Normal'].font.name = 'Verdana'
        doc.styles['Normal'].font.size = Pt(9)
        doc.styles['Normal'].paragraph_format.space_after = Pt(6) 
        doc.styles['Normal'].paragraph_format.line_spacing = 1.5 

    for i in range(1, 4):
        style_name = f'Heading {i}'
        if style_name in doc.styles:
            doc.styles[style_name].paragraph_format.space_before = Pt(18)
            doc.styles[style_name].paragraph_format.space_after = Pt(10)

    ai_texts = consult_ia(dados_dashboard)
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")

    # Update Footer Information
    for section in doc.sections:
        for p in section.footer.paragraphs:
            if "TIC-RQ-28" in p.text or "Relatório" in p.text:
                p.text = "" 
                run = p.add_run(f"TIC-RQ-28 - Relatório de Nível de Serviço e Indicadores da Qualidade de Serviço {current_date}")
                run.font.name = 'Verdana'
                run.font.size = Pt(8)
                run.font.color.rgb = RGBColor(100, 100, 100) 
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- CAPA ---
    for _ in range(1): doc.add_paragraph()
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p_titulo.add_run("TIC-RQ-28 - Relatório de Nível de Serviço e Indicadores da Qualidade de Serviço")
    run_t.font.name = 'Verdana'
    run_t.font.size = Pt(12)
    run_t.font.bold = True
    
    for _ in range(4): doc.add_paragraph()
    p_cli = doc.add_paragraph()
    p_cli.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cli = p_cli.add_run("Cliente: Bahiagás")
    run_cli.font.name = 'Verdana'
    run_cli.font.size = Pt(11)
    run_cli.font.bold = True
    
    for _ in range(3): doc.add_paragraph()
    add_paragraph(doc, f"Emitido em: {current_date}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_paragraph(doc, "Período de apuração: [MÊS DE APURAÇÃO]").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # --- SUMÁRIO ---
    add_title(doc, 'Sumário', 1)
    sumario = [
        "1. INTRODUÇÃO",
        "2. SUMÁRIO DA PERFORMANCE RELACIONADO ÀS METAS DE NÍVEL DE SERVIÇO",
        "3. RESULTADOS APURADOS DOS SERVIÇOS",
        "   3.1 DADOS GERAIS",
        "      3.1.1 Percentual de chamados registrados por tipo",
        "      3.1.2 Percentual de Incidentes e Solicitações de Serviços registradas por prioridade relatada",
        "      3.1.3 Atendimentos por área demandante",
        "4. EVENTOS SIGNIFICATIVOS",
        "   4.1 REGISTROS DE INCIDENTE",
        "      4.1.1 Planos de Continuidade Acionados",
        "      4.1.2 Incidentes Graves",
        "   4.2 REGISTROS DE PROBLEMA",
        "   4.3 CARGA DE TRABALHO",
        "      4.3.1 Serviços mais utilizados",
        "5. ANÁLISE DE TENDÊNCIAS",
        "6. ANEXOS"
    ]
    for item in sumario:
        is_bold = not item.startswith(" ")
        add_paragraph(doc, item, bold=is_bold)
        
    doc.add_page_break()

    # --- 1. INTRODUCTION ---
    add_title(doc, '1. INTRODUÇÃO', 1)
    add_paragraph(doc, ai_texts.get('introduction', 'Standard introduction text.'))

    doc.add_page_break()
    
    # --- 2. SLA (MATRIZ GERAL) ---
    add_title(doc, '2. SUMÁRIO DA PERFORMANCE RELACIONADO ÀS METAS DE NÍVEL DE SERVIÇO', 1)
    add_paragraph(doc, 'O quadro abaixo resume o nível de serviço obtido no período e compara com o nível proposto:')
    
    t_sla = doc.add_table(rows=7, cols=13)
    try: t_sla.style = 'Table Grid'
    except KeyError:
        try: t_sla.style = 'Grade de Tabela'
        except KeyError: pass
    
    cor_branca = RGBColor(255, 255, 255)

    shade_cell(t_sla.cell(0,0), "244062")

    headers_r1 = [(0,1,"Chamados"), (2,4,"Baixa"), (5,7,"Média"), (8,10,"Alta"), (11,12,"Total")]
    for c_start, c_end, text in headers_r1:
        c = t_sla.cell(1, c_start)
        c.merge(t_sla.cell(1, c_end))
        format_cell(c, text, bold=True, color=cor_branca, font_size=8)
        shade_cell(c, "244062")

    headers_r2 = ["Tipos", "Qtd", "No Prazo", "Fora", "ANS", "No Prazo", "Fora", "ANS", "No Prazo", "Fora", "ANS", "No Prazo", "Fora"]
    for idx, h in enumerate(headers_r2):
        format_cell(t_sla.cell(2, idx), h, bold=True, color=cor_branca, font_size=7)
        shade_cell(t_sla.cell(2, idx), "4F81BD")

    # Populate Table with Real Data
    matriz_sla = dados_dashboard.get("matriz_sla", {})
    tipos = ["Incidentes", "Solicitações", "Problemas", "Total"]
    
    for r_idx, tipo in enumerate(tipos, start=3):
        is_bold = (r_idx == 6)
        format_cell(t_sla.cell(r_idx, 0), tipo, bold=is_bold, font_size=7)
        
        # Retrieve data sent from main.py (fallback to hyphens if missing)
        valores = matriz_sla.get(tipo, ["-"] * 12)
        
        for c_idx in range(1, 13):
            val = valores[c_idx - 1]
            
            # Format SLA percentage columns (indices 4, 7, 10 in the Word matrix)
            if val != "-" and c_idx in [4, 7, 10]:
                try:
                    val_str = f"{float(val)*100:.0f}%"
                except (ValueError, TypeError):
                    val_str = str(val)
            else:
                val_str = str(val)
                
            format_cell(t_sla.cell(r_idx, c_idx), val_str, bold=is_bold, font_size=7)

    p_tab = doc.add_paragraph()
    p_tab.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tab = p_tab.add_run("Tabela 1: Quantitativo de chamados por tipo x impacto")
    run_tab.font.name = 'Verdana'
    run_tab.font.size = Pt(8)

    doc.add_page_break()
    
    # --- 3. RESULTADOS APURADOS ---
    add_title(doc, '3. RESULTADOS APURADOS DOS SERVIÇOS', 1)
    add_title(doc, '3.1 DADOS GERAIS', 2)
    add_paragraph(doc, 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.')
    
    # --- 3.1.1 General Chart for Call Types ---
    add_title(doc, '3.1.1 Percentual de chamados registrados por tipo', 3)
    # Ensure title does not necessarily stick to the image in an awkward way
    doc.paragraphs[-1].paragraph_format.keep_with_next = False 
    
    if dados_dashboard.get('tipos_gerais'):
        img_tipos = generate_image_graphic(dados_dashboard['tipos_gerais'], 'Tipo de Chamado', 'pie')
        add_image_with_subtitle(doc, img_tipos, "Gráfico 1: Percentual por tipo de chamado", 3.2) 
        # Reset line spacing to prevent image distortion
        doc.paragraphs[-2].paragraph_format.line_spacing = 1.0 
        doc.paragraphs[-1].paragraph_format.keep_with_next = False
        
    # --- 3.1.2 Priority Chart for Incidents and Requests ---
    add_title(doc, '3.1.2 Percentual de Incidentes e Solicitações de Serviços registradas por prioridade relatada', 3)
    doc.paragraphs[-1].paragraph_format.keep_with_next = False 
    
    if dados_dashboard.get('inc_prio'):
        img_inc = generate_image_graphic(dados_dashboard['inc_prio'], 'Incidentes por Prioridade', 'pie')
        add_image_with_subtitle(doc, img_inc, "Gráfico 2: Incidentes por prioridade", 3.2)
        doc.paragraphs[-2].paragraph_format.line_spacing = 1.0
        doc.paragraphs[-1].paragraph_format.keep_with_next = False 
        
    # --- 3.1.2 Cont. (Requests) ---
    if dados_dashboard.get('req_prio'):
        img_req = generate_image_graphic(dados_dashboard['req_prio'], 'Solicitações por Prioridade', 'pie')
        add_image_with_subtitle(doc, img_req, "Gráfico 3: Solicitações por prioridade", 3.2)
        doc.paragraphs[-2].paragraph_format.line_spacing = 1.0
        doc.paragraphs[-1].paragraph_format.keep_with_next = False 

    # --- 3.1.3 Chart for Demanding Areas (Bar Chart) ---
    add_title(doc, '3.1.3 Atendimentos por área demandante', 3)
    doc.paragraphs[-1].paragraph_format.keep_with_next = False
    
    if dados_dashboard.get('top_setores'):
        img_setores = generate_image_graphic(dados_dashboard['top_setores'], 'Atendimentos por Setor - Top 10', 'bar')
        add_image_with_subtitle(doc, img_setores, "Gráfico 4: Atendimentos abertos por áreas demandantes", 4.5)
        doc.paragraphs[-2].paragraph_format.line_spacing = 1.0
        doc.paragraphs[-1].paragraph_format.keep_with_next = False 
    
    doc.add_page_break()
    
    # --- 4. EVENTOS SIGNIFICATIVOS ---
    add_title(doc, '4. EVENTOS SIGNIFICATIVOS', 1)
    add_title(doc, '4.1 REGISTRO DE INCIDENTE', 2)
    add_title(doc, '4.1.1 Planos de Continuidade Acionados', 3)
    add_paragraph(doc, 'Nesse período não houve acionamento de Plano de Continuidade.')
    
    add_title(doc, '4.1.2 Incidentes Graves', 3)
    add_paragraph(doc, 'Nesse período não houve registro de incidentes graves.')
    
    add_title(doc, '4.2 REGISTRO DE PROBLEMA', 2)
    add_paragraph(doc, 'Nesse período não houve registro de Problemas.')
    
    add_title(doc, '4.3 CARGA DE TRABALHO', 2)
    doc.paragraphs[-1].paragraph_format.keep_with_next = True 
    
    add_title(doc, '4.3.1 Serviços mais utilizados', 3)
    doc.paragraphs[-1].paragraph_format.keep_with_next = True 
    
    p_carga = add_paragraph(doc, 'Houve maior incidência das seguintes Solicitações de Serviço:')
    p_carga.paragraph_format.keep_with_next = True 
    
    if dados_dashboard.get('top_categorias'):
        img_cat = generate_image_graphic(dados_dashboard['top_categorias'], 'Chamados por Categoria', 'bar')
        add_image_with_subtitle(doc, img_cat, "Gráfico 5: Chamados abertos por categoria", 4.5)

    # --- 5. TREND ANALYSIS ---
    add_title(doc, '5. ANÁLISE DE TENDÊNCIAS', 1)
    p_tendencia = doc.add_paragraph()
    run_tend = p_tendencia.add_run(ai_texts.get('data_analysis', 'Standard trend analysis.'))
    run_tend.font.name = 'Verdana'
    run_tend.font.size = Pt(9)

    # --- 6. ATTACHMENTS ---
    add_title(doc, 'Anexos', 1)
    # Placeholder for manual evidence insertion
    add_paragraph(doc, 'Insira aqui evidências ou imagens complementares da Central Telefônica ou outros sistemas.')

    word_output = io.BytesIO()
    doc.save(word_output)
    word_output.seek(0)
    return base64.b64encode(word_output.getvalue()).decode("utf-8")