# app/models/horario_recepcionista.py
from sqlalchemy import Column, Integer, Enum as SQLEnum, ForeignKey, UniqueConstraint
from app.models.base import Base


class HorarioRecepcionista(Base):
    """Horario recurrente semanal de la recepcionista (espejo del de veterinarios)."""
    __tablename__ = "Horario_recepcionista"

    id_horario = Column(Integer, primary_key=True, autoincrement=True)
    id_recepcionista = Column(Integer, ForeignKey('Recepcionista.id_recepcionista', ondelete='CASCADE'), nullable=False)
    dia_semana = Column(SQLEnum(
        'Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo',
        name='dia_semana_recep_enum'
    ), nullable=False)
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', 'Madrugada', name='turno_horario_recep_enum'), nullable=False)

    __table_args__ = (
        UniqueConstraint('id_recepcionista', 'dia_semana', 'turno', name='uq_horario_recep_dia_turno'),
    )
