# app/schemas/recepcionista_schema.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date
from .base_schema import BaseResponse, PaginationResponse, validate_dni, validate_telefono, validate_name


# ===== SCHEMAS DE INPUT (REQUEST) =====

class RecepcionistaCreate(BaseModel):
    """Schema para crear un recepcionista"""
    id_usuario: int  # ← AGREGADO: ID del usuario ya creado
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: EmailStr  # Para validar que coincida con el usuario
    fecha_ingreso: Optional[date] = None
    turno: Optional[str] = None  # 'Mañana', 'Tarde', 'Noche'
    genero: str  # 'F' o 'M'

    # Validators
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)
    _validate_apellido_paterno = validator('apellido_paterno', allow_reuse=True)(validate_name)
    _validate_apellido_materno = validator('apellido_materno', allow_reuse=True)(validate_name)
    _validate_dni = validator('dni', allow_reuse=True)(validate_dni)
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)

    @validator('turno')
    def validate_turno(cls, v):
        if v and v not in ['Mañana', 'Tarde', 'Noche']:
            raise ValueError('Turno debe ser Mañana, Tarde o Noche')
        return v

    @validator('genero')
    def validate_genero(cls, v):
        if v not in ['F', 'M']:
            raise ValueError('Género debe ser F o M')
        return v


class RecepcionistaUpdate(BaseModel):
    """Schema para actualizar un recepcionista"""
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    turno: Optional[str] = None

    # Validators similares a Create
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)
    _validate_apellido_paterno = validator('apellido_paterno', allow_reuse=True)(validate_name)
    _validate_apellido_materno = validator('apellido_materno', allow_reuse=True)(validate_name)
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class RecepcionistaResponse(BaseResponse):
    """Schema para devolver información de recepcionista"""
    id_recepcionista: int
    id_usuario: int  # ← AGREGADO: Para mostrar la relación
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: str
    fecha_ingreso: Optional[date]
    turno: Optional[str]
    genero: str
    # Nota: NO incluimos contraseña por seguridad


class RecepcionistaWithUserResponse(RecepcionistaResponse):
    """Schema para recepcionista con información del usuario"""
    usuario_estado: Optional[str] = None  # Estado del usuario asociado
    usuario_tipo: Optional[str] = None  # Tipo del usuario asociado


class RecepcionistaListResponse(PaginationResponse):
    """Schema para lista de recepcionistas"""
    recepcionistas: list[RecepcionistaResponse]


# ===== SCHEMAS DE BÚSQUEDA =====

class RecepcionistaSearch(BaseModel):
    """Schema para búsqueda de recepcionistas"""
    nombre: Optional[str] = None
    dni: Optional[str] = None
    turno: Optional[str] = None
    id_usuario: Optional[int] = None  # ← AGREGADO: Para buscar por usuario
    page: int = 1
    per_page: int = 20