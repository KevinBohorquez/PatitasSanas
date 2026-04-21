# app/models/historial_clinico.py
from sqlalchemy import Column, Integer, DateTime, String, Text, Numeric, ForeignKey, CheckConstraint
from app.models.base import Base


class HistorialClinico(Base):
    __tablename__ = "Historial_clinico"

    id_historial = Column(Integer, primary_key=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_diagnostico = Column(Integer, ForeignKey('Diagnostico.id_diagnostico'))
    id_tratamiento = Column(Integer, ForeignKey('Tratamiento.id_tratamiento'))
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'))
    
    fecha_evento = Column(DateTime, nullable=False)
    tipo_evento = Column(String(100), nullable=False)
    edad_meses = Column(Integer)
    descripcion_evento = Column(Text, nullable=False)
    peso_momento = Column(Numeric(5, 2))
    observaciones = Column(Text)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(tipo_evento) != '' AND LENGTH(TRIM(tipo_evento)) >= 4", name='check_tipo_evento'),
        CheckConstraint("edad_meses >= 0 AND edad_meses <= 300", name='check_edad_meses_historial'),
        CheckConstraint("LENGTH(TRIM(descripcion_evento)) >= 5", name='check_descripcion_evento'),
        CheckConstraint("peso_momento > 0 AND peso_momento <= 200", name='check_peso_momento'),
        CheckConstraint("observaciones IS NULL OR LENGTH(TRIM(observaciones)) >= 3", name='check_observaciones_historial'),
    )