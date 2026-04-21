# app/crud/veterinario_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from app.crud.base_crud import CRUDBase
from app.models.veterinario import Veterinario
from app.models.especialidad import Especialidad
from app.schemas.veterinario_schema import VeterinarioCreate, VeterinarioUpdate, VeterinarioSearch

class CRUDVeterinario(CRUDBase[Veterinario, VeterinarioCreate, VeterinarioUpdate]):
    
    def get_by_dni(self, db: Session, *, dni: str) -> Optional[Veterinario]:
        """Obtener veterinario por DNI"""
        return db.query(Veterinario).filter(Veterinario.dni == dni).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Veterinario]:
        """Obtener veterinario por email"""
        return db.query(Veterinario).filter(Veterinario.email == email).first()

    def get_by_codigo_cmvp(self, db: Session, *, codigo_cmvp: str) -> Optional[Veterinario]:
        """Obtener veterinario por código CMVP"""
        return db.query(Veterinario).filter(Veterinario.codigo_CMVP == codigo_cmvp).first()


    def get_by_especialidad(self, db: Session, *, especialidad_id: int) -> List[Veterinario]:
        """Obtener veterinarios por especialidad"""
        return db.query(Veterinario).filter(Veterinario.id_especialidad == especialidad_id).all()

    def get_by_turno(self, db: Session, *, turno: str) -> List[Veterinario]:
        """Obtener veterinarios por turno"""
        return db.query(Veterinario).filter(Veterinario.turno == turno).all()

    def get_disponibles(self, db: Session) -> List[Veterinario]:
        """Obtener veterinarios disponibles (libres y activos)"""
        return db.query(Veterinario).filter(
            and_(
                Veterinario.disposicion == "Libre"
            )
        ).all()

    def get_with_especialidad(self, db: Session, *, veterinario_id: int) -> Optional[dict]:
        """Obtener veterinario con detalles de especialidad"""
        result = db.query(
            Veterinario,
            Especialidad.descripcion.label('especialidad_descripcion')
        ).join(Especialidad, Veterinario.id_especialidad == Especialidad.id_especialidad)\
         .filter(Veterinario.id_veterinario == veterinario_id).first()
        
        if result:
            return {
                "veterinario": result.Veterinario,
                "especialidad_descripcion": result.especialidad_descripcion
            }
        return None

    def search_veterinarios(self, db: Session, *, search_params: VeterinarioSearch) -> Tuple[List[Veterinario], int]:
        """Buscar veterinarios con filtros múltiples"""
        query = db.query(Veterinario)
        
        # Aplicar filtros
        if search_params.nombre:
            nombre_filter = f"%{search_params.nombre}%"
            query = query.filter(
                or_(
                    Veterinario.nombre.ilike(nombre_filter),
                    Veterinario.apellido_paterno.ilike(nombre_filter),
                    Veterinario.apellido_materno.ilike(nombre_filter)
                )
            )
        
        if search_params.dni:
            query = query.filter(Veterinario.dni == search_params.dni)
        
        if search_params.id_especialidad:
            query = query.filter(Veterinario.id_especialidad == search_params.id_especialidad)
        
        if search_params.tipo_veterinario:
            query = query.filter(Veterinario.tipo_veterinario == search_params.tipo_veterinario)

        
        if search_params.disposicion:
            query = query.filter(Veterinario.disposicion == search_params.disposicion)
        
        if search_params.turno:
            query = query.filter(Veterinario.turno == search_params.turno)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación
        veterinarios = query.order_by(Veterinario.fecha_ingreso.desc())\
                           .offset((search_params.page - 1) * search_params.per_page)\
                           .limit(search_params.per_page).all()
        
        return veterinarios, total

    def exists_by_dni(self, db: Session, *, dni: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un veterinario con ese DNI"""
        query = db.query(Veterinario).filter(Veterinario.dni == dni)
        if exclude_id:
            query = query.filter(Veterinario.id_veterinario != exclude_id)
        return query.first() is not None

    def exists_by_email(self, db: Session, *, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un veterinario con ese email"""
        query = db.query(Veterinario).filter(Veterinario.email == email)
        if exclude_id:
            query = query.filter(Veterinario.id_veterinario != exclude_id)
        return query.first() is not None

    def exists_by_codigo_cmvp(self, db: Session, *, codigo_cmvp: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un veterinario con ese código CMVP"""
        query = db.query(Veterinario).filter(Veterinario.codigo_CMVP == codigo_cmvp)
        if exclude_id:
            query = query.filter(Veterinario.id_veterinario != exclude_id)
        return query.first() is not None

    def cambiar_disposicion(self, db: Session, *, veterinario_id: int, nueva_disposicion: str) -> Optional[Veterinario]:
        """Cambiar disposición del veterinario (Libre/Ocupado)"""
        veterinario = self.get(db, veterinario_id)
        if veterinario:
            veterinario.disposicion = nueva_disposicion
            db.commit()
            db.refresh(veterinario)
        return veterinario

    def get_estadisticas_por_turno(self, db: Session) -> dict:
        """Obtener estadísticas de veterinarios por turno"""
        return {
            "mañana": db.query(Veterinario).filter(Veterinario.turno == "Mañana").count(),
            "tarde": db.query(Veterinario).filter(Veterinario.turno == "Tarde").count(),
            "noche": db.query(Veterinario).filter(Veterinario.turno == "Noche").count()
        }

# Instancia única
veterinario = CRUDVeterinario(Veterinario)