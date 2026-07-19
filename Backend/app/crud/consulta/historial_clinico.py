# app/crud/consulta/historial_clinico.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime
from app.crud.base_crud import CRUDBase
from app.models.historial_clinico import HistorialClinico
from app.schemas.consulta_schema import HistorialClinicoCreate


# ===== HISTORIAL CLÍNICO COMPLETO =====
class CRUDHistorialClinico(CRUDBase[HistorialClinico, HistorialClinicoCreate, None]):

    def get_by_mascota(self, db: Session, *, mascota_id: int, limit: int = 50) -> List[HistorialClinico]:
        """Obtener historial clínico de una mascota"""
        return db.query(HistorialClinico) \
            .filter(HistorialClinico.id_mascota == mascota_id) \
            .order_by(desc(HistorialClinico.fecha_evento)) \
            .limit(limit).all()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int) -> List[HistorialClinico]:
        """Obtener eventos del historial por veterinario"""
        return db.query(HistorialClinico).filter(HistorialClinico.id_veterinario == veterinario_id) \
            .order_by(desc(HistorialClinico.fecha_evento)).all()

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[HistorialClinico]:
        """Obtener eventos relacionados a una consulta"""
        return db.query(HistorialClinico).filter(HistorialClinico.id_consulta == consulta_id) \
            .order_by(HistorialClinico.fecha_evento).all()

    def add_evento(self, db: Session, *, evento_data: HistorialClinicoCreate) -> HistorialClinico:
        """Agregar evento al historial"""
        evento_dict = evento_data.dict()
        evento_dict['fecha_evento'] = evento_dict.get('fecha_evento', datetime.now())
        return self.create(db, obj_in=evento_dict)

    def add_evento_consulta(self, db: Session, *, mascota_id: int, consulta_id: int, veterinario_id: int,
                            descripcion: str, peso_actual: float = None) -> HistorialClinico:
        """Agregar evento específico de consulta"""
        # Registrar la edad (en meses) que la mascota tenía al momento de la consulta, para
        # que quede visible en el historial. Antes no se guardaba y quedaba siempre NULL.
        from app.models.mascota import Mascota
        mascota_obj = db.query(Mascota).filter(Mascota.id_mascota == mascota_id).first()
        edad_meses_actual = None
        if mascota_obj:
            edad_meses_actual = (mascota_obj.edad_anios or 0) * 12 + (mascota_obj.edad_meses or 0)

        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_consulta=consulta_id,
            id_veterinario=veterinario_id,
            tipo_evento="Consulta médica",
            descripcion_evento=descripcion,
            peso_momento=peso_actual,
            edad_meses=edad_meses_actual,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def add_evento_diagnostico(self, db: Session, *, mascota_id: int, diagnostico_id: int,
                               veterinario_id: int, descripcion: str) -> HistorialClinico:
        """Agregar evento específico de diagnóstico"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_diagnostico=diagnostico_id,
            id_veterinario=veterinario_id,
            tipo_evento="Diagnóstico",
            descripcion_evento=descripcion,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def add_evento_tratamiento(self, db: Session, *, mascota_id: int, tratamiento_id: int,
                               veterinario_id: int, descripcion: str) -> HistorialClinico:
        """Agregar evento específico de tratamiento"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_tratamiento=tratamiento_id,
            id_veterinario=veterinario_id,
            tipo_evento="Tratamiento",
            descripcion_evento=descripcion,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)


# Instancias únicas - TODAS LAS CLASES


historial_clinico = CRUDHistorialClinico(HistorialClinico)
