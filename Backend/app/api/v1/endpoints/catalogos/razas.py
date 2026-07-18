# app/api/v1/endpoints/catalogos/razas.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.crud.catalogo_crud import raza
from app.schemas.catalogo_schemas import (
    RazaCreate, RazaResponse
)

router = APIRouter()

# ===== ENDPOINTS PARA RAZA =====

@router.post("/razas/", response_model=RazaResponse, status_code=status.HTTP_201_CREATED)
async def create_raza(
        raza_data: RazaCreate,
        db: Session = Depends(get_db)
):
    """Crear una nueva raza"""
    try:
        # Validar duplicados
        if raza.exists_by_nombre(db, nombre_raza=raza_data.nombre_raza):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una raza con ese nombre"
            )

        return raza.create(db, obj_in=raza_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear raza: {str(e)}"
        )


@router.get("/razas/", response_model=List[RazaResponse])
async def get_razas(
        db: Session = Depends(get_db),
        ordenadas: bool = Query(True, description="Ordenar alfabéticamente")
):
    """Obtener lista de razas"""
    try:
        if ordenadas:
            return raza.get_all_ordenadas(db)
        else:
            return raza.get_multi(db, limit=1000)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener razas: {str(e)}"
        )


@router.get("/razas/{raza_id}", response_model=RazaResponse)
async def get_raza(
        raza_id: int,
        db: Session = Depends(get_db)
):
    """Obtener una raza específica por ID"""
    try:
        raza_obj = raza.get(db, raza_id)
        if not raza_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raza no encontrada"
            )
        return raza_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener raza: {str(e)}"
        )


@router.get("/razas/nombre/{nombre}")
async def get_raza_by_nombre(
        nombre: str,
        db: Session = Depends(get_db)
):
    """Obtener raza por nombre"""
    try:
        raza_obj = raza.get_by_nombre(db, nombre_raza=nombre)
        if not raza_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raza no encontrada"
            )
        return raza_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar raza: {str(e)}"
        )


@router.get("/razas/search/{termino}")
async def search_razas(
        termino: str,
        db: Session = Depends(get_db)
):
    """Buscar razas por nombre (parcial)"""
    try:
        razas_encontradas = raza.search_razas(db, nombre=termino)
        return {
            "termino_busqueda": termino,
            "razas": razas_encontradas,
            "total": len(razas_encontradas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de razas: {str(e)}"
        )


@router.get("/razas/estadisticas/mascotas")
async def get_razas_con_mascotas_count(db: Session = Depends(get_db)):
    """Obtener razas con conteo de mascotas"""
    try:
        return raza.get_razas_con_mascotas_count(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas de razas: {str(e)}"
        )


@router.get("/razas/populares/top")
async def get_razas_populares(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """Obtener razas más populares"""
    try:
        return raza.get_razas_populares(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener razas populares: {str(e)}"
        )
