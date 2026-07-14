# app/models/horario_excepcion_recep.py
from sqlalchemy import Column, Integer, Date, Boolean, Enum as SQLEnum, ForeignKey, UniqueConstraint
from app.models.base import Base


class HorarioExcepcionRecep(Base):
    """Excepción puntual por fecha al horario recurrente de la recepcionista.
    trabaja=False -> día libre; trabaja=True -> trabaja ese día en el turno indicado."""
    __tablename__ = "Horario_excepcion_recep"

    id_excepcion = Column(Integer, primary_key=True, autoincrement=True)
    id_recepcionista = Column(Integer, ForeignKey('Recepcionista.id_recepcionista', ondelete='CASCADE'), nullable=False)
    fecha = Column(Date, nullable=False)
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', 'Madrugada', name='turno_exc_recep_enum'), nullable=True)
    trabaja = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('id_recepcionista', 'fecha', name='uq_exc_recep_fecha'),
    )
