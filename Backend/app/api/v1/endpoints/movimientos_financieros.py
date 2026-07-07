from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.config.database import get_db
from app.crud.movimiento_financiero_crud import movimiento_financiero
from app.schemas.movimiento_financiero_schema import (
    MovimientoFinancieroResponse, MovimientoFinancieroCreate, MovimientoFinancieroUpdate
)

router = APIRouter()


@router.get("/resumen")
async def get_resumen_financiero(
    db: Session = Depends(get_db),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)")
):
    try:
        resumen = movimiento_financiero.get_resumen(db, fecha_desde, fecha_hasta)
        return resumen
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resumen financiero: {str(e)}"
        )


@router.get("/", response_model=List[MovimientoFinancieroResponse])
async def get_movimientos(
    db: Session = Depends(get_db),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (Ingreso/Egreso)"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500, description="Limite de resultados")
):
    try:
        if tipo:
            movimientos = movimiento_financiero.get_by_tipo(db, tipo=tipo)
        elif categoria:
            movimientos = movimiento_financiero.get_by_categoria(db, categoria=categoria)
        elif fecha_desde and fecha_hasta:
            movimientos = movimiento_financiero.get_by_fecha_range(
                db, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
            )
        else:
            movimientos = movimiento_financiero.get_recientes(db, limit=limit)

        return movimientos[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener movimientos: {str(e)}"
        )


@router.get("/{movimiento_id}", response_model=MovimientoFinancieroResponse)
async def get_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db)
):
    try:
        movimiento = movimiento_financiero.get(db, movimiento_id)
        if not movimiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento no encontrado"
            )
        return movimiento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener movimiento: {str(e)}"
        )


@router.post("/", response_model=MovimientoFinancieroResponse, status_code=status.HTTP_201_CREATED)
async def create_movimiento(
    movimiento_data: MovimientoFinancieroCreate,
    db: Session = Depends(get_db)
):
    try:
        movimiento_dict = movimiento_data.model_dump()
        if not movimiento_dict.get('fecha_movimiento'):
            movimiento_dict['fecha_movimiento'] = datetime.now()

        nuevo = movimiento_financiero.create(db, obj_in=movimiento_dict)
        return nuevo
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear movimiento: {str(e)}"
        )


@router.put("/{movimiento_id}", response_model=MovimientoFinancieroResponse)
async def update_movimiento(
    movimiento_id: int,
    movimiento_data: MovimientoFinancieroUpdate,
    db: Session = Depends(get_db)
):
    try:
        movimiento_obj = movimiento_financiero.get(db, movimiento_id)
        if not movimiento_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento no encontrado"
            )
        actualizado = movimiento_financiero.update(
            db, db_obj=movimiento_obj, obj_in=movimiento_data
        )
        return actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar movimiento: {str(e)}"
        )


@router.delete("/{movimiento_id}")
async def delete_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db)
):
    try:
        movimiento_obj = movimiento_financiero.get(db, movimiento_id)
        if not movimiento_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento no encontrado"
            )
        movimiento_financiero.remove(db, id=movimiento_id)
        return {"message": "Movimiento eliminado correctamente", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar movimiento: {str(e)}"
        )
