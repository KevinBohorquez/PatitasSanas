# app/models/servicio_solicitado.py
from sqlalchemy import Column, Integer, DateTime, Text, Enum as SQLEnum, ForeignKey, CheckConstraint
from app.models.base import Base


class ServicioSolicitado(Base):
    __tablename__ = "Servicio_Solicitado"

    id_servicio_solicitado = Column(Integer, primary_key=True, autoincrement=True)
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_servicio = Column(Integer, ForeignKey('Servicio.id_servicio'))
    
    fecha_solicitado = Column(DateTime)
    prioridad = Column(SQLEnum('Urgente', 'Normal', 'Programable', name='prioridad_enum'))
    estado_examen = Column(SQLEnum(
        'Solicitado', 
        'Citado', 
        'En proceso', 
        'Completado', 
        name='estado_examen_enum'
    ), default='Solicitado')
    comentario_opcional = Column(Text)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("comentario_opcional IS NULL OR LENGTH(TRIM(comentario_opcional)) >= 3", name='check_comentario_opcional'),
    )