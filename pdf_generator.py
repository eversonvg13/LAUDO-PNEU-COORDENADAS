def pdf_generator(pneu, data_analise):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=15,
        bottomMargin=15
    )
    
    styles = getSampleStyleSheet()
    
    style_header_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#000000')
    )
    
    style_cell_value = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#000000')
    )
    
    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#000000')
    )
    
    style_section_body = ParagraphStyle(
        'SectionBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#000000')
    )

    style_garagem_lines = ParagraphStyle(
        'GaragemLines',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=11.5,
        textColor=colors.HexColor('#999999')
    )

    story = []
    
    # 1. Cabeçalho com Logo
    logo_path = None
    for nome_img in ["ssasdsds.png", "logo-nobg.png", "logo.png"]:
        if os.path.exists(nome_img):
            logo_path = nome_img
            break
            
    if logo_path:
        try:
            with PILImage.open(logo_path) as pil_img:
                orig_w, orig_h = pil_img.size
                desired_w = 95
                desired_h = (orig_h * desired_w) / orig_w
                
                scale_factor = 3
                high_res_img = pil_img.resize(
                    (int(desired_w * scale_factor), int(desired_h * scale_factor)), 
                    PILImage.Resampling.LANCZOS
                )
                
                logo_io = io.BytesIO()
                high_res_img.save(logo_io, format='PNG', optimize=True)
                logo_io.seek(0)
                
                img_logo = RLImage(logo_io, width=desired_w, height=desired_h)
        except Exception:
            img_logo = RLImage(logo_path, width=95, height=32)
        
        img_logo.hAlign = 'LEFT'

    style_header_sub = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#000000')
    )
        
    bloco_titulo_central = [
        Paragraph("<b>GRUPO EMPRESARIAL COORDENADAS</b>", style_header_title),
        Spacer(1, 2),
        Paragraph("Laudo de Pneus", style_header_sub)
    ]
    
    if logo_path:
        header_table_data = [
            [img_logo, bloco_titulo_central, Paragraph("<b>SGQ 391/15-Rev01</b>", ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=TA_RIGHT))]
        ]
    else:
        header_table_data = [
            [Paragraph("<b>COORDENADAS</b>", style_header_title), bloco_titulo_central, Paragraph("<b>SGQ 391/15-Rev01</b>", ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=TA_RIGHT))]
        ]
        
    t_header = Table(header_table_data, colWidths=[120, 325, 115])
    t_header.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e5e7eb')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 3))
    
    # 2. Grid de Informações
    unidade = pneu.get('local', '') or '-'
    fogo = str(pneu.get('fogo', ''))
    veiculo = str(pneu.get('veiculo', ''))
    
    medida_raw = str(pneu.get('medida', ''))
    if '-' in medida_raw:
        medida = medida_raw.split('-')[-1].strip()
    else:
        medida = medida_raw.strip()

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
    
    t_grid = Table(grid_data, colWidths=[185, 187, 188])
    t_grid.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_grid)
    story.append(Spacer(1, 3))
    
    # 3. Laudo, Causas e Observações
    danos = pneu.get('danos', '') or pneu.get('descricao_dano_ia', '')
    causas = pneu.get('causas_provaveis', '')
    obs = pneu.get('observacoes', '') or pneu.get('acao_recomendada', '')
    
    secoes_data = [
        [Paragraph(f"<b>Dano causado:</b> {danos}", style_section_body)],
        [Paragraph(f"<b>Causas prováveis:</b> {causas}", style_section_body)],
        [Paragraph(f"<b>Observações:</b> {obs}", style_section_body)],
        [Paragraph("Laudo relatado por: &nbsp; &nbsp; <b>Everson Veloso</b><br/><font size=9 color='#333333'>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;Enc. Borracharia</font>", style_section_body)]
    ]
    
    t_secoes = Table(secoes_data, colWidths=[560])
    t_secoes.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_secoes)
    story.append(Spacer(1, 3))
    
    # 4. Bloco da Garagem Ampliado
    linha_completa = "_" * 100
    linhas_pautadas = "<br/>".join([linha_completa] * 14)
    espaco_garagem_data = [
        [Paragraph("<b>Resposta da Garagem (Defeitos encontrados no veículo / Ações executadas):</b>", style_section_title)],
        [Paragraph(linhas_pautadas, style_garagem_lines)],
    ]
    t_garagem = Table(espaco_garagem_data, colWidths=[560])
    t_garagem.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('LINEBELOW', (0,0), (0,0), 1, colors.HexColor('#000000')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f9fafb')),
    ]))
    story.append(t_garagem)
    story.append(Spacer(1, 3))
    
    # 5. Assinatura Coordenador de Manutenção
    assinatura_data = [
        [Paragraph("<b>Visto Coordenador de Manutenção:</b> _____________________________________________________", style_cell_value)]
    ]
    t_assinatura = Table(assinatura_data, colWidths=[560])
    t_assinatura.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_assinatura)
    
    # 6. Fotos Específicas do Pneu (Com suporte a Rotação Dinâmica)
    imagens_pneu_objs = pneu.get('imagens_objetos', [])
    rotacoes_dict = pneu.get('rotacoes_imagens', {})
    
    if imagens_pneu_objs:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Registro Fotográfico do Pneu:</b>", style_section_title))
        story.append(Spacer(1, 4))
        
        img_table_data = []
        linha_atual = []
        for img_file in imagens_pneu_objs:
            try:
                img_pil = PILImage.open(img_file)
                
                # Aplica a rotação escolhida pelo usuário na tela
                angulo = rotacoes_dict.get(img_file.name, 0)
                if angulo > 0:
                    img_pil = img_pil.rotate(-angulo, expand=True)
                
                img_io = io.BytesIO()
                img_pil.save(img_io, format='JPEG')
                img_io.seek(0)
                
                rl_img = RLImage(img_io, width=230, height=145)
                linha_atual.append(rl_img)
                if len(linha_atual) == 2:
                    img_table_data.append(linha_atual)
                    linha_atual = []
            except Exception:
                pass
                
        if linha_atual:
            while len(linha_atual) < 2:
                linha_atual.append("")
            img_table_data.append(linha_atual)
            
        if img_table_data:
            t_fotos = Table(img_table_data, colWidths=[280, 280])
            t_fotos.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(t_fotos)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
