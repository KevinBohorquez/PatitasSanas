# app/crud/consulta/triaje.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from app.crud.base_crud import CRUDBase
from app.models.triaje import Triaje
from app.schemas.consulta_schema import TriajeCreate


# ===== TRIAJE COMPLETO =====
class CRUDTriaje(CRUDBase[Triaje, TriajeCreate, None]):

    def get_by_solicitud(self, db: Session, *, solicitud_id: int) -> Optional[Triaje]:
        """Obtener triaje por solicitud"""
        return db.query(Triaje).filter(Triaje.id_solicitud == solicitud_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int, limit: int = 50) -> List[Triaje]:
        """Obtener triajes realizados por un veterinario"""
        return db.query(Triaje).filter(Triaje.id_veterinario == veterinario_id) \
            .order_by(desc(Triaje.fecha_hora_triaje)) \
            .limit(limit).all()

    def get_by_urgencia(self, db: Session, *, clasificacion: str) -> List[Triaje]:
        """Obtener triajes por nivel de urgencia"""
        return db.query(Triaje).filter(Triaje.clasificacion_urgencia == clasificacion) \
            .order_by(desc(Triaje.fecha_hora_triaje)).all()

    def get_by_fecha_rango(self, db: Session, *, fecha_inicio: datetime, fecha_fin: datetime) -> List[Triaje]:
        """Obtener triajes dentro de un rango de fechas (inclusivo en ambos extremos)"""
        return db.query(Triaje).filter(
            and_(
                Triaje.fecha_hora_triaje >= fecha_inicio,
                Triaje.fecha_hora_triaje <= fecha_fin
            )
        ).order_by(desc(Triaje.fecha_hora_triaje)).all()

    def get_criticos_recientes(self, db: Session, *, horas: int = 24) -> List[Triaje]:
        """Obtener casos críticos recientes"""
        fecha_limite = datetime.now() - timedelta(hours=horas)
        return db.query(Triaje).filter(
            and_(
                Triaje.clasificacion_urgencia == "Critico",
                Triaje.fecha_hora_triaje >= fecha_limite
            )
        ).order_by(desc(Triaje.fecha_hora_triaje)).all()

    def get_by_condicion_corporal(self, db: Session, *, condicion: str) -> List[Triaje]:
        """Obtener triajes por condición corporal"""
        return db.query(Triaje).filter(Triaje.condicion_corporal == condicion).all()

    def get_promedios_signos_vitales(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[
        str, float]:
        """Obtener promedios de signos vitales"""
        query = db.query(Triaje)

        if fecha_inicio:
            query = query.filter(Triaje.fecha_hora_triaje >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Triaje.fecha_hora_triaje <= fecha_fin)

        resultado = query.with_entities(
            func.avg(Triaje.peso_mascota).label('peso_promedio'),
            func.avg(Triaje.latido_por_minuto).label('latidos_promedio'),
            func.avg(Triaje.frecuencia_respiratoria_rpm).label('respiracion_promedio'),
            func.avg(Triaje.temperatura).label('temperatura_promedio'),
            func.avg(Triaje.frecuencia_pulso).label('pulso_promedio')
        ).first()

        return {
            "peso_promedio": float(resultado.peso_promedio) if resultado.peso_promedio else 0,
            "latidos_promedio": float(resultado.latidos_promedio) if resultado.latidos_promedio else 0,
            "respiracion_promedio": float(resultado.respiracion_promedio) if resultado.respiracion_promedio else 0,
            "temperatura_promedio": float(resultado.temperatura_promedio) if resultado.temperatura_promedio else 0,
            "pulso_promedio": float(resultado.pulso_promedio) if resultado.pulso_promedio else 0
        }


triaje = CRUDTriaje(Triaje)
