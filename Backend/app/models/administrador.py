# app/models/administrador.py
from sqlalchemy import Column, Integer, String, Date, CHAR, Enum as SQLEnum, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Administrador(Base):
    __tablename__ = "Administrador"

    id_administrador = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), unique=True, nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    dni = Column(CHAR(8), unique=True, nullable=False)
    telefono = Column(CHAR(9), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    genero = Column(CHAR(1), nullable=False)

    # Relación con la tabla usuarios
    usuario = relationship("Usuario", back_populates="administrador")

    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(nombre) != '' AND LENGTH(TRIM(nombre)) >= 2", name='check_nombre_admin'),
        CheckConstraint("TRIM(apellido_paterno) != '' AND LENGTH(TRIM(apellido_paterno)) >= 2",
                        name='check_apellido_paterno_admin'),
        CheckConstraint("TRIM(apellido_materno) != '' AND LENGTH(TRIM(apellido_materno)) >= 2",
                        name='check_apellido_materno_admin'),
        CheckConstraint("dni REGEXP '^[0-9]{8}$'", name='check_dni_admin'),
        CheckConstraint("telefono REGEXP '^9[0-9]{8}$'", name='check_telefono_admin'),
        CheckConstraint("email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='check_email_admin'),
        CheckConstraint("genero IN ('F', 'M')", name='check_genero_admin'),
    )

    def __repr__(self):
        return f"<Administrador(id={self.id_administrador}, nombre='{self.nombre} {self.apellido_paterno}', dni='{self.dni}')>"

    @property
    def nombre_completo(self):
        """Propiedad para obtener el nombre completo"""
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    @property
    def genero_descripcion(self):
        """Propiedad para obtener la descripción del género"""
        return "Femenino" if self.genero == 'F' else "Masculino"