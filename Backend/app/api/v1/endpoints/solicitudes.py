# app/api/v1/endpoints/consultas.py - VERSIÓN CORREGIDA
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.config.database import get_db
from app.crud.consulta_crud import (
    solicitud_atencion
)
from app.models import Triaje, Veterinario, SolicitudAtencion

from app.schemas.consulta_schema import (
    SolicitudAtencionResponse, SolicitudAtencionCreate
)

router = APIRouter()

@router.post("/", response_model=SolicitudAtencionResponse, status_code=status.HTTP_201_CREATED)
async def create_solicitud_atencion(
        solicitud_data: SolicitudAtencionCreate,
        db: Session = Depends(get_db)
):
    """
    Crear una nueva solicitud de atención
    """
    try:
        # Verificar que la mascota existe
        from app.crud import mascota
        mascota_obj = mascota.get(db, solicitud_data.id_mascota)
        if not mascota_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mascota no encontrada"
            )

        # Verificar que la recepcionista existe
        from app.crud import recepcionista
        recep_obj = recepcionista.get(db, solicitud_data.id_recepcionista)
        if not recep_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recepcionista no encontrada"
            )

        # Agregar timestamp actual si no se proporciona
        solicitud_dict = solicitud_data.dict()
        solicitud_dict['fecha_hora_solicitud'] = solicitud_dict.get('fecha_hora_solicitud', datetime.now())
        solicitud_dict['estado'] = 'Pendiente'  # Estado inicial

        # Crear la solicitud
        nueva_solicitud = solicitud_atencion.create(db, obj_in=solicitud_dict)

        return nueva_solicitud

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear solicitud: {str(e)}"
        )


@router.get("/", response_model=List[SolicitudAtencionResponse])
async def get_solicitudes_atencion(
        db: Session = Depends(get_db),
        estado: Optional[str] = Query(None, description="Filtrar por estado"),
        tipo_solicitud: Optional[str] = Query(None, description="Filtrar por tipo"),
        mascota_id: Optional[int] = Query(None, description="Filtrar por mascota"),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener lista de solicitudes de atención con filtros
    """
    try:
        if estado:
            solicitudes = solicitud_atencion.get_by_estado(db, estado=estado)
        elif tipo_solicitud:
            solicitudes = solicitud_atencion.get_by_tipo(db, tipo_solicitud=tipo_solicitud)
        elif mascota_id:
            solicitudes = solicitud_atencion.get_by_mascota(db, mascota_id=mascota_id)
        else:
            solicitudes = solicitud_atencion.get_multi(db, limit=limit)

        return solicitudes[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes: {str(e)}"
        )


@router.get("/{solicitud_id}", response_model=SolicitudAtencionResponse)
async def get_solicitud_atencion(
        solicitud_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener una solicitud específica por ID
    """
    try:
        solicitud = solicitud_atencion.get(db, solicitud_id)
        if not solicitud:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )
        return solicitud

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitud: {str(e)}"
        )

@router.delete("/{solicitud_id}")
async def delete_solicitud(
        solicitud_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar una solicitud
    """
    solicitud_atencion_obj = solicitud_atencion.get(db, solicitud_id)
    if not solicitud_atencion_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )

    solicitud_atencion.remove(db, id=solicitud_id)
    return {"message": "Solicitud eliminada correctamente", "success": True}


@router.get("/veterinario/{id_usuario}", response_model=List[SolicitudAtencionResponse])
async def get_solicitudes_by_veterinario(
        id_usuario: int,
        estado: Optional[str] = Query(None, description="Filtrar por estado de la solicitud"),
        tipo_solicitud: Optional[str] = Query(None, description="Filtrar por tipo de solicitud"),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
        db: Session = Depends(get_db)
):
    """
    Obtener solicitudes de atención relacionadas con el veterinario por id_usuario.
    """
    try:
        # 1️⃣ Buscar el veterinario
        veterinario = db.query(Veterinario).filter(Veterinario.id_usuario == id_usuario).first()
        if not veterinario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        # 2️⃣ Buscar los triajes hechos por ese veterinario
        triajes = db.query(Triaje).filter(Triaje.id_veterinario == veterinario.id_veterinario).all()
        if not triajes:
            return []

        # 3️⃣ Obtener los IDs de solicitudes
        solicitud_ids = [triaje.id_solicitud for triaje in triajes]

        # 4️⃣ Consulta base de solicitudes
        query = db.query(SolicitudAtencion).filter(SolicitudAtencion.id_solicitud.in_(solicitud_ids))

        # 5️⃣ Filtros opcionales
        if estado:
            query = query.filter(SolicitudAtencion.estado == estado)
        if tipo_solicitud:
            query = query.filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud)

        solicitudes = query.limit(limit).all()

        return solicitudes

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes: {str(e)}"
        )
