# app/crud/consulta/cita.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional
from datetime import datetime, date
from app.crud.base_crud import CRUDBase
from app.models.cita import Cita
from app.models.servicio_solicitado import ServicioSolicitado
from app.models.servicio import Servicio
from app.models.movimiento_financiero import MovimientoFinanciero
from app.schemas.consulta_schema import CitaCreate, CitaUpdate


# ===== CITA COMPLETO =====
class CRUDCita(CRUDBase[Cita, CitaCreate, CitaUpdate]):

    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[Cita]:
        """Obtener citas de una mascota"""
        return db.query(Cita).filter(Cita.id_mascota == mascota_id) \
            .order_by(desc(Cita.fecha_hora_programada)).all()

    def get_by_estado(self, db: Session, *, estado_cita: str) -> List[Cita]:
        """Obtener citas por estado"""
        return db.query(Cita).filter(Cita.estado_cita == estado_cita) \
            .order_by(Cita.fecha_hora_programada).all()

    def get_by_servicio_solicitado(self, db: Session, *, servicio_solicitado_id: int,
                                   limit: int = 50) -> List[Cita]:
        """Obtener citas de un servicio solicitado"""
        return db.query(Cita).filter(Cita.id_servicio_solicitado == servicio_solicitado_id) \
            .order_by(Cita.fecha_hora_programada).limit(limit).all()

    def get_por_fecha(self, db: Session, *, fecha: date) -> List[Cita]:
        """Obtener citas de una fecha específica"""
        return db.query(Cita).filter(func.date(Cita.fecha_hora_programada) == fecha) \
            .order_by(Cita.fecha_hora_programada).all()

    def verificar_disponibilidad(self, db: Session, *, fecha_hora: datetime, exclude_id: int = None) -> bool:
        """Verificar disponibilidad de horario"""
        query = db.query(Cita).filter(
            and_(
                Cita.fecha_hora_programada == fecha_hora,
                Cita.estado_cita == "Programada"
            )
        )

        if exclude_id:
            query = query.filter(Cita.id_cita != exclude_id)

        return query.first() is None

    def marcar_atendida(self, db: Session, *, cita_id: int) -> Optional[Cita]:
        """Marcar cita como atendida y registrar ingreso automaticamente"""
        cita = self.get(db, cita_id)
        if cita and cita.estado_cita == "Programada":
            cita.estado_cita = "Atendida"

            # Obtener el precio del servicio asociado
            monto = 0
            concepto = f"Ingreso por cita #{cita_id}"
            if cita.id_servicio_solicitado:
                ss = db.query(ServicioSolicitado).filter(
                    ServicioSolicitado.id_servicio_solicitado == cita.id_servicio_solicitado
                ).first()
                if ss and ss.id_servicio:
                    servicio = db.query(Servicio).filter(Servicio.id_servicio == ss.id_servicio).first()
                    if servicio:
                        monto = float(servicio.precio)
                        concepto = f"Ingreso por {servicio.nombre_servicio} - Cita #{cita_id}"

            # Registrar movimiento financiero (ingreso automático) SOLO si hay monto.
            # Si la cita no tiene servicio con precio, el monto es 0 y registrarlo
            # ensuciaría el Flujo de Caja / Balance con ingresos vacíos (SC-032 / F13).
            if monto > 0:
                movimiento = MovimientoFinanciero(
                    tipo='Ingreso',
                    categoria='Servicio',
                    monto=monto,
                    concepto=concepto,
                    fecha_movimiento=datetime.now(),
                    id_cita=cita_id
                )
                db.add(movimiento)

            # El commit/refresh se hacen siempre, para persistir estado_cita='Atendida'.
            db.commit()
            db.refresh(cita)
        return cita


cita = CRUDCita(Cita)
