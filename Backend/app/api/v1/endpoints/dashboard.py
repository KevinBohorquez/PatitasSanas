from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.crud.dashboard_crud import dashboard

router = APIRouter()



@router.get("/tasa-asistencia")
def get_tasa_asistencia(db: Session = Depends(get_db)):
    try:
        return dashboard.get_tasa_asistencia(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
