from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.crud.base_crud import CRUDBase
from app.models.movimiento_financiero import MovimientoFinanciero
from app.schemas.movimiento_financiero_schema import (
    MovimientoFinancieroCreate, MovimientoFinancieroUpdate
)


class CRUDMovimientoFinanciero(CRUDBase[MovimientoFinanciero, MovimientoFinancieroCreate, MovimientoFinancieroUpdate]):

    def get(self, db: Session, id: int) -> Optional[MovimientoFinanciero]:
        return db.query(MovimientoFinanciero).filter(MovimientoFinanciero.id_movimiento == id).first()

    def get_by_tipo(self, db: Session, *, tipo: str) -> List[MovimientoFinanciero]:
        return db.query(MovimientoFinanciero).filter(MovimientoFinanciero.tipo == tipo)\
            .order_by(desc(MovimientoFinanciero.fecha_movimiento)).all()

    def get_by_categoria(self, db: Session, *, categoria: str) -> List[MovimientoFinanciero]:
        return db.query(MovimientoFinanciero).filter(MovimientoFinanciero.categoria == categoria)\
            .order_by(desc(MovimientoFinanciero.fecha_movimiento)).all()

    def get_by_cita(self, db: Session, *, cita_id: int) -> Optional[MovimientoFinanciero]:
        return db.query(MovimientoFinanciero).filter(MovimientoFinanciero.id_cita == cita_id).first()

    def get_by_fecha_range(
        self, db: Session, *, fecha_desde: date, fecha_hasta: date
    ) -> List[MovimientoFinanciero]:
        return db.query(MovimientoFinanciero).filter(
            func.date(MovimientoFinanciero.fecha_movimiento) >= fecha_desde,
            func.date(MovimientoFinanciero.fecha_movimiento) <= fecha_hasta
        ).order_by(desc(MovimientoFinanciero.fecha_movimiento)).all()

    def get_recientes(self, db: Session, *, limit: int = 50) -> List[MovimientoFinanciero]:
        return db.query(MovimientoFinanciero)\
            .order_by(desc(MovimientoFinanciero.fecha_movimiento))\
            .limit(limit).all()

    def get_resumen(self, db: Session) -> Dict[str, Any]:
        total_ingresos = db.query(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))\
            .filter(MovimientoFinanciero.tipo == 'Ingreso').scalar()
        total_egresos = db.query(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))\
            .filter(MovimientoFinanciero.tipo == 'Egreso').scalar()
        return {
            "total_ingresos": float(total_ingresos),
            "total_egresos": float(total_egresos),
            "saldo_neto": float(total_ingresos) - float(total_egresos)
        }


movimiento_financiero = CRUDMovimientoFinanciero(MovimientoFinanciero)
