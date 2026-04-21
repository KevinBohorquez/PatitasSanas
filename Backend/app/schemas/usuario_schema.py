# app/schemas/usuario_schema.py
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from .base_schema import BaseResponse, PaginationResponse, validate_name

# ===== ENUMS =====
TIPO_USUARIO_CHOICES = ['Administrador', 'Veterinario', 'Recepcionista']
ESTADO_USUARIO_CHOICES = ['Activo', 'Inactivo']


# ===== SCHEMAS DE INPUT (REQUEST) =====

class UsuarioCreate(BaseModel):
    """Schema para crear un usuario"""
    username: str
    contraseña: str
    tipo_usuario: str
    estado: Optional[str] = "Activo"

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

    @validator('tipo_usuario')
    def validate_tipo_usuario(cls, v):
        if v not in TIPO_USUARIO_CHOICES:
            raise ValueError(f'Tipo debe ser uno de: {", ".join(TIPO_USUARIO_CHOICES)}')
        return v

    @validator('estado')
    def validate_estado(cls, v):
        if v and v not in ESTADO_USUARIO_CHOICES:
            raise ValueError(f'Estado debe ser uno de: {", ".join(ESTADO_USUARIO_CHOICES)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "admin001",
                "contraseña": "password123",
                "tipo_usuario": "Administrador",
                "estado": "Activo"
            }
        }


class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario"""
    username: Optional[str] = None
    contraseña: Optional[str] = None
    estado: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('Username debe tener al menos 3 caracteres')
        return v.strip().lower() if v else v

    @validator('contraseña')
    def validate_contraseña(cls, v):
        if v and len(v) < 3:
            raise ValueError('Contraseña debe tener al menos 3 caracteres')
        return v

    @validator('estado')
    def validate_estado(cls, v):
        if v and v not in ESTADO_USUARIO_CHOICES:
            raise ValueError(f'Estado debe ser uno de: {", ".join(ESTADO_USUARIO_CHOICES)}')
        return v


class UsuarioLogin(BaseModel):
    """Schema para login de usuario"""
    username: str
    contraseña: str

    class Config:
        schema_extra = {
            "example": {
                "username": "admin001",
                "contraseña": "password123"
            }
        }


class PasswordChange(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str
    new_password: str
    confirm_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 3:
            raise ValueError('Nueva contraseña debe tener al menos 3 caracteres')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v


class PasswordReset(BaseModel):
    """Schema para reseteo de contraseña"""
    username: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 3:
            raise ValueError('Nueva contraseña debe tener al menos 3 caracteres')
        return v


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class UsuarioResponse(BaseResponse):
    """Schema para devolver información de usuario"""
    id_usuario: int
    username: str
    tipo_usuario: str
    estado: str
    fecha_creacion: datetime


class UsuarioWithProfileResponse(UsuarioResponse):
    """Schema para usuario con perfil"""
    perfil: Optional[dict] = None
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    dni: Optional[str] = None


class UsuarioListResponse(PaginationResponse):
    """Schema para lista de usuarios"""
    usuarios: List[UsuarioResponse]


class AuthResponse(BaseModel):
    """Schema para respuesta de autenticación"""
    success: bool
    message: str
    usuario: Optional[UsuarioResponse] = None
    tipo_usuario: Optional[str] = None
    permisos: Optional[dict] = None
    session_info: Optional[dict] = None


class SessionInfoResponse(BaseModel):
    """Schema para información de sesión"""
    user_id: int
    username: str
    tipo_usuario: str
    estado: str
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    dni: Optional[str] = None
    permisos: dict


class EstadisticasUsuarios(BaseModel):
    """Schema para estadísticas de usuarios"""
    total_usuarios: int
    usuarios_activos: int
    usuarios_inactivos: int
    porcentaje_activos: float
    por_tipo: dict


# ===== SCHEMAS DE BÚSQUEDA =====

class UsuarioSearch(BaseModel):
    """Schema para búsqueda de usuarios"""
    username: Optional[str] = None
    tipo_usuario: Optional[str] = None
    estado: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    page: int = 1
    per_page: int = 20

    @validator('tipo_usuario')
    def validate_tipo_usuario(cls, v):
        if v and v not in TIPO_USUARIO_CHOICES:
            raise ValueError(f'Tipo debe ser uno de: {", ".join(TIPO_USUARIO_CHOICES)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "tipo_usuario": "Administrador",
                "estado": "Activo",
                "page": 1,
                "per_page": 20
            }
        }