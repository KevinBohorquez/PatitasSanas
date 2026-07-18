# app/crud/consulta/tratamiento.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import date, timedelta
from app.crud.base_crud import CRUDBase
from app.models.tratamiento import Tratamiento
from app.schemas.consulta_schema import TratamientoCreate


# ===== TRATAMIENTO COMPLETO =====
class CRUDTratamiento(CRUDBase[Tratamiento, TratamientoCreate, None]):

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[Tratamiento]:
        """Obtener tratamientos de una consulta"""
        return db.query(Tratamiento).filter(Tratamiento.id_consulta == consulta_id) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_by_tipo(self, db: Session, *, tipo_tratamiento: str) -> List[Tratamiento]:
        """Obtener tratamientos por tipo"""
        return db.query(Tratamiento).filter(Tratamiento.tipo_tratamiento == tipo_tratamiento) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_activos(self, db: Session) -> List[Tratamiento]:
        """Obtener tratamientos activos (iniciados recientemente)"""
        return db.query(Tratamiento).filter(Tratamiento.fecha_inicio <= date.today()) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_recientes(self, db: Session, *, dias: int = 30) -> List[Tratamiento]:
        """Obtener tratamientos iniciados en los últimos X días"""
        fecha_limite = date.today() - timedelta(days=dias)
        return db.query(Tratamiento).filter(Tratamiento.fecha_inicio >= fecha_limite) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()


tratamiento = CRUDTratamiento(Tratamiento)
