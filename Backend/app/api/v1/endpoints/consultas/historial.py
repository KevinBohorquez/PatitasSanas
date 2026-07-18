# app/api/v1/endpoints/consultas/historial.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.config.database import get_db
from app.queries import historial_queries

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
        resultados = historial_queries.listar_historial(
            db, mascota_id=mascota_id, fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta, limit=limit
        )

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
        eventos = historial_queries.listar_consultas(db, mascota_id=mascota_id, limit=limit)

        # Si la mascota no tiene consultas, devolver lista vacía (HTTP 200) en lugar
        # de 404, para que el front muestre un historial vacío y no un error.
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
        consultas = historial_queries.listar_consultas_con_veterinario(
            db, mascota_id=mascota_id, limit=limit
        )

        resultado = []
        for cons, vet in consultas:
            # Evento de historial de esta consulta (peso/edad/observaciones registrados al atender).
            evento = historial_queries.get_evento_historial_consulta(db, consulta_id=cons.id_consulta)

            # Diagnósticos de la consulta, con la patología asociada.
            diags = historial_queries.listar_diagnosticos_consulta(db, consulta_id=cons.id_consulta)

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
