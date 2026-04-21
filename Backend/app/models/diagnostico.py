# app/models/diagnostico.py
from sqlalchemy import Column, Integer, DateTime, Text, Enum as SQLEnum, ForeignKey, CheckConstraint
from app.models.base import Base


class Diagnostico(Base):
    __tablename__ = "Diagnostico"

    id_diagnostico = Column(Integer, primary_key=True, autoincrement=True)
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_patologia = Column(Integer, ForeignKey('Patologia.id_patologia'))
    
    tipo_diagnostico = Column(SQLEnum(
        'Presuntivo', 
        'Confirmado', 
        'Descartado', 
        name='tipo_diagnostico_enum'
    ), nullable=False, default='Presuntivo')
    fecha_diagnostico = Column(DateTime, nullable=False)
    estado_patologia = Column(SQLEnum(
        'Activa', 
        'Controlada', 
        'Curada', 
        'En seguimiento', 
        name='estado_patologia_enum'
    ), nullable=False, default='Activa')
    diagnostico = Column(Text, nullable=False)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(diagnostico)) >= 5", name='check_diagnostico'),
    )