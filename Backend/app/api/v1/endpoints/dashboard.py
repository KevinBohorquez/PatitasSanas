from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.config.database import get_db
from app.crud.dashboard_crud import dashboard

router = APIRouter()

@router.get("/tasa-asistencia")
def get_tasa_asistencia(db: Session = Depends(get_db)):
    try:
        return dashboard.get_tasa_asistencia(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats-generales")
def get_stats_generales(db: Session = Depends(get_db)):
    try:
        return dashboard.get_stats_generales(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servicios-mas-solicitados")
def get_servicios_mas_solicitados(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    try:
        return dashboard.get_servicios_mas_solicitados(db, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mascotas-por-especie")
def get_mascotas_por_especie(db: Session = Depends(get_db)):
    try:
        return dashboard.get_mascotas_por_especie(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingresos-por-servicio")
def get_ingresos_por_servicio(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        return dashboard.get_ingresos_por_servicio(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))