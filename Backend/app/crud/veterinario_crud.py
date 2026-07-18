# app/crud/veterinario_crud.py
from sqlalchemy.orm import Session
from typing import Optional
from app.crud.base_crud import CRUDBase
from app.models.veterinario import Veterinario
from app.schemas.veterinario_schema import VeterinarioCreate, VeterinarioUpdate

class CRUDVeterinario(CRUDBase[Veterinario, VeterinarioCreate, VeterinarioUpdate]):
    
    def get_by_dni(self, db: Session, *, dni: str) -> Optional[Veterinario]:
        """Obtener veterinario por DNI"""
        return db.query(Veterinario).filter(Veterinario.dni == dni).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Veterinario]:
        """Obtener veterinario por email"""
        return db.query(Veterinario).filter(Veterinario.email == email).first()


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

# Instancia única
veterinario = CRUDVeterinario(Veterinario)