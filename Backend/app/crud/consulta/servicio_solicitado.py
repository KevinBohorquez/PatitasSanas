# app/crud/consulta/servicio_solicitado.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.crud.base_crud import CRUDBase
from app.models.servicio_solicitado import ServicioSolicitado
from app.models.cita import Cita
from app.schemas.consulta_schema import ServicioSolicitadoCreate


# ===== SERVICIO SOLICITADO COMPLETO =====
class CRUDServicioSolicitado(CRUDBase[ServicioSolicitado, ServicioSolicitadoCreate, None]):

    def get_all(self, db: Session) -> List[ServicioSolicitado]:
        """Obtener todos los servicios solicitados."""
        return db.query(ServicioSolicitado).all()

    def get_con_cita(self, db: Session) -> List[ServicioSolicitado]:
        """Servicios solicitados que tienen una cita asociada."""
        return db.query(ServicioSolicitado) \
            .join(Cita, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado).all()

    def get_con_cita_by_id(self, db: Session, *, id_servicio_solicitado: int) -> Optional[ServicioSolicitado]:
        """Un servicio solicitado con cita asociada, por id."""
        return db.query(ServicioSolicitado) \
            .join(Cita, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .filter(ServicioSolicitado.id_servicio_solicitado == id_servicio_solicitado).first()

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[ServicioSolicitado]:
        """Obtener servicios solicitados de una consulta"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_consulta == consulta_id) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def count_by_servicio(self, db: Session, *, servicio_id: int) -> int:
        """Contar cuántos servicios solicitados usan un servicio dado."""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_servicio == servicio_id).count()

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
