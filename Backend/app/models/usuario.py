# app/models/usuario.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum as SQLEnum, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    contraseña = Column(String(60), nullable=False)
    tipo_usuario = Column(SQLEnum('Veterinario', 'Recepcionista', 'Administrador', name='tipo_usuario_enum'),
                          nullable=False)
    fecha_creacion = Column(TIMESTAMP, default=func.current_timestamp())
    estado = Column(SQLEnum('Activo', 'Inactivo', name='estado_usuario_enum'), default='Activo')

    # Relaciones con otras tablas
    administrador = relationship("Administrador", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    veterinario = relationship("Veterinario", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    recepcionista = relationship("Recepcionista", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

    # Constraints de validación
    __table_args__ = (
        CheckConstraint("LENGTH(contraseña) >= 3", name='check_contraseña_length'),
        CheckConstraint("LENGTH(TRIM(username)) >= 3", name='check_username_length'),
    )

    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, username='{self.username}', tipo='{self.tipo_usuario}', estado='{self.estado}')>"

    @property
    def is_active(self):
        """Propiedad para verificar si el usuario está activo"""
        return self.estado == 'Activo'

    @property
    def is_admin(self):
        """Propiedad para verificar si es administrador"""
        return self.tipo_usuario == 'Administrador'

    @property
    def is_veterinario(self):
        """Propiedad para verificar si es veterinario"""
        return self.tipo_usuario == 'Veterinario'

    @property
    def is_recepcionista(self):
        """Propiedad para verificar si es recepcionista"""
        return self.tipo_usuario == 'Recepcionista'

    def get_perfil(self):
        """Método para obtener el perfil específico del usuario"""
        if self.tipo_usuario == 'Administrador':
            return self.administrador
        elif self.tipo_usuario == 'Veterinario':
            return self.veterinario
        elif self.tipo_usuario == 'Recepcionista':
            return self.recepcionista
        return None

    def get_nombre_completo(self):
        """Método para obtener el nombre completo del usuario"""
        perfil = self.get_perfil()
        if perfil:
            return f"{perfil.nombre} {perfil.apellido_paterno} {perfil.apellido_materno}"
        return self.username

    def activate(self):
        """Método para activar el usuario"""
        self.estado = 'Activo'

    def deactivate(self):
        """Método para desactivar el usuario"""
        self.estado = 'Inactivo'

    def change_password(self, new_password: str):
        """Método para cambiar la contraseña (deberá ser hasheada externamente)"""
        if len(new_password) < 3:
            raise ValueError("La contraseña debe tener al menos 3 caracteres")
        self.contraseña = new_password