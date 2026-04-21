# app/models/consulta.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey, Boolean, CheckConstraint
from app.models.base import Base


class Consulta(Base):
    __tablename__ = "Consulta"

    id_consulta = Column(Integer, primary_key=True, autoincrement=True)
    id_triaje = Column(Integer, ForeignKey('Triaje.id_triaje'), nullable=False)
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'), nullable=False)
    
    tipo_consulta = Column(String(100), nullable=False)
    fecha_consulta = Column(DateTime, nullable=False)
    motivo_consulta = Column(Text)
    sintomas_observados = Column(Text)
    diagnostico_preliminar = Column(Text)
    observaciones = Column(Text)
    condicion_general = Column(SQLEnum(
        'Excelente', 
        'Buena', 
        'Regular', 
        'Mala', 
        'Critica', 
        name='condicion_general_enum'
    ), nullable=False)
    es_seguimiento = Column(Boolean, default=False)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(tipo_consulta) != '' AND LENGTH(TRIM(tipo_consulta)) >= 5", name='check_tipo_consulta'),
        CheckConstraint("motivo_consulta IS NULL OR LENGTH(TRIM(motivo_consulta)) >= 5", name='check_motivo_consulta'),
        CheckConstraint("sintomas_observados IS NULL OR LENGTH(TRIM(sintomas_observados)) >= 5", name='check_sintomas_observados'),
        CheckConstraint("diagnostico_preliminar IS NULL OR LENGTH(TRIM(diagnostico_preliminar)) >= 5", name='check_diagnostico_preliminar'),
        CheckConstraint("observaciones IS NULL OR LENGTH(TRIM(observaciones)) >= 3", name='check_observaciones_consulta'),
    )