# app/schemas/clientes_schema.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal
from datetime import datetime
from .base_schema import BaseResponse, PaginationResponse, validate_dni, validate_telefono, validate_name

# Validator personalizado para género
def validate_genero(v):
    """Validar que el género sea F o M"""
    if v is not None and v not in ['F', 'M']:
        raise ValueError('El género debe ser F (Femenino) o M (Masculino)')
    return v

# ===== SCHEMAS DE INPUT (REQUEST) =====

class ClienteCreate(BaseModel):
    """Schema para crear un cliente"""
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: EmailStr
    genero: Literal['F', 'M']  # Campo requerido
    direccion: Optional[str] = None
    estado: Optional[str] = "Activo"
    
    # Validators
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)
    _validate_apellido_paterno = validator('apellido_paterno', allow_reuse=True)(validate_name)
    _validate_apellido_materno = validator('apellido_materno', allow_reuse=True)(validate_name)
    _validate_dni = validator('dni', allow_reuse=True)(validate_dni)
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)
    _validate_genero = validator('genero', allow_reuse=True)(validate_genero)


class ClienteUpdate(BaseModel):
    """Schema para actualizar un cliente"""
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    genero: Optional[Literal['F', 'M']] = None  # Campo opcional para actualización
    direccion: Optional[str] = None
    estado: Optional[str] = None
    
    # Validators
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)
    _validate_apellido_paterno = validator('apellido_paterno', allow_reuse=True)(validate_name)
    _validate_apellido_materno = validator('apellido_materno', allow_reuse=True)(validate_name)
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)
    _validate_genero = validator('genero', allow_reuse=True)(validate_genero)


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class ClienteResponse(BaseResponse):
    """Schema para devolver información de cliente"""
    id_cliente: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: str
    genero: str  # Campo incluido en la respuesta
    direccion: Optional[str]
    fecha_registro: Optional[datetime]
    estado: Optional[str]


class ClienteListResponse(PaginationResponse):
    """Schema para lista de clientes"""
    clientes: list[ClienteResponse]


# ===== SCHEMAS DE BÚSQUEDA =====

class ClienteSearch(BaseModel):
    """Schema para búsqueda de clientes"""
    nombre: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[str] = None
    estado: Optional[str] = None
    genero: Optional[Literal['F', 'M']] = None  # Filtro por género
    page: int = 1
    per_page: int = 20