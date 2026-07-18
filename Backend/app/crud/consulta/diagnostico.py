# app/crud/consulta/diagnostico.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.diagnostico import Diagnostico
from app.schemas.consulta_schema import DiagnosticoCreate


# ===== DIAGNÓSTICO COMPLETO =====
class CRUDDiagnostico(CRUDBase[Diagnostico, DiagnosticoCreate, None]):

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[Diagnostico]:
        """Obtener diagnósticos de una consulta"""
        return db.query(Diagnostico).filter(Diagnostico.id_consulta == consulta_id) \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def get_by_tipo(self, db: Session, *, tipo_diagnostico: str) -> List[Diagnostico]:
        """Obtener diagnósticos por tipo"""
        return db.query(Diagnostico).filter(Diagnostico.tipo_diagnostico == tipo_diagnostico) \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def get_mas_frecuentes(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener patologías más diagnosticadas"""
        from app.models.patologia import Patologia

        resultado = db.query(
            Patologia.nombre_patologia,
            func.count(Diagnostico.id_diagnostico).label('total_diagnosticos')
        ).join(Patologia, Diagnostico.id_patologia == Patologia.id_patologia) \
            .group_by(Patologia.id_patologia, Patologia.nombre_patologia) \
            .order_by(func.count(Diagnostico.id_diagnostico).desc()) \
            .limit(limit).all()

        return [
            {
                "patologia": r.nombre_patologia,
                "total_diagnosticos": r.total_diagnosticos
            }
            for r in resultado
        ]


diagnostico = CRUDDiagnostico(Diagnostico)
