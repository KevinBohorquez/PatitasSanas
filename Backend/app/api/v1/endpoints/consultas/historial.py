# app/api/v1/endpoints/consultas/historial.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, date

from app.config.database import get_db
from app.models import Veterinario, HistorialClinico, Diagnostico, Patologia
from app.models.consulta import Consulta
from app.models.triaje import Triaje
from app.models.solicitud_atencion import SolicitudAtencion

router = APIRouter()

@router.get("/historial/{mascota_id}")
async def get_historial_clinico_mascota(
    mascota_id: int,
    db: Session = Depends(get_db),
    fecha_desde: Optional[date] = Query(None, description="Filtrar eventos desde esta fecha (inclusive)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar eventos hasta esta fecha (inclusive)"),
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de eventos")
):
    """
    Obtener historial clínico de una mascota, ordenado por fecha de evento descendente,
    incluyendo el veterinario responsable de cada evento.
    Permite filtrar opcionalmente por rango de fechas (fecha_hasta es inclusiva).
    Si la mascota no tiene eventos, retorna una lista vacía (HTTP 200).
    """
    try:
        query = db.query(HistorialClinico, Veterinario) \
            .outerjoin(Veterinario, HistorialClinico.id_veterinario == Veterinario.id_veterinario) \
            .filter(HistorialClinico.id_mascota == mascota_id)

        if fecha_desde:
            query = query.filter(HistorialClinico.fecha_evento >= fecha_desde)
        if fecha_hasta:
            # Incluir todos los eventos del día 'fecha_hasta' (hasta las 23:59:59)
            fecha_hasta_completa = datetime.combine(fecha_hasta, datetime.max.time())
            query = query.filter(HistorialClinico.fecha_evento <= fecha_hasta_completa)

        resultados = query.order_by(desc(HistorialClinico.fecha_evento)).limit(limit).all()

        return [
            {
                "id_historial": e.id_historial,
                "fecha_evento": e.fecha_evento,
                "tipo_evento": e.tipo_evento,
                "edad_meses": e.edad_meses,
                "descripcion_evento": e.descripcion_evento,
                "peso_momento": float(e.peso_momento) if e.peso_momento else None,
                "observaciones": e.observaciones,
                "veterinario": f"{v.nombre} {v.apellido_paterno}" if v else None
            }
            for e, v in resultados
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial clínico: {str(e)}"
        )


@router.get("/historialConsultas/{mascota_id}", response_model=List[dict])
async def get_historial_consultas_mascota(
    mascota_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de eventos")
):
    """
    Obtener historial clínico de una mascota y sus consultas
    """
    try:
        # Consultar las consultas relacionadas con la mascota, pasando por la cadena
        # correcta: Consulta -> Triaje -> Solicitud_atencion -> Mascota.
        # (Antes se cruzaba SolicitudAtencion.id_solicitud == Consulta.id_triaje, lo que
        # comparaba un id de solicitud con un id de triaje y solo coincidía por casualidad
        # en los registros donde ambos ids eran iguales.)
        eventos = db.query(Consulta) \
            .join(Triaje, Triaje.id_triaje == Consulta.id_triaje) \
            .join(SolicitudAtencion, SolicitudAtencion.id_solicitud == Triaje.id_solicitud) \
            .filter(SolicitudAtencion.id_mascota == mascota_id) \
            .order_by(Consulta.fecha_consulta.desc()) \
            .limit(limit).all()

        # Si la mascota no tiene consultas, devolver lista vacía (HTTP 200) en lugar
        # de 404, para que el front muestre un historial vacío y no un error.
        # Mapear los eventos para devolverlos en el formato adecuado
        return [
            {
                "id_consulta": e.id_consulta,
                "fecha_consulta": e.fecha_consulta,
                "tipo_consulta": e.tipo_consulta,
                "motivo_consulta": e.motivo_consulta,
                "diagnostico_preliminar": e.diagnostico_preliminar,
                "observaciones": e.observaciones
            }
            for e in eventos
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consultas: {str(e)}"
        )


@router.get("/historialDetallado/{mascota_id}", response_model=List[dict])
async def get_historial_detallado_mascota(
    mascota_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de consultas")
):
    """
    Historial clínico detallado por consulta de una mascota. Por cada consulta devuelve sus
    datos clínicos + el evento de historial asociado (edad, peso, observaciones) + los
    diagnósticos con su patología (nombre, tipo, estado, gravedad, contagiosa/crónica).
    Alimenta el panel interactivo y el detalle de diagnóstico del modal de Historial Clínico.
    """
    try:
        # Consultas de la mascota, por la cadena Consulta -> Triaje -> Solicitud_atencion -> Mascota.
        consultas = db.query(Consulta, Veterinario) \
            .join(Triaje, Triaje.id_triaje == Consulta.id_triaje) \
            .join(SolicitudAtencion, SolicitudAtencion.id_solicitud == Triaje.id_solicitud) \
            .outerjoin(Veterinario, Veterinario.id_veterinario == Consulta.id_veterinario) \
            .filter(SolicitudAtencion.id_mascota == mascota_id) \
            .order_by(Consulta.fecha_consulta.desc()) \
            .limit(limit).all()

        resultado = []
        for cons, vet in consultas:
            # Evento de historial de esta consulta (peso/edad/observaciones registrados al atender).
            evento = db.query(HistorialClinico) \
                .filter(HistorialClinico.id_consulta == cons.id_consulta) \
                .order_by(HistorialClinico.fecha_evento) \
                .first()

            # Diagnósticos de la consulta, con la patología asociada.
            diags = db.query(Diagnostico, Patologia) \
                .outerjoin(Patologia, Patologia.id_patologia == Diagnostico.id_patologia) \
                .filter(Diagnostico.id_consulta == cons.id_consulta) \
                .order_by(Diagnostico.fecha_diagnostico) \
                .all()

            diagnosticos = [
                {
                    "id_diagnostico": d.id_diagnostico,
                    "diagnostico": d.diagnostico,
                    "tipo_diagnostico": d.tipo_diagnostico,
                    "estado_patologia": d.estado_patologia,
                    "fecha_diagnostico": d.fecha_diagnostico,
                    "patologia": {
                        "nombre": p.nombre_patologia,
                        "gravedad": p.gravedad,
                        "especie_afecta": p.especie_afecta,
                        "es_contagiosa": p.es_contagiosa,
                        "es_cronica": p.es_crónica,
                    } if p else None,
                }
                for d, p in diags
            ]

            resultado.append({
                "id_consulta": cons.id_consulta,
                "fecha_consulta": cons.fecha_consulta,
                "tipo_consulta": cons.tipo_consulta,
                "motivo_consulta": cons.motivo_consulta,
                "sintomas_observados": cons.sintomas_observados,
                "diagnostico_preliminar": cons.diagnostico_preliminar,
                "observaciones": cons.observaciones,
                "condicion_general": cons.condicion_general,
                "es_seguimiento": cons.es_seguimiento,
                "veterinario": f"{vet.nombre} {vet.apellido_paterno}" if vet else None,
                "edad_meses": evento.edad_meses if evento else None,
                "peso_momento": float(evento.peso_momento) if evento and evento.peso_momento else None,
                "observaciones_historial": evento.observaciones if evento else None,
                "diagnosticos": diagnosticos,
            })

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial detallado: {str(e)}"
        )
