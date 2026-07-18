# app/api/v1/endpoints/catalogos/tipos_servicio.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.crud.catalogo_crud import tipo_servicio
from app.schemas.catalogo_schemas import (
    TipoServicioCreate, TipoServicioResponse
)

router = APIRouter()

# ===== ENDPOINTS PARA TIPO SERVICIO =====

@router.post("/tipos-servicio/", response_model=TipoServicioResponse, status_code=status.HTTP_201_CREATED)
async def create_tipo_servicio(
        tipo_servicio_data: TipoServicioCreate,
        db: Session = Depends(get_db)
):
    """Crear un nuevo tipo de servicio"""
    try:
        # Validar duplicados
        if tipo_servicio.exists_by_descripcion(db, descripcion=tipo_servicio_data.descripcion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un tipo de servicio con esa descripción"
            )

        return tipo_servicio.create(db, obj_in=tipo_servicio_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tipo de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/", response_model=List[TipoServicioResponse])
async def get_tipos_servicio(db: Session = Depends(get_db)):
    """Obtener lista de tipos de servicio"""
    try:
        return tipo_servicio.get_all_ordenados(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/{tipo_servicio_id}", response_model=TipoServicioResponse)
async def get_tipo_servicio(
        tipo_servicio_id: int,
        db: Session = Depends(get_db)
):
    """Obtener un tipo de servicio específico por ID"""
    try:
        tipo_servicio_obj = tipo_servicio.get(db, tipo_servicio_id)
        if not tipo_servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de servicio no encontrado"
            )
        return tipo_servicio_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipo de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/search/{termino}")
async def search_tipos_servicio(
        termino: str,
        db: Session = Depends(get_db)
):
    """Buscar tipos de servicio por descripción"""
    try:
        tipos_encontrados = tipo_servicio.search_tipos(db, descripcion=termino)
        return {
            "termino_busqueda": termino,
            "tipos_servicio": tipos_encontrados,
            "total": len(tipos_encontrados)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de tipos de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/estadisticas/servicios")
async def get_tipos_servicio_con_servicios_count(db: Session = Depends(get_db)):
    """Obtener tipos de servicio con conteo de servicios"""
    try:
        return tipo_servicio.get_tipos_con_servicios_count(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
