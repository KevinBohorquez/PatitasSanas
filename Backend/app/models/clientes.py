# app/models/clientes.py
from sqlalchemy import Column, Integer, String, DateTime, Text, CHAR, Enum as SQLEnum, CheckConstraint
from sqlalchemy.sql import func
from app.models.base import Base


class Cliente(Base):
    __tablename__ = "Cliente"

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    dni = Column(CHAR(8), unique=True, nullable=False)
    telefono = Column(CHAR(9), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    direccion = Column(Text)
    fecha_registro = Column(DateTime, default=func.current_timestamp())
    estado = Column(SQLEnum('Activo', 'Inactivo', name='estado_cliente_enum'))
    genero = Column(CHAR(1), nullable=False)  # ← AGREGAR ESTA LÍNEA
    
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(nombre) != '' AND LENGTH(TRIM(nombre)) >= 2", name='check_nombre_cliente'),
        CheckConstraint("TRIM(apellido_paterno) != '' AND LENGTH(TRIM(apellido_paterno)) >= 2", name='check_apellido_paterno_cliente'),
        CheckConstraint("TRIM(apellido_materno) != '' AND LENGTH(TRIM(apellido_materno)) >= 2", name='check_apellido_materno_cliente'),
        CheckConstraint("dni REGEXP '^[0-9]{8}'", name='check_dni_cliente'),
        CheckConstraint("telefono REGEXP '^9[0-9]{8}", name='check_telefono_cliente'),
        CheckConstraint("email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", name='check_email_cliente'),
        CheckConstraint("genero IN ('F', 'M')", name='check_genero_cliente'),  # ← AGREGAR ESTA LÍNEA
    )