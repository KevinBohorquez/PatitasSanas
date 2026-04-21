from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.config.database import get_db
from app.crud.consulta_crud import (
    triaje
)
from app.models import Triaje

from app.schemas.consulta_schema import (
    TriajeResponse, TriajeCreate, TriajeUpdate
)

router = APIRouter()

@router.post("/", response_model=TriajeResponse, status_code=status.HTTP_201_CREATED)
async def create_triaje(
        triaje_data: TriajeCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo triaje
    """
    try:
        # Verificar que la solicitud existe
        from app.crud.consulta_crud import solicitud_atencion
        solicitud_obj = solicitud_atencion.get(db, triaje_data.id_solicitud)
        if not solicitud_obj:
            raise HTTPException(
                status_code=400,
                detail="Solicitud de atención no encontrada"
            )

        # Verificar que el veterinario existe
        from app.crud.veterinario_crud import veterinario
        veterinario_obj = veterinario.get(db, triaje_data.id_veterinario)
        if not veterinario_obj:
            raise HTTPException(
                status_code=400,
                detail="Veterinario no encontrado"
            )

        # Verificar que no exista ya un triaje para esta solicitud
        triaje_existente = triaje.get_by_solicitud(db, solicitud_id=triaje_data.id_solicitud)
        if triaje_existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un triaje para esta solicitud"
            )

        # Crear el triaje
        triaje_dict = triaje_data.dict()

        # Asignar fecha actual si no se proporciona
        if not triaje_dict.get("fecha_hora_triaje"):
            triaje_dict["fecha_hora_triaje"] = datetime.now()

        nuevo_triaje = triaje.create(db, obj_in=triaje_dict)

        return nuevo_triaje

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear triaje: {str(e)}"
        )


@router.get("/", response_model=List[TriajeResponse])
async def get_triajes(
        db: Session = Depends(get_db),
        clasificacion_urgencia: Optional[str] = Query(None, description="Filtrar por clasificación de urgencia"),
        veterinario_id: Optional[int] = Query(None, description="Filtrar por veterinario"),
        solicitud_id: Optional[int] = Query(None, description="Filtrar por solicitud"),
        condicion_corporal: Optional[str] = Query(None, description="Filtrar por condición corporal"),
        fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicio para filtrar"),
        fecha_fin: Optional[datetime] = Query(None, description="Fecha fin para filtrar"),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener lista de triajes con filtros opcionales
    """
    try:
        # Filtrar por solicitud específica
        if solicitud_id:
            triaje_obj = triaje.get_by_solicitud(db, solicitud_id=solicitud_id)
            return [triaje_obj] if triaje_obj else []

        # Filtrar por veterinario
        elif veterinario_id:
            triajes = triaje.get_by_veterinario(db, veterinario_id=veterinario_id)
            return triajes[:limit]

        # Filtrar por clasificación de urgencia
        elif clasificacion_urgencia:
            triajes = triaje.get_by_clasificacion_urgencia(db, clasificacion=clasificacion_urgencia)
            return triajes[:limit]

        # Filtrar por condición corporal
        elif condicion_corporal:
            triajes = triaje.get_by_condicion_corporal(db, condicion=condicion_corporal)
            return triajes[:limit]

        # Filtrar por rango de fechas
        elif fecha_inicio and fecha_fin:
            triajes = triaje.get_by_fecha_rango(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
            return triajes[:limit]

        # Obtener todos los triajes
        else:
            triajes = triaje.get_multi(db, limit=limit)
            return triajes

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triajes: {str(e)}"
        )

@router.get("/{triaje_id}", response_model=TriajeResponse)
async def get_triaje(
    triaje_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un triaje específico por ID
    """
    try:
        triaje_obj = triaje.get(db, id=triaje_id)
        if not triaje_obj:
            raise HTTPException(
                status_code=404,
                detail="Triaje no encontrado"
            )
        return triaje_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triaje: {str(e)}"
        )

@router.get("/{triaje_id}", response_model=TriajeResponse)
async def get_triaje(
    triaje_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un triaje específico por ID
    """
    try:
        triaje_obj = triaje.get(db, id=triaje_id)
        if not triaje_obj:
            raise HTTPException(
                status_code=404,
                detail="Triaje no encontrado"
            )
        return triaje_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triaje: {str(e)}"
        )


@router.put("/triaje/{triaje_id}", response_model=TriajeResponse)
async def update_triaje(
        triaje_id: int,
        triaje_data: TriajeUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un triaje existente
    """
    try:
        # Verificar que el triaje existe
        triaje_obj = triaje.get(db, id=triaje_id)
        if not triaje_obj:
            raise HTTPException(
                status_code=404,
                detail="Triaje no encontrado"
            )

        # Si se actualiza el veterinario, verificar que existe
        if triaje_data.id_veterinario and triaje_data.id_veterinario != triaje_obj.id_veterinario:
            from app.crud.veterinario_crud import veterinario
            veterinario_obj = veterinario.get(db, triaje_data.id_veterinario)
            if not veterinario_obj:
                raise HTTPException(
                    status_code=400,
                    detail="Veterinario no encontrado"
                )

        # Actualizar el triaje
        triaje_actualizado = triaje.update(db, db_obj=triaje_obj, obj_in=triaje_data)

        return triaje_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar triaje: {str(e)}"
        )


@router.get("/consulta/{id_solicitud}", response_model=TriajeResponse)
async def get_triaje_por_consulta_id(
    id_solicitud: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un triaje específico por ID de consulta
    """
    try:
        consulta_obj = db.query(Triaje).filter(Triaje.id_solicitud == id_solicitud).first()
        if not consulta_obj:
            raise HTTPException(
                status_code=404,
                detail="Triaje no encontrado"
            )
        return consulta_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triaje: {str(e)}"
        )
