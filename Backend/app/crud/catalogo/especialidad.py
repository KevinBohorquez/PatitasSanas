# app/crud/catalogo/especialidad.py
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.especialidad import Especialidad
from app.schemas.catalogo_schemas import EspecialidadCreate


# ===== ESPECIALIDAD COMPLETO =====
class CRUDEspecialidad(CRUDBase[Especialidad, EspecialidadCreate, None]):
    
    def get_by_descripcion(self, db: Session, *, descripcion: str) -> Optional[Especialidad]:
        """Obtener especialidad por descripción exacta"""
        return db.query(Especialidad).filter(Especialidad.descripcion == descripcion).first()

    def search_especialidades(self, db: Session, *, descripcion: str) -> List[Especialidad]:
        """Buscar especialidades por descripción (parcial)"""
        return db.query(Especialidad).filter(Especialidad.descripcion.ilike(f"%{descripcion}%"))\
                                    .order_by(Especialidad.descripcion).all()

    def exists_by_descripcion(self, db: Session, *, descripcion: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una especialidad con esa descripción"""
        query = db.query(Especialidad).filter(Especialidad.descripcion == descripcion)
        if exclude_id:
            query = query.filter(Especialidad.id_especialidad != exclude_id)
        return query.first() is not None

    def get_especialidades_con_veterinarios_count(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener especialidades con conteo de veterinarios"""
        from app.models.veterinario import Veterinario
        
        resultado = db.query(
            Especialidad.id_especialidad,
            Especialidad.descripcion,
            func.count(Veterinario.id_veterinario).label('total_veterinarios'),
            func.sum(
                case((Veterinario.disposicion == 'Libre', 1), 
                    else_=0
                )
            ).label('veterinarios_disponibles')
        ).outerjoin(Veterinario, Especialidad.id_especialidad == Veterinario.id_especialidad)\
         .group_by(Especialidad.id_especialidad, Especialidad.descripcion)\
         .order_by(Especialidad.descripcion).all()
        
        return [
            {
                "id_especialidad": r.id_especialidad,
                "descripcion": r.descripcion,
                "total_veterinarios": r.total_veterinarios or 0,
                "veterinarios_disponibles": r.veterinarios_disponibles or 0
            }
            for r in resultado
        ]

    def get_mas_demandadas(self, db: Session, *, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener especialidades más demandadas"""
        from app.models.veterinario import Veterinario
        from app.models.consulta import Consulta
        
        resultado = db.query(
            Especialidad.descripcion,
            func.count(Consulta.id_consulta).label('total_consultas')
        ).join(Veterinario, Especialidad.id_especialidad == Veterinario.id_especialidad)\
         .join(Consulta, Veterinario.id_veterinario == Consulta.id_veterinario)\
         .group_by(Especialidad.id_especialidad, Especialidad.descripcion)\
         .order_by(func.count(Consulta.id_consulta).desc())\
         .limit(limit).all()
        
        return [
            {
                "especialidad": r.descripcion,
                "total_consultas": r.total_consultas
            }
            for r in resultado
        ]

    def get_all_ordenadas(self, db: Session) -> List[Especialidad]:
        """Obtener todas las especialidades ordenadas alfabéticamente"""
        return db.query(Especialidad).order_by(Especialidad.descripcion).all()


especialidad = CRUDEspecialidad(Especialidad)
