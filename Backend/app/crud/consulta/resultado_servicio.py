# app/crud/consulta/resultado_servicio.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from datetime import date, timedelta
from app.crud.base_crud import CRUDBase
from app.models.resultado_servicio import ResultadoServicio
from app.schemas.consulta_schema import ResultadoServicioCreate


# ===== RESULTADO SERVICIO COMPLETO =====
class CRUDResultadoServicio(CRUDBase[ResultadoServicio, ResultadoServicioCreate, None]):

    def get_by_veterinario(self, db: Session, *, veterinario_id: int) -> List[ResultadoServicio]:
        """Obtener resultados realizados por un veterinario"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.id_veterinario == veterinario_id) \
            .order_by(desc(ResultadoServicio.fecha_realizacion)).all()

    def get_recientes(self, db: Session, *, dias: int = 7) -> List[ResultadoServicio]:
        """Obtener resultados recientes"""
        fecha_limite = date.today() - timedelta(days=dias)
        return db.query(ResultadoServicio).filter(
            func.date(ResultadoServicio.fecha_realizacion) >= fecha_limite
        ).order_by(desc(ResultadoServicio.fecha_realizacion)).all()


resultado_servicio = CRUDResultadoServicio(ResultadoServicio)
