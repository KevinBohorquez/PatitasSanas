# app/crud/consulta/servicio_solicitado.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.crud.base_crud import CRUDBase
from app.models.servicio_solicitado import ServicioSolicitado
from app.schemas.consulta_schema import ServicioSolicitadoCreate


# ===== SERVICIO SOLICITADO COMPLETO =====
class CRUDServicioSolicitado(CRUDBase[ServicioSolicitado, ServicioSolicitadoCreate, None]):

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[ServicioSolicitado]:
        """Obtener servicios solicitados de una consulta"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_consulta == consulta_id) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def get_by_estado(self, db: Session, *, estado_examen: str) -> List[ServicioSolicitado]:
        """Obtener servicios por estado de examen"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.estado_examen == estado_examen) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def cambiar_estado(self, db: Session, *, servicio_solicitado_id: int, nuevo_estado: str) -> Optional[
        ServicioSolicitado]:
        """Cambiar estado del servicio solicitado"""
        servicio_sol = self.get(db, servicio_solicitado_id)
        if servicio_sol:
            servicio_sol.estado_examen = nuevo_estado
            db.commit()
            db.refresh(servicio_sol)
        return servicio_sol


servicio_solicitado = CRUDServicioSolicitado(ServicioSolicitado)
