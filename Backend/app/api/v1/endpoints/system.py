# app/api/v1/endpoints/system.py
"""Endpoints de sistema: raíz, salud y estadísticas generales de la API."""
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.database import get_db

router = APIRouter()


@router.get("/api/v1/")
async def v1_root():
    return {"message": "Bienvenido a la API v1", "docs": "/docs"}


@router.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "🏥 Sistema Veterinaria API COMPLETO funcionando!",
        "version": "2.0.0",
        "status": "✅ Operativo",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Endpoint de salud del sistema"""
    try:
        # Verificar conexión a la base de datos
        db.execute(text("SELECT 1"))
        db_status = "✅ Conectada"
    except Exception as e:
        db_status = f"❌ Error: {str(e)}"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.0.0"
    }


@router.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Estadísticas generales del sistema"""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "system_info": {"environment": os.getenv("ENVIRONMENT", "development")}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")
