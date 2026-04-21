# app/models/mascota.py (CORREGIDO PARA COINCIDIR CON TU TABLA SQL)
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, Boolean, CheckConstraint
from app.models.base import Base


class Mascota(Base):
    __tablename__ = "Mascota"

    id_mascota = Column(Integer, primary_key=True, autoincrement=True)
    id_raza = Column(Integer, ForeignKey('Raza.id_raza'), nullable=False)

    nombre = Column(String(50), nullable=False)
    sexo = Column(SQLEnum('Macho', 'Hembra', name='sexo_enum'), nullable=False)
    color = Column(String(50))
    edad_anios = Column(Integer)
    edad_meses = Column(Integer)
    esterilizado = Column(Boolean, default=False)
    imagen = Column(String(50))

    # Constraints de validación (igual que tu tabla SQL)
    __table_args__ = (
        CheckConstraint("TRIM(nombre) != '' AND LENGTH(TRIM(nombre)) >= 2", name='check_nombre_mascota'),
        CheckConstraint("color IS NULL OR (TRIM(color) != '' AND LENGTH(TRIM(color)) >= 3)",
                        name='check_color_mascota'),
        CheckConstraint("edad_anios IS NULL OR (edad_anios >= 0 AND edad_anios <= 25)", name='check_edad_anios'),
        CheckConstraint("edad_meses IS NULL OR (edad_meses >= 0 AND edad_meses <= 11)", name='check_edad_meses'),
    )

# NOTA: Las relaciones con clientes se manejan a través de la tabla Cliente_Mascota
# No se definen relationships aquí para mantener la estructura simple