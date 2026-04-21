# app/models/servicio.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, CheckConstraint
from app.models.base import Base


class Servicio(Base):
    __tablename__ = "Servicio"

    id_servicio = Column(Integer, primary_key=True, autoincrement=True)
    id_tipo_servicio = Column(Integer, ForeignKey('Tipo_servicio.id_tipo_servicio'), nullable=False)
    nombre_servicio = Column(String(50), nullable=False)
    precio = Column(Numeric(6, 2), nullable=False)
    activo = Column(Boolean, default=True)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(nombre_servicio) != '' AND LENGTH(TRIM(nombre_servicio)) >= 3", name='check_nombre_servicio'),
        CheckConstraint("precio >= 0 AND precio <= 9999.99", name='check_precio_servicio'),
    )