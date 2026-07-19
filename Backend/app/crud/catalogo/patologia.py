# app/crud/catalogo/patologia.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.patologia import Patologia
from app.schemas.catalogo_schemas import PatologiaCreate


# ===== PATOLOGÍA COMPLETO =====
class CRUDPatologia(CRUDBase[Patologia, PatologiaCreate, None]):

    def get_by_nombre(self, db: Session, *, nombre_patologia: str) -> Optional[Patologia]:
        """Obtener patología por nombre exacto"""
        return db.query(Patologia).filter(Patologia.nombre_patologia == nombre_patologia).first()

    def get_by_especie(self, db: Session, *, especie: str) -> List[Patologia]:
        """Obtener patologías por especie"""
        return db.query(Patologia).filter(
            or_(
                Patologia.especie_afecta == especie,
                Patologia.especie_afecta == "Ambas"
            )
        ).order_by(Patologia.nombre_patologia).all()

    def get_by_gravedad(self, db: Session, *, gravedad: str) -> List[Patologia]:
        """Obtener patologías por gravedad"""
        return db.query(Patologia).filter(Patologia.gravedad == gravedad) \
            .order_by(Patologia.nombre_patologia).all()

    def get_cronicas(self, db: Session) -> List[Patologia]:
        """Obtener patologías crónicas"""
        return db.query(Patologia).filter(Patologia.es_crónica == True) \
            .order_by(Patologia.nombre_patologia).all()

    def get_contagiosas(self, db: Session) -> List[Patologia]:
        """Obtener patologías contagiosas"""
        return db.query(Patologia).filter(Patologia.es_contagiosa == True) \
            .order_by(Patologia.nombre_patologia).all()

    def search_patologias(self, db: Session, *, nombre: str = None, especie: str = None, gravedad: str = None) -> List[
        Patologia]:
        """Buscar patologías con múltiples filtros"""
        query = db.query(Patologia)

        if nombre:
            query = query.filter(Patologia.nombre_patologia.ilike(f"%{nombre}%"))

        if especie:
            query = query.filter(
                or_(
                    Patologia.especie_afecta == especie,
                    Patologia.especie_afecta == "Ambas"
                )
            )

        if gravedad:
            query = query.filter(Patologia.gravedad == gravedad)

        return query.order_by(Patologia.nombre_patologia).all()

    def exists_by_nombre(self, db: Session, *, nombre_patologia: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una patología con ese nombre"""
        query = db.query(Patologia).filter(Patologia.nombre_patologia == nombre_patologia)
        if exclude_id:
            query = query.filter(Patologia.id_patologia != exclude_id)
        return query.first() is not None

    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de patologías"""
        total = db.query(Patologia).count()

        # Por especie
        perros = db.query(Patologia).filter(
            or_(
                Patologia.especie_afecta == "Perro",
                Patologia.especie_afecta == "Ambas"
            )
        ).count()

        gatos = db.query(Patologia).filter(
            or_(
                Patologia.especie_afecta == "Gato",
                Patologia.especie_afecta == "Ambas"
            )
        ).count()

        # Por gravedad
        por_gravedad = db.query(
            Patologia.gravedad,
            func.count(Patologia.id_patologia).label('total')
        ).group_by(Patologia.gravedad).all()

        # Características especiales
        cronicas = db.query(Patologia).filter(Patologia.es_crónica == True).count()
        contagiosas = db.query(Patologia).filter(Patologia.es_contagiosa == True).count()

        return {
            "total_patologias": total,
            "por_especie": {
                "perros": perros,
                "gatos": gatos,
                "ambas": db.query(Patologia).filter(Patologia.especie_afecta == "Ambas").count()
            },
            "por_gravedad": {gravedad.gravedad: gravedad.total for gravedad in por_gravedad},
            "caracteristicas": {
                "cronicas": cronicas,
                "contagiosas": contagiosas,
                "agudas": total - cronicas
            }
        }

    def get_mas_diagnosticadas(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener patologías más diagnosticadas"""
        from app.models.diagnostico import Diagnostico

        resultado = db.query(
            Patologia.id_patologia,
            Patologia.nombre_patologia,
            Patologia.gravedad,
            func.count(Diagnostico.id_diagnostico).label('total_diagnosticos')
        ).outerjoin(Diagnostico, Patologia.id_patologia == Diagnostico.id_patologia) \
            .group_by(Patologia.id_patologia, Patologia.nombre_patologia, Patologia.gravedad) \
            .order_by(func.count(Diagnostico.id_diagnostico).desc()) \
            .limit(limit).all()

        return [
            {
                "id_patologia": r.id_patologia,
                "nombre_patologia": r.nombre_patologia,
                "gravedad": r.gravedad,
                "total_diagnosticos": r.total_diagnosticos or 0
            }
            for r in resultado
        ]

    def get_all_ordenadas(self, db: Session) -> List[Patologia]:
        """Obtener todas las patologías ordenadas alfabéticamente"""
        return db.query(Patologia).order_by(Patologia.nombre_patologia).all()


patologia = CRUDPatologia(Patologia)
