# app/crud/consulta/solicitud_atencion.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.crud.base_crud import CRUDBase
from app.models.solicitud_atencion import SolicitudAtencion
from app.schemas.consulta_schema import SolicitudAtencionCreate


# ===== SOLICITUD ATENCIÓN COMPLETO =====
class CRUDSolicitudAtencion(CRUDBase[SolicitudAtencion, SolicitudAtencionCreate, None]):

    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[SolicitudAtencion]:
        """Obtener solicitudes por mascota"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.id_mascota == mascota_id) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_by_tipo(self, db: Session, *, tipo_solicitud: str) -> List[SolicitudAtencion]:
        """Obtener solicitudes por tipo"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_by_estado(self, db: Session, *, estado: str) -> List[SolicitudAtencion]:
        """Obtener solicitudes por estado"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == estado) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def cambiar_estado(self, db: Session, *, solicitud_id: int, nuevo_estado: str) -> Optional[SolicitudAtencion]:
        """Cambiar estado de la solicitud"""
        solicitud = self.get(db, solicitud_id)
        if solicitud:
            solicitud.estado = nuevo_estado
            db.commit()
            db.refresh(solicitud)
        return solicitud


solicitud_atencion = CRUDSolicitudAtencion(SolicitudAtencion)
