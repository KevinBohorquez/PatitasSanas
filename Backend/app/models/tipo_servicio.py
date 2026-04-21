# app/models/tipo_servicio.py
from sqlalchemy import Column, Integer, String
from app.models.base import Base


class TipoServicio(Base):
    __tablename__ = "Tipo_servicio"

    id_tipo_servicio = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(50), nullable=False)