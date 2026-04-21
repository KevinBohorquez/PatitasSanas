# app/models/especialidad.py
from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Especialidad(Base):
    __tablename__ = "Especialidad"

    id_especialidad = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(50), nullable=False)