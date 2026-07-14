# app/models/horario_veterinario.py
from sqlalchemy import Column, Integer, Enum as SQLEnum, ForeignKey, UniqueConstraint
from app.models.base import Base


class HorarioVeterinario(Base):
    """Horario recurrente semanal del veterinario: qué turno cubre cada día de la semana.
    Las excepciones puntuales por fecha se manejan en HorarioExcepcion."""
    __tablename__ = "Horario_veterinario"

    id_horario = Column(Integer, primary_key=True, autoincrement=True)
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario', ondelete='CASCADE'), nullable=False)
    dia_semana = Column(SQLEnum(
        'Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo',
        name='dia_semana_enum'
    ), nullable=False)
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', 'Madrugada', name='turno_horario_enum'), nullable=False)

    __table_args__ = (
        UniqueConstraint('id_veterinario', 'dia_semana', 'turno', name='uq_horario_vet_dia_turno'),
    )
