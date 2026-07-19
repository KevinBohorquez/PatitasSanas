from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date, time
import os

from app.config.database import get_db
from app.crud.dashboard_crud import dashboard
from app.queries import reportes_queries
from app.services.pdf.appointments_pdf import generar_pdf_citas_diarias
from app.services.pdf.medical_history_pdf import generar_pdf_historial_clinico

router = APIRouter()

@router.get("/citas/pdf", response_class=FileResponse)
async def descargar_reporte_citas_pdf(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Genera y descarga el reporte PDF de las citas médicas.
    """
    try:
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin."
            )

        inicio_dt = datetime.combine(fecha_inicio, time.min) if fecha_inicio else None
        fin_dt = datetime.combine(fecha_fin, time(23, 59, 59)) if fecha_fin else None

        resultados = reportes_queries.listar_citas_reporte(db, inicio_dt=inicio_dt, fin_dt=fin_dt)

        citas_data = []
        citas_vistas = set()
        for r in resultados:
            cita, mascota, cliente, veterinario, usuario = r

            if cita.id_cita in citas_vistas:
                continue
            citas_vistas.add(cita.id_cita)
            
            nombre_cliente = "N/A"
            if cliente:
                nombre_cliente = f"{cliente.nombre} {cliente.apellido_paterno}"
                
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

        if fecha_inicio and fecha_fin:
            periodo = f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        elif fecha_inicio:
            periodo = f"Desde {fecha_inicio.strftime('%d/%m/%Y')}"
        elif fecha_fin:
            periodo = f"Hasta {fecha_fin.strftime('%d/%m/%Y')}"
        else:
            periodo = "Todas las citas"

        file_path = generar_pdf_citas_diarias(citas_data, periodo)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error al generar el archivo PDF")
            
        return FileResponse(
            path=file_path,
            filename=f"Reporte_Citas_{datetime.now().strftime('%Y%m%d')}.pdf",
            media_type='application/pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consultas-por-mes")
def get_consultas_por_mes(
    año: int = None,
    db: Session = Depends(get_db)
):
    return dashboard.get_consultas_por_mes(db, año=año)

@router.get("/historial/{mascota_id}/pdf", response_class=FileResponse)
async def descargar_historial_clinico_pdf(
    mascota_id: int,
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio del filtro (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin del filtro (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Genera y descarga el historial clínico en PDF de una mascota específica conectando a BD.
    Acepta parámetros opcionales fecha_inicio y fecha_fin para filtrar por rango de fechas.
    """
    try:
        # Validar rango de fechas
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin."
            )

        # 1. Obtener información de la mascota
        mascota_db = reportes_queries.get_mascota_reporte(db, mascota_id=mascota_id)

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

        # 2. Obtener Historial con filtros de fecha opcionales
        inicio_dt = datetime.combine(fecha_inicio, time.min) if fecha_inicio else None
        fin_dt = datetime.combine(fecha_fin, time(23, 59, 59)) if fecha_fin else None

        registros_db = reportes_queries.listar_historial_reporte(
            db, mascota_id=mascota_id, inicio_dt=inicio_dt, fin_dt=fin_dt
        )
            
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