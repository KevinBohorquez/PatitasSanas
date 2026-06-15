import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generar_pdf_citas_diarias(citas_data, periodo_reporte):
    """
    Genera un archivo PDF con el reporte de citas diarias.
    citas_data: Lista de diccionarios con las claves 'horario', 'mascota', 'cliente', 'veterinario', 'estado'.
    periodo_reporte: Rango de fechas o descripción del período consultado.
    Retorna la ruta del archivo generado.
    """
    import tempfile
    
    # Crear un archivo temporal
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"citas_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos Personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor("#2aabcf"),
        spaceAfter=14,
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor("#555555"),
        spaceAfter=20,
        alignment=1 # Center
    )

    # Título y período
    elements.append(Paragraph("<b>Reporte de Citas Diarias - Patitas Sanas</b>", title_style))
    periodo_str = periodo_reporte if isinstance(periodo_reporte, str) else periodo_reporte.strftime("%d/%m/%Y")
    elements.append(Paragraph(f"Período consultado: {periodo_str}", subtitle_style))
    elements.append(Paragraph(
        f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        subtitle_style
    ))
    elements.append(Spacer(1, 10))

    # Tabla de Citas
    if not citas_data:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>No hay citas registradas para el período seleccionado.</b>", subtitle_style))
    else:
        data = [["Horario", "Mascota", "Cliente", "Veterinario", "Estado"]]
        
        for cita in citas_data:
            data.append([
                cita.get('horario', 'N/A'),
                cita.get('mascota', 'N/A'),
                cita.get('cliente', 'N/A'),
                cita.get('veterinario', 'N/A'),
                cita.get('estado', 'N/A')
            ])
            
        # Estilos de la tabla
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor("#2aabcf")),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#FFFFFF")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor("#f8f9fa")),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor("#333333")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor("#dddddd")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Crear la tabla y aplicar estilos
        t = Table(data, colWidths=[3*cm, 3.5*cm, 4*cm, 4*cm, 2.5*cm])
        t.setStyle(table_style)
        
        elements.append(t)
    
    # Construir PDF
    doc.build(elements)
    
    return file_path
