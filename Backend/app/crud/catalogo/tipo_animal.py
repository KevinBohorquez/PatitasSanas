# app/crud/catalogo/tipo_animal.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.raza import Raza
from app.models.tipo_animal import TipoAnimal
from app.schemas.catalogo_schemas import TipoAnimalCreate


# ===== TIPO ANIMAL COMPLETO =====
class CRUDTipoAnimal(CRUDBase[TipoAnimal, TipoAnimalCreate, None]):
    
    def get_by_raza(self, db: Session, *, raza_id: int) -> List[TipoAnimal]:
        """Obtener tipos de animal por raza"""
        return db.query(TipoAnimal).filter(TipoAnimal.id_raza == raza_id).all()

    def get_by_descripcion(self, db: Session, *, descripcion: str) -> List[TipoAnimal]:
        """Obtener tipos de animal por descripción (Perro/Gato)"""
        return db.query(TipoAnimal).filter(TipoAnimal.descripcion == descripcion).all()

    def get_with_raza_info(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener tipos de animal con información de raza"""
        resultado = db.query(
            TipoAnimal.id_tipo_animal,
            TipoAnimal.id_raza,
            TipoAnimal.descripcion,
            Raza.nombre_raza
        ).join(Raza, TipoAnimal.id_raza == Raza.id_raza)\
         .order_by(TipoAnimal.descripcion, Raza.nombre_raza).all()
        
        return [
            {
                "id_tipo_animal": r.id_tipo_animal,
                "id_raza": r.id_raza,
                "descripcion": r.descripcion,
                "nombre_raza": r.nombre_raza
            }
            for r in resultado
        ]

    def exists_combination(self, db: Session, *, raza_id: int, descripcion: str) -> bool:
        """Verificar si existe la combinación raza-descripción"""
        return db.query(TipoAnimal).filter(
            and_(
                TipoAnimal.id_raza == raza_id,
                TipoAnimal.descripcion == descripcion
            )
        ).first() is not None

    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de tipos de animal"""
        total = db.query(TipoAnimal).count()
        perros = db.query(TipoAnimal).filter(TipoAnimal.descripcion == "Perro").count()
        gatos = db.query(TipoAnimal).filter(TipoAnimal.descripcion == "Gato").count()
        
        return {
            "total_tipos": total,
            "perros": perros,
            "gatos": gatos,
            "razas_perros": perros,
            "razas_gatos": gatos
        }


tipo_animal = CRUDTipoAnimal(TipoAnimal)
