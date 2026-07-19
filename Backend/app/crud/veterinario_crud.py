# app/crud/veterinario_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import case
from typing import Optional, List, Tuple
from app.crud.base_crud import CRUDBase
from app.models.veterinario import Veterinario
from app.models.especialidad import Especialidad
from app.models.usuario import Usuario
from app.schemas.veterinario_schema import VeterinarioCreate, VeterinarioUpdate

class CRUDVeterinario(CRUDBase[Veterinario, VeterinarioCreate, VeterinarioUpdate]):

    def get_paginated(self, db: Session, *, skip: int = 0, limit: int = 20,
                      especialidad: Optional[str] = None, tipo_veterinario: Optional[str] = None,
                      disposicion: Optional[str] = None, turno: Optional[str] = None,
                      solo_activos: Optional[bool] = None) -> Tuple[List[Veterinario], int]:
        """Listar veterinarios con filtros opcionales y paginación."""
        query = db.query(Veterinario)

        if especialidad:
            query = query.join(Veterinario.especialidad).filter(Especialidad.descripcion.ilike(f"%{especialidad}%"))
        if tipo_veterinario:
            query = query.filter(Veterinario.tipo_veterinario == tipo_veterinario)
        if disposicion:
            query = query.filter(Veterinario.disposicion == disposicion)
        if turno:
            query = query.filter(Veterinario.turno == turno)
        if solo_activos:
            query = query.join(Usuario, Veterinario.id_usuario == Usuario.id_usuario) \
                .filter(Usuario.estado == "Activo")

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_disponibles(self, db: Session, *, turno: Optional[str] = None,
                        especialidad_id: Optional[int] = None) -> List[Veterinario]:
        """Veterinarios ACTIVOS ordenados por disposición (Libre -> Ocupado -> resto)."""
        orden_disposicion = case(
            (Veterinario.disposicion == "Libre", 0),
            (Veterinario.disposicion == "Ocupado", 1),
            else_=2,
        )

        query = db.query(Veterinario) \
            .join(Usuario, Usuario.id_usuario == Veterinario.id_usuario) \
            .filter(Usuario.estado == "Activo")

        if turno:
            query = query.filter(Veterinario.turno == turno)
        if especialidad_id:
            query = query.filter(Veterinario.id_especialidad == especialidad_id)

        return query.order_by(orden_disposicion, Veterinario.id_veterinario).all()

    def get_by_especialidad(self, db: Session, *, especialidad_id: int,
                            skip: int = 0, limit: int = 20) -> Tuple[List[Veterinario], int]:
        """Veterinarios de una especialidad, paginados."""
        query = db.query(Veterinario).filter(Veterinario.id_especialidad == especialidad_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_usuario(self, db: Session, *, id_usuario: int) -> Optional[Veterinario]:
        """Obtener veterinario por id_usuario"""
        return db.query(Veterinario).filter(Veterinario.id_usuario == id_usuario).first()

    def get_by_dni(self, db: Session, *, dni: str) -> Optional[Veterinario]:
        """Obtener veterinario por DNI"""
        return db.query(Veterinario).filter(Veterinario.dni == dni).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Veterinario]:
        """Obtener veterinario por email"""
        return db.query(Veterinario).filter(Veterinario.email == email).first()

    def get_by_codigo_cmvp(self, db: Session, *, codigo_cmvp: str) -> Optional[Veterinario]:
        """Obtener veterinario por código CMVP"""
        return db.query(Veterinario).filter(Veterinario.codigo_CMVP == codigo_cmvp).first()

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
