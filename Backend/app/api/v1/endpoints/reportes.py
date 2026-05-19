from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app.config.database import get_db
from app.models import Cita, Mascota, Cliente, ClienteMascota, ServicioSolicitado, Consulta, Veterinario, Usuario, HistorialClinico, Raza, Diagnostico
from app.services.pdf.appointments_pdf import generar_pdf_citas_diarias
from app.services.pdf.medical_history_pdf import generar_pdf_historial_clinico

router = APIRouter()

@router.get("/citas/pdf", response_class=FileResponse)
async def descargar_reporte_citas_pdf(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Genera y descarga el reporte PDF de las citas médicas.
    """
    try:
        query = db.query(Cita, Mascota, Cliente, Veterinario, Usuario).select_from(Cita) \
            .outerjoin(Mascota, Cita.id_mascota == Mascota.id_mascota) \
            .outerjoin(ClienteMascota, Mascota.id_mascota == ClienteMascota.id_mascota) \
            .outerjoin(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente) \
            .outerjoin(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .outerjoin(Consulta, ServicioSolicitado.id_consulta == Consulta.id_consulta) \
            .outerjoin(Veterinario, Consulta.id_veterinario == Veterinario.id_veterinario) \
            .outerjoin(Usuario, Veterinario.id_usuario == Usuario.id_usuario)

        if fecha_inicio:
            query = query.filter(Cita.fecha_hora_programada >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Cita.fecha_hora_programada <= fecha_fin)

        resultados = query.order_by(Cita.fecha_hora_programada.asc()).all()

        citas_data = []
        for r in resultados:
            cita, mascota, cliente, veterinario, usuario = r
            
            # Formatear cliente
            nombre_cliente = "N/A"
            if cliente:
                nombre_cliente = f"{cliente.nombre} {cliente.apellido_paterno}"
                
            # Formatear veterinario
            nombre_vet = "N/A"
            if veterinario:
                nombre_vet = f"{veterinario.nombre} {veterinario.apellido_paterno}"
            elif usuario:
                nombre_vet = usuario.username

            citas_data.append({
                "horario": str(cita.fecha_hora_programada.strftime("%d/%m/%Y %H:%M") if cita.fecha_hora_programada else "N/A"),
                "mascota": str(mascota.nombre if mascota and mascota.nombre else "N/A"),
                "cliente": str(nombre_cliente),
                "veterinario": str(nombre_vet),
                "estado": str(cita.estado_cita or "Programada")
            })
        
        # Generar archivo
        file_path = generar_pdf_citas_diarias(citas_data, datetime.now())
        
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
async def descargar_historial_clinico_pdf(mascota_id: int, db: Session = Depends(get_db)):
    """
    Genera y descarga el historial clínico en PDF de una mascota específica conectando a BD.
    """
    try:
        # 1. Obtener información de la mascota
        mascota_db = db.query(Mascota, Raza, Cliente).select_from(Mascota) \
            .outerjoin(Raza, Mascota.id_raza == Raza.id_raza) \
            .outerjoin(ClienteMascota, Mascota.id_mascota == ClienteMascota.id_mascota) \
            .outerjoin(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente) \
            .filter(Mascota.id_mascota == mascota_id).first()
            
        if not mascota_db:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")
            
        m_obj, r_obj, c_obj = mascota_db
        
        mascota_data = {
            "nombre": str(m_obj.nombre or "Desconocido"),
            "raza": str(r_obj.nombre_raza if r_obj and r_obj.nombre_raza else "Desconocida"),
            "edad": str(m_obj.edad_anios if m_obj.edad_anios is not None else "N/A"),
            "sexo": str(m_obj.sexo or "N/A"),
            "cliente": str(f"{c_obj.nombre} {c_obj.apellido_paterno}" if c_obj else "Sin asignar")
        }

        # 2. Obtener Historial
        registros_db = db.query(HistorialClinico, Consulta, Diagnostico, Veterinario, Usuario).select_from(HistorialClinico) \
            .outerjoin(Consulta, HistorialClinico.id_consulta == Consulta.id_consulta) \
            .outerjoin(Diagnostico, HistorialClinico.id_diagnostico == Diagnostico.id_diagnostico) \
            .outerjoin(Veterinario, HistorialClinico.id_veterinario == Veterinario.id_veterinario) \
            .outerjoin(Usuario, Veterinario.id_usuario == Usuario.id_usuario) \
            .filter(HistorialClinico.id_mascota == mascota_id) \
            .order_by(HistorialClinico.fecha_evento.desc()).all()
            
        historial_data = []
        for reg in registros_db:
            h_obj, cons_obj, diag_obj, vet_obj, u_obj = reg
            
            # Formatear veterinario
            nombre_vet = "N/A"
            if vet_obj:
                nombre_vet = f"{vet_obj.nombre} {vet_obj.apellido_paterno}"
            elif u_obj:
                nombre_vet = u_obj.username
                
            historial_data.append({
                "fecha": str(h_obj.fecha_evento.strftime("%d/%m/%Y %H:%M") if h_obj.fecha_evento else "N/A"),
                "motivo": str(cons_obj.motivo_consulta if cons_obj and cons_obj.motivo_consulta else h_obj.tipo_evento or "N/A"),
                "diagnostico": str(diag_obj.diagnostico if diag_obj and hasattr(diag_obj, 'diagnostico') and diag_obj.diagnostico else h_obj.descripcion_evento or "N/A"),
                "veterinario": str(nombre_vet)
            })
        
        file_path = generar_pdf_historial_clinico(historial_data, mascota_data)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error al generar el archivo PDF")
            
        return FileResponse(
            path=file_path,
            filename=f"Historial_Clinico_{mascota_id}.pdf",
            media_type='application/pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))