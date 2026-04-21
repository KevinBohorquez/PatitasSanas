# app/models/resultado_servicio.py
from sqlalchemy import Column, Integer, DateTime, Text, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class ResultadoServicio(Base):
    __tablename__ = "Resultado_servicio"

    id_resultado = Column(Integer, primary_key=True, autoincrement=True)
    id_cita = Column(Integer, ForeignKey('Cita.id_cita'))
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'))
    
    resultado = Column(Text, nullable=False)
    interpretacion = Column(Text)
    archivo_adjunto = Column(String(100))
    fecha_realizacion = Column(DateTime, nullable=False)

    cita = relationship("Cita", backref="resultados")

    # Constraints de validación
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(resultado)) >= 5", name='check_resultado'),
        CheckConstraint("interpretacion IS NULL OR LENGTH(TRIM(interpretacion)) >= 5", name='check_interpretacion'),
        CheckConstraint("archivo_adjunto IS NULL OR LENGTH(TRIM(archivo_adjunto)) >= 5", name='check_archivo_adjunto'),
    )