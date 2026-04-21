from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import text
from starlette import status

from app.config.database import get_db

from app.models import Cita, ServicioSolicitado, Servicio, Consulta, Veterinario, ResultadoServicio

from app.schemas.consulta_schema import (
    ServicioSolicitadoUpdate, ServicioSolicitadoResponse, ServicioCitaCreate
)

router = APIRouter()

@router.get("/", response_model=List[ServicioSolicitadoResponse])
async def get_servicios_solicitados(db: Session = Depends(get_db)):
    """
    Obtener todos los servicios solicitados
    """
    try:
        servicios = db.query(ServicioSolicitado).all()
        return servicios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener servicios solicitados: {str(e)}")


# 1. Obtener todos los servicios solicitados que tienen citas
@router.get("/pendientes", response_model=List[ServicioSolicitadoResponse])
async def get_servicios_solicitados_pendientes(db: Session = Depends(get_db)):
    """
    Obtener todos los servicios solicitados que tienen citas asociadas
    Equivale a: SELECT * FROM Cita c INNER JOIN Servicio_Solicitado ON c.id_servicio_solicitado = Servicio_Solicitado.id_servicio_solicitado
    """
    try:
        servicios_con_cita = db.query(ServicioSolicitado) \
            .join(Cita, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .all()

        return servicios_con_cita

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener servicios solicitados con citas: {str(e)}")


# 2. Obtener un servicio solicitado específico que tenga cita
@router.get("/pendientes/{id_servicio_solicitado}", response_model=ServicioSolicitadoResponse)
async def get_servicio_solicitado_pendiente_por_id(id_servicio_solicitado: int, db: Session = Depends(get_db)):
    """
    Obtener un servicio solicitado específico que tenga cita asociada
    """
    try:
        servicio_con_cita = db.query(ServicioSolicitado) \
            .join(Cita, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .filter(ServicioSolicitado.id_servicio_solicitado == id_servicio_solicitado) \
            .first()

        if not servicio_con_cita:
            raise HTTPException(
                status_code=404,
                detail="Servicio solicitado no encontrado o no tiene cita asociada"
            )

        return servicio_con_cita

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener servicio solicitado: {str(e)}")

@router.put("/id_servicio_solicitado}", response_model=ServicioSolicitadoResponse)
async def update_servicio_solicitado(id_servicio_solicitado: int, servicio_solicitado: ServicioSolicitadoUpdate, db: Session = Depends(get_db)):
    """
    Actualizar un servicio solicitado
    """
    try:
        servicio = db.query(ServicioSolicitado).filter(ServicioSolicitado.id_servicio_solicitado == id_servicio_solicitado).first()

        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio solicitado no encontrado")

        # Actualizar los campos del servicio
        for key, value in servicio_solicitado.dict(exclude_unset=True).items():
            setattr(servicio, key, value)

        db.commit()
        db.refresh(servicio)

        return servicio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar servicio solicitado: {str(e)}")


@router.post("/consultas/{consulta_id}/servicio-cita", status_code=status.HTTP_201_CREATED)
async def create_servicio_cita(
        consulta_id: int,
        request_data: ServicioCitaCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un servicio solicitado y su cita correspondiente para una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = db.query(Consulta).filter(Consulta.id_consulta == consulta_id).first()
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        # Verificar que el servicio existe y está activo
        servicio_obj = db.query(Servicio).filter(
            Servicio.id_servicio == request_data.id_servicio,
            Servicio.activo == True
        ).first()
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado o inactivo"
            )

        # Verificar que el veterinario existe
        veterinario_obj = db.query(Veterinario).filter(
            Veterinario.id_veterinario == request_data.id_veterinario
        ).first()
        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        # Obtener id_mascota a través de joins: Consulta -> Triaje -> Solicitud_atencion -> Mascota
        result = db.execute(
            text("""
            SELECT sa.id_mascota 
            FROM Consulta c
            JOIN Triaje t ON c.id_triaje = t.id_triaje
            JOIN Solicitud_atencion sa ON t.id_solicitud = sa.id_solicitud
            WHERE c.id_consulta = :consulta_id
            """),
            {"consulta_id": consulta_id}
        ).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudo obtener la mascota asociada a la consulta"
            )

        id_mascota = result[0]

        # Crear el diccionario para Servicio_Solicitado
        servicio_solicitado_dict = {
            'id_consulta': consulta_id,
            'id_servicio': request_data.id_servicio,
            'fecha_solicitado': datetime.now(),
            'prioridad': request_data.prioridad,
            'estado_examen': 'Solicitado',  # Fijo como solicitaste
            'comentario_opcional': request_data.comentario_opcional
        }

        # Crear el servicio solicitado directamente con la sesión
        nuevo_servicio_solicitado = ServicioSolicitado(**servicio_solicitado_dict)
        db.add(nuevo_servicio_solicitado)
        db.flush()  # Para obtener el ID sin hacer commit

        # Crear el diccionario para Cita usando el ID del servicio_solicitado recién creado
        cita_dict = {
            'id_mascota': id_mascota,
            'id_servicio_solicitado': nuevo_servicio_solicitado.id_servicio_solicitado,
            'fecha_hora_programada': request_data.fecha_hora_programada,
            'estado_cita': 'Programada',  # Fijo como solicitaste
            'requiere_ayuno': request_data.requiere_ayuno,
            'observaciones': request_data.observaciones
        }

        # Crear la cita directamente con la sesión
        nueva_cita = Cita(**cita_dict)
        db.add(nueva_cita)
        db.flush()  # Para obtener el ID de la cita sin hacer commit

        # Crear el diccionario para Resultado_servicio
        resultado_servicio_dict = {
            'id_cita': nueva_cita.id_cita,
            'id_veterinario': request_data.id_veterinario,
            'fecha_realizacion': datetime.now()
        }

        # Crear el resultado de servicio directamente con la sesión
        nuevo_resultado = ResultadoServicio(**resultado_servicio_dict)
        db.add(nuevo_resultado)
        db.commit()  # Confirmar todas las operaciones

        return {
            "detail": "Servicio solicitado, cita y resultado creados exitosamente",
            "servicio_solicitado_id": nuevo_servicio_solicitado.id_servicio_solicitado,
            "cita_id": nueva_cita.id_cita,
            "resultado_id": nuevo_resultado.id_resultado
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear servicio solicitado y cita: {str(e)}"
        )