# app/models/recepcionista.py
from sqlalchemy import Column, Integer, String, Date, CHAR, Enum as SQLEnum, CheckConstraint, ForeignKey  # ← Agregar ForeignKey aquí
from sqlalchemy.orm import relationship
from app.models.base import Base


class Recepcionista(Base):
    __tablename__ = "Recepcionista"

    id_recepcionista = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), unique=True, nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    dni = Column(CHAR(8), unique=True, nullable=False)
    telefono = Column(CHAR(9), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    fecha_ingreso = Column(Date)
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', name='turno_recepcionista_enum'))
    genero = Column(CHAR(1), nullable=False)

    usuario = relationship("Usuario", back_populates="recepcionista")
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(nombre) != '' AND LENGTH(TRIM(nombre)) >= 2", name='check_nombre_recepcionista'),
        CheckConstraint("TRIM(apellido_paterno) != '' AND LENGTH(TRIM(apellido_paterno)) >= 2", name='check_apellido_paterno_recep'),
        CheckConstraint("TRIM(apellido_materno) != '' AND LENGTH(TRIM(apellido_materno)) >= 2", name='check_apellido_materno_recep'),
        CheckConstraint("dni REGEXP '^[0-9]{8}'", name='check_dni_recepcionista'),
        CheckConstraint("telefono REGEXP '^9[0-9]{8}$'", name='check_telefono_recepcionista'),
        CheckConstraint("email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='check_email_recepcionista'),
        CheckConstraint("genero IN ('F', 'M')", name='check_genero_recepcionista'),
    )