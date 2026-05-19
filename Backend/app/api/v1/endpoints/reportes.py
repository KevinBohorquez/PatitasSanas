from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
import os

from app.services.pdf.appointments_pdf import generar_pdf_citas_diarias
from app.services.pdf.medical_history_pdf import generar_pdf_historial_clinico

router = APIRouter()

@router.get("/citas/pdf", response_class=FileResponse)
async def descargar_reporte_citas_pdf():
    """
    Genera y descarga el reporte PDF de las citas diarias.
    """
    try:
        # Aquí en el futuro se conectará con la DB para traer citas reales
        # Por ahora usamos data simulada para probar el motor de PDF
        mock_citas = [
            {"horario": "09:00 AM", "mascota": "Firulais", "cliente": "Juan Perez", "veterinario": "Dr. Smith", "estado": "Programada"},
            {"horario": "10:30 AM", "mascota": "Mishi", "cliente": "Ana Gomez", "veterinario": "Dra. Lee", "estado": "Atendida"}
        ]
        
        file_path = generar_pdf_citas_diarias(mock_citas, datetime.now())
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error al generar el archivo PDF")
            
        return FileResponse(
            path=file_path,
            filename=f"Reporte_Citas_{datetime.now().strftime('%Y%m%d')}.pdf",
            media_type='application/pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historial/{mascota_id}/pdf", response_class=FileResponse)
async def descargar_historial_clinico_pdf(mascota_id: int):
    """
    Genera y descarga el historial clínico en PDF de una mascota específica.
    """
    try:
        # Data simulada temporal
        mock_mascota = {
            "nombre": "Firulais", "raza": "Golden Retriever", "edad": 4, "sexo": "Macho", "cliente": "Juan Perez"
        }
        mock_historial = [
            {"fecha": "10/05/2026", "motivo": "Vacunación", "diagnostico": "Paciente sano", "veterinario": "Dr. Smith"},
            {"fecha": "15/04/2026", "motivo": "Control de peso", "diagnostico": "Sobrepeso leve", "veterinario": "Dra. Lee"}
        ]
        
        file_path = generar_pdf_historial_clinico(mock_historial, mock_mascota)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error al generar el archivo PDF")
            
        return FileResponse(
            path=file_path,
            filename=f"Historial_Clinico_{mascota_id}.pdf",
            media_type='application/pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))