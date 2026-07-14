# app/models/horario_excepcion.py
from sqlalchemy import Column, Integer, Date, Boolean, Enum as SQLEnum, ForeignKey, UniqueConstraint
from app.models.base import Base


class HorarioExcepcion(Base):
    """Excepción puntual al horario recurrente en una fecha concreta.
    trabaja=False -> el veterinario NO trabaja ese día (día libre), turno se ignora.
    trabaja=True  -> trabaja ese día en el turno indicado (turno extra o cambio)."""
    __tablename__ = "Horario_excepcion"

    id_excepcion = Column(Integer, primary_key=True, autoincrement=True)
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario', ondelete='CASCADE'), nullable=False)
    fecha = Column(Date, nullable=False)
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', 'Madrugada', name='turno_excepcion_enum'), nullable=True)
    trabaja = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('id_veterinario', 'fecha', name='uq_excepcion_vet_fecha'),
    )
