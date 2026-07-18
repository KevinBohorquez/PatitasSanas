# app/api/v1/endpoints/catalogos/especialidades.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.crud.catalogo_crud import especialidad
from app.schemas.catalogo_schemas import (
    EspecialidadCreate, EspecialidadResponse
)

router = APIRouter()

# ===== ENDPOINTS PARA ESPECIALIDAD =====

@router.post("/especialidades/", response_model=EspecialidadResponse, status_code=status.HTTP_201_CREATED)
async def create_especialidad(
        especialidad_data: EspecialidadCreate,
        db: Session = Depends(get_db)
):
    """Crear una nueva especialidad"""
    try:
        # Validar duplicados
        if especialidad.exists_by_descripcion(db, descripcion=especialidad_data.descripcion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una especialidad con esa descripción"
            )

        return especialidad.create(db, obj_in=especialidad_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear especialidad: {str(e)}"
        )


@router.get("/especialidades/", response_model=List[EspecialidadResponse])
async def get_especialidades(db: Session = Depends(get_db)):
    """Obtener lista de especialidades"""
    try:
        return especialidad.get_all_ordenadas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener especialidades: {str(e)}"
        )


@router.get("/especialidades/{especialidad_id}", response_model=EspecialidadResponse)
async def get_especialidad(
        especialidad_id: int,
        db: Session = Depends(get_db)
):
    """Obtener una especialidad específica por ID"""
    try:
        especialidad_obj = especialidad.get(db, especialidad_id)
        if not especialidad_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Especialidad no encontrada"
            )
        return especialidad_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener especialidad: {str(e)}"
        )


@router.get("/especialidades/search/{termino}")
async def search_especialidades(
        termino: str,
        db: Session = Depends(get_db)
):
    """Buscar especialidades por descripción"""
    try:
        especialidades_encontradas = especialidad.search_especialidades(db, descripcion=termino)
        return {
            "termino_busqueda": termino,
            "especialidades": especialidades_encontradas,
            "total": len(especialidades_encontradas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de especialidades: {str(e)}"
        )


@router.get("/especialidades/estadisticas/veterinarios")
async def get_especialidades_con_veterinarios_count(db: Session = Depends(get_db)):
    """Obtener especialidades con conteo de veterinarios"""
    try:
        return especialidad.get_especialidades_con_veterinarios_count(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/especialidades/demandadas/top")
async def get_especialidades_mas_demandadas(
        db: Session = Depends(get_db),
        limit: int = Query(5, ge=1, le=20, description="Límite de resultados")
):
    """Obtener especialidades más demandadas"""
    try:
        return especialidad.get_mas_demandadas(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener especialidades demandadas: {str(e)}"
        )
