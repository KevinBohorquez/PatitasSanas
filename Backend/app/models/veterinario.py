# app/models/veterinario.py
from sqlalchemy import Column, Integer, String, Date, CHAR, Enum as SQLEnum, ForeignKey, CheckConstraint
from app.models.base import Base
from sqlalchemy.orm import relationship  # ← ASEGÚRATE DE TENER ESTO



class Veterinario(Base):
    __tablename__ = "Veterinario"

    id_veterinario = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), unique=True, nullable=False)
    id_especialidad = Column(Integer, ForeignKey('Especialidad.id_especialidad'), nullable=False)
    codigo_CMVP = Column(String(20), nullable=False)
    tipo_veterinario = Column(SQLEnum('Medico General', 'Especializado', name='tipo_veterinario_enum'), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(CHAR(1), nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    dni = Column(CHAR(8), unique=True, nullable=False)
    telefono = Column(CHAR(9), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    disposicion = Column(SQLEnum('Ocupado', 'Fuera de turno', 'Libre', name='disposicion_enum'), default='Libre')
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', name='turno_enum'), nullable=False)

    usuario = relationship("Usuario", back_populates="veterinario")
    especialidad = relationship("Especialidad")

    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(codigo_CMVP) != '' AND LENGTH(TRIM(codigo_CMVP)) >= 6", name='check_codigo_cmvp'),
        CheckConstraint("genero IN ('F', 'M')", name='check_genero'),
        CheckConstraint("TRIM(nombre) != '' AND LENGTH(TRIM(nombre)) >= 2", name='check_nombre_veterinario'),
        CheckConstraint("TRIM(apellido_paterno) != '' AND LENGTH(TRIM(apellido_paterno)) >= 2", name='check_apellido_paterno_vet'),
        CheckConstraint("TRIM(apellido_materno) != '' AND LENGTH(TRIM(apellido_materno)) >= 2", name='check_apellido_materno_vet'),
        CheckConstraint("dni REGEXP '^[0-9]{8}'", name='check_dni_veterinario'),
        CheckConstraint("telefono REGEXP '^9[0-9]{8}", name='check_telefono_veterinario'),
        CheckConstraint("email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", name='check_email_veterinario'),
    )