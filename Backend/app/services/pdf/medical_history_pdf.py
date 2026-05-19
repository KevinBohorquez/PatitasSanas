import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generar_pdf_historial_clinico(historial_data, mascota_data):
    """
    Genera un archivo PDF con el historial clínico de una mascota.
    historial_data: Lista de diccionarios con las consultas/diagnósticos.
    mascota_data: Diccionario con la información básica de la mascota.
    Retorna la ruta del archivo generado.
    """
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"historial_{mascota_data.get('nombre', 'mascota')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
    
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
    
    # Estilos
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=HexColor("#2aabcf"), alignment=1)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=14, textColor=HexColor("#5ec1dd"), spaceBefore=10)
    normal_style = styles['Normal']
    
    # Encabezado principal
    elements.append(Paragraph("<b>Historial Clínico Veterinario</b>", title_style))
    elements.append(Spacer(1, 10))
    
    # Datos de la Mascota
    elements.append(Paragraph("<b>Datos del Paciente</b>", subtitle_style))
    
    info_mascota = [
        ["Nombre:", mascota_data.get('nombre', 'N/A'), "Especie/Raza:", mascota_data.get('raza', 'N/A')],
        ["Edad:", str(mascota_data.get('edad', 'N/A')), "Sexo:", mascota_data.get('sexo', 'N/A')],
        ["Dueño:", mascota_data.get('cliente', 'N/A'), "Fecha Reporte:", datetime.now().strftime("%d/%m/%Y")]
    ]
    
    t_mascota = Table(info_mascota, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
    t_mascota.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_mascota)
    elements.append(Spacer(1, 20))
    
    # Registros médicos
    elements.append(Paragraph("<b>Registros Médicos</b>", subtitle_style))
    elements.append(Spacer(1, 5))
    
    if not historial_data:
        elements.append(Paragraph("No hay registros médicos para este paciente.", normal_style))
    else:
        for registro in historial_data:
            fecha = registro.get('fecha', 'Sin fecha')
            motivo = registro.get('motivo', 'N/A')
            diagnostico = registro.get('diagnostico', 'N/A')
            veterinario = registro.get('veterinario', 'N/A')
            
            # Crear mini-tabla por cada registro para mejor visualización
            datos_registro = [
                [Paragraph(f"<b>Fecha:</b> {fecha}", normal_style), Paragraph(f"<b>Atendido por:</b> {veterinario}", normal_style)],
                [Paragraph(f"<b>Motivo:</b> {motivo}", normal_style), ""],
                [Paragraph(f"<b>Diagnóstico:</b> {diagnostico}", normal_style), ""]
            ]
            
            t_registro = Table(datos_registro, colWidths=[8*cm, 8*cm])
            t_registro.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor("#f0f8ff")),
                ('SPAN', (0, 1), (1, 1)), # Unir columnas para motivo
                ('SPAN', (0, 2), (1, 2)), # Unir columnas para diagnostico
                ('BOX', (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(t_registro)
            elements.append(Spacer(1, 15))
    
    doc.build(elements)
    return file_path
