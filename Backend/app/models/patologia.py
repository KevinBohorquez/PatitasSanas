# app/models/patologia.py
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, CheckConstraint
from app.models.base import Base


class Patologia(Base):
    __tablename__ = "Patologia"

    id_patologia = Column(Integer, primary_key=True, autoincrement=True)
    nombre_patologia = Column(String(100), nullable=False, unique=True)
    especie_afecta = Column(SQLEnum('Perro', 'Gato', 'Ambas', name='especie_afecta_enum'), nullable=False)
    gravedad = Column(SQLEnum(
        'Leve', 
        'Moderada', 
        'Grave', 
        'Critica', 
        name='gravedad_enum'
    ), default='Moderada')
    es_crónica = Column(Boolean)
    es_contagiosa = Column(Boolean)
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(nombre_patologia) != '' AND LENGTH(TRIM(nombre_patologia)) >= 3", name='check_nombre_patologia'),
    )