# app/models/raza.py
from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Raza(Base):
    __tablename__ = "Raza"

    id_raza = Column(Integer, primary_key=True, autoincrement=True)
    nombre_raza = Column(String(60), nullable=False)