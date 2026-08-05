import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

def gerar_pdf_laudo_pneu(pneu, data_analise):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados para o padrão corporativo
    style_header_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#000000')
    )
    
    style_header_sub = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#333333')
    )
    
    style_cell_value = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#000000')
    )
    
    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#000000')
    )
    
    style_section_body = ParagraphStyle(
        'SectionBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#333333')
    )
    
    story = []
    
    # 1. Cabeçalho Oficial
    header_data = [
        [
            Paragraph("<b>GRUPO EMPRESARIAL COORDENADAS</b>", style_header_title),
            Paragraph("<b>SGQ 391/15-Rev01</b>", style_header_sub)
        ]
    ]
    t_header = Table(header_data, colWidths=[400, 135])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))
    
    # 2. Grid de Informações (Padrão 4x3)
    unidade = pneu.get('local', '') or '-'
    fogo = str(pneu.get('fogo', ''))
    veiculo = str(pneu.get('veiculo', ''))
    medida = str(pneu.get('medida', ''))
    posicao = str(pneu.get('pos', ''))
    km_pos = str(pneu.get('km_pos', ''))
    retirada = str(pneu.get('retirada', ''))
    km_total = str(pneu.get('km_total', ''))
    valor_sugerido = pneu.get('valor_sugerido', 'R$ 600,00')
    valor_cobrado = pneu.get('valor_cobrado', '')
    n_reformas = str(pneu.get('n_reformas', '0'))
    
    grid_data = [
        [
            Paragraph(f"<b>UNIDADE:</b> {unidade}", style_cell_value),
            Paragraph(f"<b>Nº FOGO PNEU:</b> {fogo}", style_cell_value),
            Paragraph(f"<b>DATA DA ANÁLISE:</b> {data_analise}", style_cell_value)
        ],
        [
            Paragraph(f"<b>VEÍCULO:</b> {veiculo}", style_cell_value),
            Paragraph(f"<b>MEDIDA PNEU:</b> {medida}", style_cell_value),
            Paragraph(f"<b>VALOR SUGERIDO:</b> {valor_sugerido}", style_cell_value)
        ],
        [
            Paragraph(f"<b>POSIÇÃO:</b> {posicao}", style_cell_value),
            Paragraph(f"<b>KM POSIÇÃO:</b> {km_pos}", style_cell_value),
            Paragraph(f"<b>VALOR COBRADO:</b> {valor_cobrado}", style_cell_value)
        ],
        [
            Paragraph(f"<b>RETIRADA:</b> {retirada}", style_cell_value),
            Paragraph(f"<b>KM TOTAL:</b> {km_total}", style_cell_value),
            Paragraph(f"<b>Nº REFORMAS:</b> {n_reformas}", style_cell_value)
        ]
    ]
    
    t_grid = Table(grid_data, colWidths=[175, 180, 180])
    t_grid.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_grid)
    story.append(Spacer(1, 8))
    
    # 3. Seções de Laudo, Causas e Observações
    danos = pneu.get('danos', '') or pneu.get('descricao_dano_ia', '')
    causas = pneu.get('causas_provaveis', '')
    obs = pneu.get('observacoes', '') or pneu.get('acao_recomendada', '')
    
    secoes_data = [
        [Paragraph("<b>Laudo relatado por:</b>", style_section_title)],
        [Paragraph(danos, style_section_body)],
        [Paragraph("<b>Causas prováveis:</b>", style_section_title)],
        [Paragraph(causas, style_section_body)],
        [Paragraph("<b>Observações:</b>", style_section_title)],
        [Paragraph(obs, style_section_body)]
    ]
    
    t_secoes = Table(secoes_data, colWidths=[535])
    t_secoes.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f5f5f5')),
        ('BACKGROUND', (0,2), (0,2), colors.HexColor('#f5f5f5')),
        ('BACKGROUND', (0,4), (0,4), colors.HexColor('#f5f5f5')),
    ]))
    story.append(t_secoes)
    story.append(Spacer(1, 10))
    
    # 4. Assinaturas e Vistos no Rodapé
    assinatura_data = [
        [
            Paragraph("<b>Everson Veloso</b><br/>Enc. Borracharia", style_cell_value),
            Paragraph("<b>Visto líder de manutenção:</b> ____________________", style_cell_value),
            Paragraph("<b>VISTO GERENTE:</b> ____________________", style_cell_value)
        ]
    ]
    t_assinatura = Table(assinatura_data, colWidths=[140, 200, 195])
    t_assinatura.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_assinatura)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_pdf_fallback(texto_bruto, data_str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>GRUPO EMPRESARIAL COORDENADAS - SGQ 391/15-Rev01</b>", styles['Heading1']),
        Spacer(1, 10),
        Paragraph(f"<b>Data:</b> {data_str}", styles['Normal']),
        Spacer(1, 10),
        Paragraph(texto_bruto.replace('\n', '<br/>'), styles['Normal'])
    ]
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
