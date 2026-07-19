# app/crud/catalogo/raza.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.raza import Raza
from app.schemas.catalogo_schemas import RazaCreate


# ===== RAZA COMPLETO =====
class CRUDRaza(CRUDBase[Raza, RazaCreate, None]):
    
    def get_by_nombre(self, db: Session, *, nombre_raza: str) -> Optional[Raza]:
        """Obtener raza por nombre exacto"""
        return db.query(Raza).filter(Raza.nombre_raza == nombre_raza).first()

    def search_razas(self, db: Session, *, nombre: str) -> List[Raza]:
        """Buscar razas por nombre (parcial)"""
        return db.query(Raza).filter(Raza.nombre_raza.ilike(f"%{nombre}%"))\
                             .order_by(Raza.nombre_raza).all()

    def exists_by_nombre(self, db: Session, *, nombre_raza: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una raza con ese nombre"""
        query = db.query(Raza).filter(Raza.nombre_raza == nombre_raza)
        if exclude_id:
            query = query.filter(Raza.id_raza != exclude_id)
        return query.first() is not None

    def get_razas_con_mascotas_count(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener razas con conteo de mascotas"""
        from app.models.mascota import Mascota
        
        resultado = db.query(
            Raza.id_raza,
            Raza.nombre_raza,
            func.count(Mascota.id_mascota).label('total_mascotas')
        ).outerjoin(Mascota, Raza.id_raza == Mascota.id_raza)\
         .group_by(Raza.id_raza, Raza.nombre_raza)\
         .order_by(Raza.nombre_raza).all()
        
        return [
            {
                "id_raza": r.id_raza,
                "nombre_raza": r.nombre_raza,
                "total_mascotas": r.total_mascotas or 0
            }
            for r in resultado
        ]

    def get_razas_populares(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener razas más populares por número de mascotas"""
        from app.models.mascota import Mascota
        
        resultado = db.query(
            Raza.id_raza,
            Raza.nombre_raza,
            func.count(Mascota.id_mascota).label('total_mascotas')
        ).join(Mascota, Raza.id_raza == Mascota.id_raza)\
         .group_by(Raza.id_raza, Raza.nombre_raza)\
         .order_by(func.count(Mascota.id_mascota).desc())\
         .limit(limit).all()
        
        return [
            {
                "id_raza": r.id_raza,
                "nombre_raza": r.nombre_raza,
                "total_mascotas": r.total_mascotas
            }
            for r in resultado
        ]

    def get_all_ordenadas(self, db: Session) -> List[Raza]:
        """Obtener todas las razas ordenadas alfabéticamente"""
        return db.query(Raza).order_by(Raza.nombre_raza).all()


raza = CRUDRaza(Raza)
