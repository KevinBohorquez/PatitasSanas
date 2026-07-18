# app/api/v1/endpoints/catalogos/patologias.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud.catalogo_crud import patologia
from app.schemas.catalogo_schemas import (
    PatologiaCreate, PatologiaResponse
)

router = APIRouter()

# ===== ENDPOINTS PARA PATOLOGÍA =====

@router.post("/patologias/", response_model=PatologiaResponse, status_code=status.HTTP_201_CREATED)
async def create_patologia(
        patologia_data: PatologiaCreate,
        db: Session = Depends(get_db)
):
    """Crear una nueva patología"""
    try:
        # Validar duplicados
        if patologia.exists_by_nombre(db, nombre_patologia=patologia_data.nombre_patologia):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una patología con ese nombre"
            )

        return patologia.create(db, obj_in=patologia_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear patología: {str(e)}"
        )


@router.get("/patologias/", response_model=List[PatologiaResponse])
async def get_patologias(db: Session = Depends(get_db)):
    """Obtener lista de patologías"""
    try:
        return patologia.get_all_ordenadas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías: {str(e)}"
        )


@router.get("/patologias/{patologia_id}", response_model=PatologiaResponse)
async def get_patologia(
        patologia_id: int,
        db: Session = Depends(get_db)
):
    """Obtener una patología específica por ID"""
    try:
        patologia_obj = patologia.get(db, patologia_id)
        if not patologia_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patología no encontrada"
            )
        return patologia_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patología: {str(e)}"
        )


@router.get("/patologias/especie/{especie}")
async def get_patologias_by_especie(
        especie: str,
        db: Session = Depends(get_db)
):
    """Obtener patologías por especie"""
    try:
        if especie not in ['Perro', 'Gato', 'Ambas']:
            raise HTTPException(
                status_code=400,
                detail="Especie debe ser 'Perro', 'Gato' o 'Ambas'"
            )

        patologias_encontradas = patologia.get_by_especie(db, especie=especie)
        return {
            "especie": especie,
            "patologias": patologias_encontradas,
            "total": len(patologias_encontradas)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías por especie: {str(e)}"
        )


@router.get("/patologias/gravedad/{gravedad}")
async def get_patologias_by_gravedad(
        gravedad: str,
        db: Session = Depends(get_db)
):
    """Obtener patologías por gravedad"""
    try:
        if gravedad not in ['Leve', 'Moderada', 'Grave', 'Critica']:
            raise HTTPException(
                status_code=400,
                detail="Gravedad debe ser 'Leve', 'Moderada', 'Grave' o 'Critica'"
            )

        patologias_encontradas = patologia.get_by_gravedad(db, gravedad=gravedad)
        return {
            "gravedad": gravedad,
            "patologias": patologias_encontradas,
            "total": len(patologias_encontradas)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías por gravedad: {str(e)}"
        )


@router.get("/patologias/cronicas/list")
async def get_patologias_cronicas(db: Session = Depends(get_db)):
    """Obtener patologías crónicas"""
    try:
        patologias_cronicas = patologia.get_cronicas(db)
        return {
            "patologias_cronicas": patologias_cronicas,
            "total": len(patologias_cronicas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías crónicas: {str(e)}"
        )


@router.get("/patologias/contagiosas/list")
async def get_patologias_contagiosas(db: Session = Depends(get_db)):
    """Obtener patologías contagiosas"""
    try:
        patologias_contagiosas = patologia.get_contagiosas(db)
        return {
            "patologias_contagiosas": patologias_contagiosas,
            "total": len(patologias_contagiosas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías contagiosas: {str(e)}"
        )


@router.get("/patologias/search/avanzada")
async def search_patologias_avanzada(
        db: Session = Depends(get_db),
        nombre: Optional[str] = Query(None, description="Buscar por nombre"),
        especie: Optional[str] = Query(None, description="Filtrar por especie"),
        gravedad: Optional[str] = Query(None, description="Filtrar por gravedad")
):
    """Buscar patologías con filtros múltiples"""
    try:
        patologias_encontradas = patologia.search_patologias(
            db,
            nombre=nombre,
            especie=especie,
            gravedad=gravedad
        )
        return {
            "filtros": {
                "nombre": nombre,
                "especie": especie,
                "gravedad": gravedad
            },
            "patologias": patologias_encontradas,
            "total": len(patologias_encontradas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda avanzada de patologías: {str(e)}"
        )


@router.get("/patologias/estadisticas/general")
async def get_patologias_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas generales de patologías"""
    try:
        return patologia.get_estadisticas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas de patologías: {str(e)}"
        )


@router.get("/patologias/diagnosticadas/top")
async def get_patologias_mas_diagnosticadas(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """Obtener patologías más diagnosticadas"""
    try:
        return patologia.get_mas_diagnosticadas(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías más diagnosticadas: {str(e)}"
        )
