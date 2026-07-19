# app/api/v1/endpoints/catalogos/general.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.raza import Raza
from app.models.tipo_animal import TipoAnimal
from app.models.especialidad import Especialidad
from app.models.tipo_servicio import TipoServicio
from app.models.servicio import Servicio
from app.models.patologia import Patologia
from app.models.cliente_mascota import ClienteMascota

router = APIRouter()

# ===== ENDPOINTS GENERALES =====

@router.get("/debug/info")
async def debug_catalogos_info(db: Session = Depends(get_db)):
    """Endpoint para depurar información de las tablas de catálogo"""
    try:
        info = {}

        tablas = [
            ("Raza", Raza),
            ("Tipo_animal", TipoAnimal),
            ("Especialidad", Especialidad),
            ("Tipo_servicio", TipoServicio),
            ("Servicio", Servicio),
            ("Patologia", Patologia),
            ("Cliente_Mascota", ClienteMascota)
        ]

        for tabla_nombre, tabla_modelo in tablas:
            try:
                count = db.query(tabla_modelo).count()
                info[tabla_nombre] = {
                    "total_records": count,
                    "status": "OK"
                }
            except Exception as e:
                info[tabla_nombre] = {
                    "total_records": 0,
                    "status": f"Error: {str(e)}"
                }

        return {
            "debug_info": info,
            "timestamp": "2024-06-09"
        }

    except Exception as e:
        return {
            "error": f"Error al obtener información de debug: {str(e)}"
        }
