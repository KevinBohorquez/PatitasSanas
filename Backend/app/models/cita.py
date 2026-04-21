# app/models/cita.py
from sqlalchemy import Column, Integer, DateTime, Text, Boolean, Enum as SQLEnum, ForeignKey, CheckConstraint
from app.models.base import Base


class Cita(Base):
    __tablename__ = "Cita"

    id_cita = Column(Integer, primary_key=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))
    id_servicio_solicitado = Column(Integer, ForeignKey('Servicio_Solicitado.id_servicio_solicitado'))
    
    fecha_hora_programada = Column(DateTime, nullable=False)
    estado_cita = Column(SQLEnum(
        'Programada', 
        'Cancelada', 
        'Atendida', 
        name='estado_cita_enum'
    ), default='Programada')
    requiere_ayuno = Column(Boolean)
    observaciones = Column(Text)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("observaciones IS NULL OR LENGTH(TRIM(observaciones)) >= 3", name='check_observaciones_cita'),
    )