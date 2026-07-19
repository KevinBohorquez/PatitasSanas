# app/crud/catalogo/tipo_servicio.py
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.tipo_servicio import TipoServicio
from app.models.servicio import Servicio
from app.schemas.catalogo_schemas import TipoServicioCreate


# ===== TIPO SERVICIO COMPLETO =====
class CRUDTipoServicio(CRUDBase[TipoServicio, TipoServicioCreate, None]):
    
    def get_by_descripcion(self, db: Session, *, descripcion: str) -> Optional[TipoServicio]:
        """Obtener tipo de servicio por descripción exacta"""
        return db.query(TipoServicio).filter(TipoServicio.descripcion == descripcion).first()

    def exists_by_descripcion(self, db: Session, *, descripcion: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un tipo de servicio con esa descripción"""
        query = db.query(TipoServicio).filter(TipoServicio.descripcion == descripcion)
        if exclude_id:
            query = query.filter(TipoServicio.id_tipo_servicio != exclude_id)
        return query.first() is not None

    def get_tipos_con_servicios_count(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener tipos de servicio con conteo de servicios"""
        resultado = db.query(
            TipoServicio.id_tipo_servicio,
            TipoServicio.descripcion,
            func.count(Servicio.id_servicio).label('total_servicios'),
            func.sum(
                case((Servicio.activo == True, 1), 
                    else_=0
                )
            ).label('servicios_activos')
        ).outerjoin(Servicio, TipoServicio.id_tipo_servicio == Servicio.id_tipo_servicio)\
         .group_by(TipoServicio.id_tipo_servicio, TipoServicio.descripcion)\
         .order_by(TipoServicio.descripcion).all()
        
        return [
            {
                "id_tipo_servicio": r.id_tipo_servicio,
                "descripcion": r.descripcion,
                "total_servicios": r.total_servicios or 0,
                "servicios_activos": r.servicios_activos or 0
            }
            for r in resultado
        ]

    def search_tipos(self, db: Session, *, descripcion: str) -> List[TipoServicio]:
        """Buscar tipos de servicio por descripción"""
        return db.query(TipoServicio).filter(TipoServicio.descripcion.ilike(f"%{descripcion}%"))\
                                    .order_by(TipoServicio.descripcion).all()

    def get_all_ordenados(self, db: Session) -> List[TipoServicio]:
        """Obtener todos los tipos ordenados alfabéticamente"""
        return db.query(TipoServicio).order_by(TipoServicio.descripcion).all()


tipo_servicio = CRUDTipoServicio(TipoServicio)
