# app/api/v1/endpoints/catalogos/tipos_animal.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.crud.catalogo import tipo_animal
from app.schemas.catalogo_schemas import (
    TipoAnimalCreate, TipoAnimalResponse
)

router = APIRouter()

# ===== ENDPOINTS PARA TIPO ANIMAL =====

@router.post("/tipos-animal/", response_model=TipoAnimalResponse, status_code=status.HTTP_201_CREATED)
async def create_tipo_animal(
        tipo_data: TipoAnimalCreate,
        db: Session = Depends(get_db)
):
    """Crear un nuevo tipo de animal"""
    try:
        # Validar que no existe la combinación
        if tipo_animal.exists_combination(db, raza_id=tipo_data.id_raza, descripcion=tipo_data.descripcion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe esa combinación de raza y tipo de animal"
            )

        return tipo_animal.create(db, obj_in=tipo_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tipo de animal: {str(e)}"
        )


@router.get("/tipos-animal/", response_model=List[TipoAnimalResponse])
async def get_tipos_animal(db: Session = Depends(get_db)):
    """Obtener lista de tipos de animal"""
    try:
        return tipo_animal.get_multi(db, limit=1000)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos de animal: {str(e)}"
        )


@router.get("/tipos-animal/raza/{raza_id}")
async def get_tipos_animal_by_raza(
        raza_id: int,
        db: Session = Depends(get_db)
):
    """Obtener tipos de animal por raza"""
    try:
        tipos = tipo_animal.get_by_raza(db, raza_id=raza_id)
        return {
            "id_raza": raza_id,
            "tipos_animal": tipos,
            "total": len(tipos)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos por raza: {str(e)}"
        )


@router.get("/tipos-animal/descripcion/{descripcion}")
async def get_tipos_animal_by_descripcion(
        descripcion: str,
        db: Session = Depends(get_db)
):
    """Obtener tipos de animal por descripción (Perro/Gato)"""
    try:
        if descripcion not in ['Perro', 'Gato']:
            raise HTTPException(
                status_code=400,
                detail="Descripción debe ser 'Perro' o 'Gato'"
            )

        tipos = tipo_animal.get_by_descripcion(db, descripcion=descripcion)
        return {
            "descripcion": descripcion,
            "tipos_animal": tipos,
            "total": len(tipos)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos por descripción: {str(e)}"
        )


@router.get("/tipos-animal/with-raza-info/list")
async def get_tipos_animal_with_raza_info(db: Session = Depends(get_db)):
    """Obtener tipos de animal con información de raza"""
    try:
        return tipo_animal.get_with_raza_info(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos con info de raza: {str(e)}"
        )


@router.get("/tipos-animal/estadisticas/general")
async def get_tipos_animal_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas de tipos de animal"""
    try:
        return tipo_animal.get_estadisticas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
