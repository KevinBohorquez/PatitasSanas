from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import date
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

    def get_resumen(
        self, db: Session,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Dict[str, Any]:
        query = db.query(MovimientoFinanciero)
        if fecha_desde:
            query = query.filter(func.date(MovimientoFinanciero.fecha_movimiento) >= fecha_desde)
        if fecha_hasta:
            query = query.filter(func.date(MovimientoFinanciero.fecha_movimiento) <= fecha_hasta)

        total_ingresos = float(query.filter(MovimientoFinanciero.tipo == 'Ingreso')
                              .with_entities(func.coalesce(func.sum(MovimientoFinanciero.monto), 0)).scalar())
        total_egresos = float(query.filter(MovimientoFinanciero.tipo == 'Egreso')
                             .with_entities(func.coalesce(func.sum(MovimientoFinanciero.monto), 0)).scalar())

        desglose_ingresos = {}
        for row in (query.filter(MovimientoFinanciero.tipo == 'Ingreso')
                    .with_entities(MovimientoFinanciero.categoria, func.sum(MovimientoFinanciero.monto))
                    .group_by(MovimientoFinanciero.categoria).all()):
            desglose_ingresos[row[0]] = float(row[1])

        desglose_egresos = {}
        for row in (query.filter(MovimientoFinanciero.tipo == 'Egreso')
                    .with_entities(MovimientoFinanciero.categoria, func.sum(MovimientoFinanciero.monto))
                    .group_by(MovimientoFinanciero.categoria).all()):
            desglose_egresos[row[0]] = float(row[1])

        return {
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "saldo_neto": total_ingresos - total_egresos,
            "desglose_ingresos": desglose_ingresos,
            "desglose_egresos": desglose_egresos
        }


movimiento_financiero = CRUDMovimientoFinanciero(MovimientoFinanciero)
