# app/models/tipo_animal.py
from sqlalchemy import Column, Integer, Enum as SQLEnum, ForeignKey
from app.models.base import Base


class TipoAnimal(Base):
    __tablename__ = "Tipo_animal"

    id_tipo_animal = Column(Integer, primary_key=True, autoincrement=True)
    id_raza = Column(Integer, ForeignKey('Raza.id_raza'), nullable=False)
    descripcion = Column(SQLEnum('Perro', 'Gato', name='tipo_animal_enum'), nullable=False)