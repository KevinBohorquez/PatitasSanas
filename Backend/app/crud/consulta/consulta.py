# app/crud/consulta/consulta.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Tuple, Dict
from datetime import date
from app.crud.base_crud import CRUDBase
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje
from app.models.consulta import Consulta
from app.schemas.consulta_schema import ConsultaCreate, ConsultaSearch


# ===== CONSULTA COMPLETO =====
class CRUDConsulta(CRUDBase[Consulta, ConsultaCreate, None]):

    def get_by_triaje(self, db: Session, *, triaje_id: int) -> Optional[Consulta]:
        """Obtener consulta por triaje"""
        return db.query(Consulta).filter(Consulta.id_triaje == triaje_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int, fecha_inicio: date = None,
                           fecha_fin: date = None) -> List[Consulta]:
        """Obtener consultas por veterinario en un rango de fechas"""
        query = db.query(Consulta).filter(Consulta.id_veterinario == veterinario_id)

        if fecha_inicio:
            query = query.filter(Consulta.fecha_consulta >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Consulta.fecha_consulta <= fecha_fin)

        return query.order_by(desc(Consulta.fecha_consulta)).all()

    def get_by_tipo(self, db: Session, *, tipo_consulta: str) -> List[Consulta]:
        """Obtener consultas por tipo"""
        return db.query(Consulta).filter(Consulta.tipo_consulta.ilike(f"%{tipo_consulta}%")) \
            .order_by(desc(Consulta.fecha_consulta)).all()

    def search_consultas(self, db: Session, *, search_params: ConsultaSearch) -> Tuple[List[Consulta], int]:
        """Buscar consultas con filtros"""
        query = db.query(Consulta)

        if search_params.id_mascota:
            # Join con triaje y solicitud para obtener id_mascota
            query = query.join(Triaje, Consulta.id_triaje == Triaje.id_triaje) \
                .join(SolicitudAtencion, Triaje.id_solicitud == SolicitudAtencion.id_solicitud) \
                .filter(SolicitudAtencion.id_mascota == search_params.id_mascota)

        if search_params.id_veterinario:
            query = query.filter(Consulta.id_veterinario == search_params.id_veterinario)

        if search_params.fecha_desde:
            query = query.filter(Consulta.fecha_consulta >= search_params.fecha_desde)

        if search_params.fecha_hasta:
            query = query.filter(Consulta.fecha_consulta <= search_params.fecha_hasta)

        if search_params.condicion_general:
            query = query.filter(Consulta.condicion_general == search_params.condicion_general)

        if search_params.es_seguimiento is not None:
            query = query.filter(Consulta.es_seguimiento == search_params.es_seguimiento)

        total = query.count()

        consultas = query.order_by(desc(Consulta.fecha_consulta)) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return consultas, total

    def get_seguimientos(self, db: Session) -> List[Consulta]:
        """Obtener consultas de seguimiento"""
        return db.query(Consulta).filter(Consulta.es_seguimiento == True) \
            .order_by(desc(Consulta.fecha_consulta)).all()

    def get_por_fecha(self, db: Session, *, fecha: date) -> List[Consulta]:
        """Obtener consultas de una fecha específica"""
        return db.query(Consulta).filter(func.date(Consulta.fecha_consulta) == fecha) \
            .order_by(Consulta.fecha_consulta).all()

    def get_estadisticas_por_condicion(self, db: Session) -> Dict[str, int]:
        """Obtener estadísticas por condición general"""
        return {
            "excelente": db.query(Consulta).filter(Consulta.condicion_general == "Excelente").count(),
            "buena": db.query(Consulta).filter(Consulta.condicion_general == "Buena").count(),
            "regular": db.query(Consulta).filter(Consulta.condicion_general == "Regular").count(),
            "mala": db.query(Consulta).filter(Consulta.condicion_general == "Mala").count(),
            "critica": db.query(Consulta).filter(Consulta.condicion_general == "Critica").count()
        }


consulta = CRUDConsulta(Consulta)
