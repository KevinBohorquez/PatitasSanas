# app/crud/base_crud.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

# Usar Any en lugar de Base para compatibilidad
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD genérico con métodos estándar para Create, Read, Update, Delete.
        
        **Parámetros**
        * `model`: Modelo de SQLAlchemy
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Obtener por ID"""
        # Intentar obtener el campo de ID dinámicamente
        id_field = None
        # Probar con varias convenciones de nombre
        for candidate in [
            f"id_{self.model.__tablename__.lower()}",
            f"id_{self.model.__tablename__.lower().replace('_', '')}",
            "id",
            "id_solicitud",
            "id_cita",
        ]:
            if hasattr(self.model, candidate):
                id_field = candidate
                break

        if id_field:
            return db.query(self.model).filter(getattr(self.model, id_field) == id).first()
        else:
            raise Exception("No se pudo determinar el campo de ID")

        if hasattr(self.model, id_field):
            return db.query(self.model).filter(getattr(self.model, id_field) == id).first()
        else:
            # Fallback a 'id' si no existe el campo específico
            return db.query(self.model).filter(getattr(self.model, 'id', None) == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, order_by: str = None
    ) -> List[ModelType]:
        """Obtener múltiples registros"""
        query = db.query(self.model)
        
        if order_by:
            if order_by.startswith('-'):
                query = query.order_by(desc(getattr(self.model, order_by[1:], None)))
            else:
                query = query.order_by(asc(getattr(self.model, order_by, None)))
        
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Crear nuevo registro"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Actualizar registro existente"""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Eliminar registro"""
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def soft_delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Soft delete (cambiar estado a inactivo)"""
        obj = self.get(db, id)
        if obj and hasattr(obj, 'estado'):
            obj.estado = "Inactivo"
            db.commit()
            db.refresh(obj)
        return obj

    def count(self, db: Session) -> int:
        """Contar registros"""
        return db.query(self.model).count()

    def exists(self, db: Session, *, id: Any) -> bool:
        """Verificar si existe"""
        return self.get(db, id) is not None

    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtener solo registros activos"""
        query = db.query(self.model)
        if hasattr(self.model, 'estado'):
            query = query.filter(self.model.estado == "Activo")
        return query.offset(skip).limit(limit).all()

    def count_active(self, db: Session) -> int:
        """Contar registros activos"""
        query = db.query(self.model)
        if hasattr(self.model, 'estado'):
            query = query.filter(self.model.estado == "Activo")
        return query.count()