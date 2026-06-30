from sqlalchemy import Column, Integer, Numeric, DateTime, Enum as SQLEnum, ForeignKey, CheckConstraint, String
from app.models.base import Base


class MovimientoFinanciero(Base):
    __tablename__ = "Movimiento_financiero"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(SQLEnum('Ingreso', 'Egreso', name='tipo_movimiento_enum'), nullable=False)
    categoria = Column(SQLEnum('Servicio', 'Operativo', 'Nomina', name='categoria_movimiento_enum'), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    concepto = Column(String(150), nullable=False)
    fecha_movimiento = Column(DateTime, nullable=False)
    id_cita = Column(Integer, ForeignKey('Cita.id_cita'))
    id_administrador = Column(Integer, ForeignKey('Administrador.id_administrador'))

    __table_args__ = (
        CheckConstraint("monto >= 0", name='MF_chk_1'),
    )
