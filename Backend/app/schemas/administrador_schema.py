# app/schemas/administrador_schema.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date
from .base_schema import BaseResponse, PaginationResponse, validate_dni, validate_telefono, validate_name


# ===== SCHEMAS DE INPUT (REQUEST) =====

class AdministradorCreate(BaseModel):
    """Schema para crear un administrador"""
    # Datos de usuario
    username: str
    contraseña: str

    # Datos de perfil
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: EmailStr
    fecha_ingreso: date
    genero: str  # 'F' o 'M'

    # Validators
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)
    _validate_apellido_paterno = validator('apellido_paterno', allow_reuse=True)(validate_name)
    _validate_apellido_materno = validator('apellido_materno', allow_reuse=True)(validate_name)
    _validate_dni = validator('dni', allow_reuse=True)(validate_dni)
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)

    @validator('username')
    def validate_username(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Username debe tener al menos 3 caracteres')
        return v.strip().lower()

    @validator('contraseña')
    def validate_contraseña(cls, v):
        if len(v) < 3:
            raise ValueError('Contraseña debe tener al menos 3 caracteres')
        return v

    @validator('genero')
    def validate_genero(cls, v):
        if v not in ['F', 'M']:
            raise ValueError('Género debe ser F o M')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "admin001",
                "contraseña": "password123",
                "nombre": "Juan",
                "apellido_paterno": "Pérez",
                "apellido_materno": "García",
                "dni": "12345678",
                "telefono": "987654321",
                "email": "admin@veterinaria.com",
                "fecha_ingreso": "2024-01-15",
                "genero": "M"
            }
        }


class AdministradorUpdate(BaseModel):
    """Schema para actualizar un administrador"""
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    genero: Optional[str] = None

    # Validators
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)
    _validate_apellido_paterno = validator('apellido_paterno', allow_reuse=True)(validate_name)
    _validate_apellido_materno = validator('apellido_materno', allow_reuse=True)(validate_name)
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)

    @validator('genero')
    def validate_genero(cls, v):
        if v and v not in ['F', 'M']:
            raise ValueError('Género debe ser F o M')
        return v


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class AdministradorResponse(BaseResponse):
    """Schema para devolver información de administrador"""
    id_administrador: int
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: str
    fecha_ingreso: date
    genero: str


class AdministradorWithUsuarioResponse(AdministradorResponse):
    """Schema para administrador con información de usuario"""
    usuario: Optional[dict] = None


class AdministradorListResponse(PaginationResponse):
    """Schema para lista de administradores"""
    administradores: List[AdministradorResponse]


class AdministradorCompleteResponse(AdministradorResponse):
    """Schema para administrador con información completa"""
    username: str
    estado_usuario: str
    fecha_creacion_usuario: Optional[date] = None
    nombre_completo: str
    genero_descripcion: str


class EstadisticasAdministradores(BaseModel):
    """Schema para estadísticas de administradores"""
    total_administradores: int
    activos: int
    inactivos: int
    por_genero: dict
    por_año_ingreso: List[dict]
    porcentaje_activos: float


# ===== SCHEMAS DE BÚSQUEDA =====

class AdministradorSearch(BaseModel):
    """Schema para búsqueda de administradores"""
    nombre: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[str] = None
    genero: Optional[str] = None
    fecha_ingreso_desde: Optional[date] = None
    fecha_ingreso_hasta: Optional[date] = None
    page: int = 1
    per_page: int = 20

    @validator('genero')
    def validate_genero(cls, v):
        if v and v not in ['F', 'M']:
            raise ValueError('Género debe ser F o M')
        return v

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Juan",
                "genero": "M",
                "fecha_ingreso_desde": "2024-01-01",
                "page": 1,
                "per_page": 20
            }
        }


# ===== SCHEMAS ESPECÍFICOS =====

class AdministradorPasswordChange(BaseModel):
    """Schema para cambio de contraseña de administrador"""
    admin_id: int
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 3:
            raise ValueError('Nueva contraseña debe tener al menos 3 caracteres')
        return v


class AdministradorActivation(BaseModel):
    """Schema para activar/desactivar administrador"""
    admin_id: int
    action: str  # 'activate' o 'deactivate'

    @validator('action')
    def validate_action(cls, v):
        if v not in ['activate', 'deactivate']:
            raise ValueError('Acción debe ser activate o deactivate')
        return v