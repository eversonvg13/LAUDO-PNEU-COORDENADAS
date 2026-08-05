import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

def gerar_pdf_laudo_pneu(pneu: dict, data_analise: str = None) -> bytes:
    """
    Gera o laudo individual de um único pneu no layout SGQ 391/15-Rev01 (Grupo Empresarial Coordenadas).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )
    
    elements = []
    styles = getSampleStyleSheet()

    # Estilos de Texto
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=0,
        textColor=colors.HexColor("#000000")
    )
    
    style_header_sub = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        alignment=2,
        textColor=colors.HexColor("#333333")
    )

    style_cell_val = ParagraphStyle(
        'CellVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#000000")
    )

    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#000000")
    )

    style_body_text = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#111111")
    )

    # --- 1. CABEÇALHO ---
    header_data = [
        [
            Paragraph("<b>GRUPO EMPRESARIAL COORDENADAS</b>", style_title),
            Paragraph("<b>SGQ 391/15-Rev01</b>", style_header_sub)
        ]
    ]
    t_header = Table(header_data, colWidths=[140 * mm, 50 * mm])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 3 * mm))

    # --- 2. GRADE DE DADOS DO PNEU ---
    dt_str = data_analise or datetime.now().strftime("%d/%m/%Y")
    
    grid_data = [
        [
            Paragraph(f"<b>UNIDADE:</b> {pneu.get('local', 'UBERLANDIA')}", style_cell_val),
            Paragraph(f"<b>Nº FOGO PNEU:</b> {pneu.get('fogo', '')}", style_cell_val),
            Paragraph(f"<b>DATA DA ANÁLISE:</b> {dt_str}", style_cell_val),
        ],
        [
            Paragraph(f"<b>VEÍCULO:</b> {pneu.get('veiculo', '')}", style_cell_val),
            Paragraph(f"<b>MEDIDA PNEU:</b> {pneu.get('medida', '')}", style_cell_val),
            Paragraph(f"<b>VALOR SUGERIDO:</b> {pneu.get('valor_sugerido', 'R$ 600,00')}", style_cell_val),
        ],
        [
            Paragraph(f"<b>POSIÇÃO:</b> {pneu.get('pos', '')}", style_cell_val),
            Paragraph(f"<b>KM POSIÇÃO:</b> {pneu.get('km_pos', '')}", style_cell_val),
            Paragraph(f"<b>VALOR COBRADO:</b> {pneu.get('valor_cobrado', '')}", style_cell_val),
        ],
        [
            Paragraph(f"<b>RETIRADA:</b> {pneu.get('retirada', '')}", style_cell_val),
            Paragraph(f"<b>KM TOTAL:</b> {pneu.get('km_total', '')}", style_cell_val),
            Paragraph(f"<b>Nº REFORMAS:</b> {pneu.get('n_reformas', '0')}", style_cell_val),
        ]
    ]

    t_grid = Table(grid_data, colWidths=[63 * mm, 63 * mm, 64 * mm])
    t_grid.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#000000")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_grid)
    elements.append(Spacer(1, 3 * mm))

    # --- 3. SEÇÕES DE LAUDO / CAUSAS / OBSERVAÇÕES ---
    laudo_relatado = pneu.get('danos') or pneu.get('laudo_relatado') or "Desgaste irregular da Banda de Rodagem."
    causas = pneu.get('causas_provaveis') or "Folgas nas mangas, cubos, buchas estouradas, veículo desalinhado."
    obs = pneu.get('acao_recomendada') or pneu.get('observacoes') or (
        "Verificar folgas nas mangas, cubos e eixos, verificar buchas das barras, amortecedores e suspensão em geral, "
        "verificar alinhamento do veículo. Orientar o colaborador a efetuar rodízios e 'viradas na roda' quando necessário, "
        "além de fazer o acompanhamento das profundidades dos sulcos no pneu."
    )

    text_block = [
        [Paragraph("<b>Laudo relatado por:</b>", style_section_title)],
        [Paragraph(laudo_relatado, style_body_text)],
        [Spacer(1, 1.5 * mm)],
        [Paragraph("<b>Causas prováveis:</b>", style_section_title)],
        [Paragraph(causas, style_body_text)],
        [Spacer(1, 1.5 * mm)],
        [Paragraph("<b>Observações:</b>", style_section_title)],
        [Paragraph(obs, style_body_text)],
    ]
    
    t_text = Table(text_block, colWidths=[190 * mm])
    t_text.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_text)
    elements.append(Spacer(1, 4 * mm))

    # --- 4. ASSINATURAS E VISTOS ---
    sig_data = [
        [
            Paragraph("<b>Everson Veloso</b><br/>Enc. Borracharia", style_body_text),
            Paragraph("<b>Visto líder de manutenção:</b>", style_body_text),
            Paragraph("<b>VISTO GERENTE:</b>", style_body_text),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[63 * mm, 63 * mm, 64 * mm])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_sig)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_pdf_fallback(texto_bruto: str, timestamp: str) -> bytes:
    """Fallback caso haja algum erro estrutural no JSON da IA."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"<b>Laudo Simplificado - {timestamp}</b>", styles['Title']),
        Spacer(1, 10),
        Paragraph(texto_bruto.replace('\n', '<br/>'), styles['BodyText'])
    ]
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
