# app/models/tratamiento.py
from sqlalchemy import Column, Integer, Date, Enum as SQLEnum, ForeignKey
from app.models.base import Base


class Tratamiento(Base):
    __tablename__ = "Tratamiento"

    id_tratamiento = Column(Integer, primary_key=True, autoincrement=True)
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_patologia = Column(Integer, ForeignKey('Patologia.id_patologia'))
    
    fecha_inicio = Column(Date, nullable=False)
    eficacia_tratamiento = Column(SQLEnum(
        'Muy buena', 
        'Buena', 
        'Regular', 
        'Mala', 
        name='eficacia_tratamiento_enum'
    ))
    tipo_tratamiento = Column(SQLEnum(
        'Medicamentoso', 
        'Quirurgico', 
        'Terapeutico', 
        'Preventivo', 
        name='tipo_tratamiento_enum'
    ), nullable=False)