# app/crud/recepcionista_crud.py
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from app.crud.base_crud import CRUDBase
from app.models.recepcionista import Recepcionista
from app.schemas.recepcionista_schema import RecepcionistaCreate, RecepcionistaUpdate


class CRUDRecepcionista(CRUDBase[Recepcionista, RecepcionistaCreate, RecepcionistaUpdate]):

    def get_paginated(self, db: Session, *, skip: int = 0, limit: int = 20,
                      turno: Optional[str] = None, genero: Optional[str] = None) -> Tuple[List[Recepcionista], int]:
        """Listar recepcionistas con filtros opcionales (turno, género) y paginación."""
        query = db.query(Recepcionista)
        if turno:
            query = query.filter(Recepcionista.turno == turno)
        if genero:
            query = query.filter(Recepcionista.genero == genero)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_dni(self, db: Session, *, dni: str) -> Optional[Recepcionista]:
        """Obtener recepcionista por DNI"""
        return db.query(Recepcionista).filter(Recepcionista.dni == dni).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Recepcionista]:
        """Obtener recepcionista por email"""
        return db.query(Recepcionista).filter(Recepcionista.email == email).first()

    def exists_by_dni(self, db: Session, *, dni: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una recepcionista con ese DNI"""
        query = db.query(Recepcionista).filter(Recepcionista.dni == dni)
        if exclude_id:
            query = query.filter(Recepcionista.id_recepcionista != exclude_id)
        return query.first() is not None

    def exists_by_email(self, db: Session, *, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una recepcionista con ese email"""
        query = db.query(Recepcionista).filter(Recepcionista.email == email)
        if exclude_id:
            query = query.filter(Recepcionista.id_recepcionista != exclude_id)
        return query.first() is not None


# Instancia única
recepcionista = CRUDRecepcionista(Recepcionista)