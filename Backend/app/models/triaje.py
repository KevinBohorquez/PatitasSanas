# app/models/triaje.py
from sqlalchemy import Column, Integer, DateTime, Numeric, String, Enum as SQLEnum, ForeignKey, CheckConstraint
from app.models.base import Base


class Triaje(Base):
    __tablename__ = "Triaje"

    id_triaje = Column(Integer, primary_key=True, autoincrement=True)
    id_solicitud = Column(Integer, ForeignKey('Solicitud_atencion.id_solicitud'), nullable=False)
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'), nullable=False)
    fecha_hora_triaje = Column(DateTime, nullable=False)
    
    peso_mascota = Column(Numeric(5, 2), nullable=False)
    latido_por_minuto = Column(Integer, nullable=False)
    frecuencia_respiratoria_rpm = Column(Integer, nullable=False)
    temperatura = Column(Numeric(4, 2), nullable=False)
    talla = Column(Numeric(5, 2))
    tiempo_capilar = Column(String(50))
    color_mucosas = Column(String(50))
    frecuencia_pulso = Column(Integer, nullable=False)
    porce_deshidratacion = Column(Numeric(4, 2))
    condicion_corporal = Column(SQLEnum(
        'Muy delgado', 
        'Delgado', 
        'Ideal', 
        'Sobrepeso', 
        'Obeso', 
        name='condicion_corporal_enum'
    ), default='Ideal')
    clasificacion_urgencia = Column(SQLEnum(
        'No urgente', 
        'Poco urgente', 
        'Urgente', 
        'Muy urgente', 
        'Critico', 
        name='clasificacion_urgencia_enum'
    ), nullable=False)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("peso_mascota > 0 AND peso_mascota <= 100", name='check_peso_mascota'),
        CheckConstraint("latido_por_minuto BETWEEN 40 AND 300", name='check_latido_por_minuto'),
        CheckConstraint("frecuencia_respiratoria_rpm BETWEEN 10 AND 150", name='check_frecuencia_respiratoria'),
        CheckConstraint("temperatura BETWEEN 35.0 AND 42.0", name='check_temperatura'),
        CheckConstraint("talla IS NULL OR (talla > 0 AND talla <= 200)", name='check_talla'),
        CheckConstraint("tiempo_capilar IS NULL OR LENGTH(TRIM(tiempo_capilar)) >= 1", name='check_tiempo_capilar'),
        CheckConstraint("color_mucosas IS NULL OR LENGTH(TRIM(color_mucosas)) >= 3", name='check_color_mucosas'),
        CheckConstraint("frecuencia_pulso BETWEEN 30 AND 250", name='check_frecuencia_pulso'),
        CheckConstraint("porce_deshidratacion >= 0 AND porce_deshidratacion <= 100", name='check_porce_deshidratacion'),
    )