# app/crud/catalogo/servicio.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.tipo_servicio import TipoServicio
from app.models.servicio import Servicio
from app.schemas.catalogo_schemas import ServicioCreate, ServicioUpdate


# ===== SERVICIO COMPLETO =====
class CRUDServicio(CRUDBase[Servicio, ServicioCreate, ServicioUpdate]):
    
    def get_by_tipo(self, db: Session, *, tipo_servicio_id: int, solo_activos: bool = True) -> List[Servicio]:
        """Obtener servicios por tipo"""
        query = db.query(Servicio).filter(Servicio.id_tipo_servicio == tipo_servicio_id)
        if solo_activos:
            query = query.filter(Servicio.activo == True)
        return query.order_by(Servicio.nombre_servicio).all()

    def get_activos(self, db: Session) -> List[Servicio]:
        """Obtener servicios activos"""
        return db.query(Servicio).filter(Servicio.activo == True)\
                                 .order_by(Servicio.nombre_servicio).all()

    def get_by_nombre(self, db: Session, *, nombre_servicio: str) -> Optional[Servicio]:
        """Obtener servicio por nombre exacto"""
        return db.query(Servicio).filter(Servicio.nombre_servicio == nombre_servicio).first()

    def search_servicios(self, db: Session, *, nombre: str = None, activo: bool = None, tipo_servicio_id: int = None) -> List[Servicio]:
        """Buscar servicios con filtros"""
        query = db.query(Servicio)
        
        if nombre:
            query = query.filter(Servicio.nombre_servicio.ilike(f"%{nombre}%"))
        
        if activo is not None:
            query = query.filter(Servicio.activo == activo)
            
        if tipo_servicio_id:
            query = query.filter(Servicio.id_tipo_servicio == tipo_servicio_id)
        
        return query.order_by(Servicio.nombre_servicio).all()

    def get_by_precio_range(self, db: Session, *, precio_min: float = None, precio_max: float = None) -> List[Servicio]:
        """Obtener servicios por rango de precio"""
        query = db.query(Servicio).filter(Servicio.activo == True)
        
        if precio_min is not None:
            query = query.filter(Servicio.precio >= precio_min)
        
        if precio_max is not None:
            query = query.filter(Servicio.precio <= precio_max)
        
        return query.order_by(Servicio.precio).all()

    def exists_by_nombre(self, db: Session, *, nombre_servicio: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un servicio con ese nombre"""
        query = db.query(Servicio).filter(Servicio.nombre_servicio == nombre_servicio)
        if exclude_id:
            query = query.filter(Servicio.id_servicio != exclude_id)
        return query.first() is not None

    def get_with_tipo_info(self, db: Session, *, servicio_id: int) -> Optional[Dict[str, Any]]:
        """Obtener servicio con información del tipo"""
        resultado = db.query(
            Servicio.id_servicio,
            Servicio.nombre_servicio,
            Servicio.precio,
            Servicio.activo,
            Servicio.id_tipo_servicio,
            TipoServicio.descripcion.label('tipo_descripcion')
        ).join(TipoServicio, Servicio.id_tipo_servicio == TipoServicio.id_tipo_servicio)\
         .filter(Servicio.id_servicio == servicio_id).first()
        
        if resultado:
            return {
                "id_servicio": resultado.id_servicio,
                "nombre_servicio": resultado.nombre_servicio,
                "precio": float(resultado.precio),
                "activo": resultado.activo,
                "id_tipo_servicio": resultado.id_tipo_servicio,
                "tipo_descripcion": resultado.tipo_descripcion
            }
        return None

    def activate_service(self, db: Session, *, servicio_id: int) -> Optional[Servicio]:
        """Activar servicio"""
        servicio_obj = self.get(db, servicio_id)
        if servicio_obj:
            servicio_obj.activo = True
            db.commit()
            db.refresh(servicio_obj)
        return servicio_obj

    def deactivate_service(self, db: Session, *, servicio_id: int) -> Optional[Servicio]:
        """Desactivar servicio"""
        servicio_obj = self.get(db, servicio_id)
        if servicio_obj:
            servicio_obj.activo = False
            db.commit()
            db.refresh(servicio_obj)
        return servicio_obj

    def get_mas_solicitados(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener servicios más solicitados"""
        from app.models.servicio_solicitado import ServicioSolicitado
        
        resultado = db.query(
            Servicio.id_servicio,
            Servicio.nombre_servicio,
            Servicio.precio,
            func.count(ServicioSolicitado.id_servicio_solicitado).label('total_solicitudes')
        ).outerjoin(ServicioSolicitado, Servicio.id_servicio == ServicioSolicitado.id_servicio)\
         .group_by(Servicio.id_servicio, Servicio.nombre_servicio, Servicio.precio)\
         .order_by(func.count(ServicioSolicitado.id_servicio_solicitado).desc())\
         .limit(limit).all()
        
        return [
            {
                "id_servicio": r.id_servicio,
                "nombre_servicio": r.nombre_servicio,
                "precio": float(r.precio),
                "total_solicitudes": r.total_solicitudes or 0
            }
            for r in resultado
        ]

    def get_estadisticas_precios(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de precios"""
        resultado = db.query(
            func.min(Servicio.precio).label('precio_minimo'),
            func.max(Servicio.precio).label('precio_maximo'),
            func.avg(Servicio.precio).label('precio_promedio'),
            func.count(Servicio.id_servicio).label('total_servicios')
        ).filter(Servicio.activo == True).first()
        
        return {
            "precio_minimo": float(resultado.precio_minimo) if resultado.precio_minimo else 0,
            "precio_maximo": float(resultado.precio_maximo) if resultado.precio_maximo else 0,
            "precio_promedio": float(resultado.precio_promedio) if resultado.precio_promedio else 0,
            "total_servicios": resultado.total_servicios or 0
        }


servicio = CRUDServicio(Servicio)
