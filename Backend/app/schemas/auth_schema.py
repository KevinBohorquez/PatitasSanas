# app/schemas/auth_schema.py
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base_schema import BaseResponse


# ===== SCHEMAS DE INPUT (REQUEST) =====

class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    username: str
    password: str

    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username debe tener al menos 3 caracteres')
        return v.strip().lower()

    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Password debe tener al menos 3 caracteres')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "admin001",
                "password": "password123"
            }
        }


class PasswordChangeRequest(BaseModel):
    """Schema para cambio de contraseña"""
    user_id: int
    current_password: str
    new_password: str
    confirm_password: str

    @validator('current_password')
    def validate_current_password(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Contraseña actual requerida')
        return v

    @validator('new_password')
    def validate_new_password(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Nueva contraseña debe tener al menos 3 caracteres')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "current_password": "oldpassword123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }


class PasswordResetRequest(BaseModel):
    """Schema para reseteo de contraseña (solo administradores)"""
    username: str
    new_password: str
    admin_confirmation: bool = False

    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username debe tener al menos 3 caracteres')
        return v.strip().lower()

    @validator('new_password')
    def validate_new_password(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Nueva contraseña debe tener al menos 3 caracteres')
        return v

    @validator('admin_confirmation')
    def validate_admin_confirmation(cls, v):
        if not v:
            raise ValueError('Se requiere confirmación del administrador')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "vet001",
                "new_password": "newpassword123",
                "admin_confirmation": True
            }
        }


class UserStatusValidationRequest(BaseModel):
    """Schema para validación de estado de usuario"""
    user_id: int


class UserBlockRequest(BaseModel):
    """Schema para bloqueo temporal de usuario"""
    user_id: int
    minutes: int = 30
    reason: Optional[str] = None

    @validator('minutes')
    def validate_minutes(cls, v):
        if v < 1 or v > 1440:  # Máximo 24 horas
            raise ValueError('Los minutos deben estar entre 1 y 1440 (24 horas)')
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "minutes": 30,
                "reason": "Intentos de login fallidos"
            }
        }


class PermissionCheckRequest(BaseModel):
    """Schema para verificación de permisos"""
    user_type: str
    permission: str

    @validator('user_type')
    def validate_user_type(cls, v):
        valid_types = ['Administrador', 'Veterinario', 'Recepcionista']
        if v not in valid_types:
            raise ValueError(f'Tipo de usuario debe ser uno de: {", ".join(valid_types)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_type": "Veterinario",
                "permission": "realizar_triaje"
            }
        }


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class UserProfileResponse(BaseModel):
    """Schema para perfil de usuario en respuestas de auth"""
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    dni: str
    # Campos específicos por tipo se agregarán dinámicamente


class LoginResponse(BaseResponse):
    """Schema para respuesta de login exitoso"""
    success: bool
    message: str
    user_info: Dict[str, Any]
    session_info: Dict[str, Any]
    permisos: Dict[str, bool]
    tipo_usuario: str

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Login exitoso",
                "user_info": {
                    "id_usuario": 1,
                    "username": "admin001",
                    "tipo_usuario": "Administrador"
                },
                "session_info": {
                    "user_id": 1,
                    "username": "admin001",
                    "nombre_completo": "Juan Pérez García",
                    "email": "admin@veterinaria.com"
                },
                "permisos": {
                    "ver_dashboard": True,
                    "gestionar_usuarios": True
                },
                "tipo_usuario": "Administrador"
            }
        }


class LoginErrorResponse(BaseModel):
    """Schema para respuesta de login fallido"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    attempts_remaining: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "Credenciales inválidas",
                "error_code": "INVALID_CREDENTIALS",
                "attempts_remaining": 2
            }
        }


class PasswordChangeResponse(BaseModel):
    """Schema para respuesta de cambio de contraseña"""
    success: bool
    message: str
    user_id: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Contraseña cambiada exitosamente",
                "user_id": 1
            }
        }


class PasswordResetResponse(BaseModel):
    """Schema para respuesta de reseteo de contraseña"""
    success: bool
    message: str
    username: Optional[str] = None
    reset_by: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Contraseña reseteada exitosamente",
                "username": "vet001",
                "reset_by": "admin001"
            }
        }


class SessionInfoResponse(BaseModel):
    """Schema para información de sesión del usuario"""
    user_id: int
    username: str
    tipo_usuario: str
    estado: str
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    dni: Optional[str] = None
    permisos: Dict[str, bool]
    session_data: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "username": "vet001",
                "tipo_usuario": "Veterinario",
                "estado": "Activo",
                "nombre_completo": "Dr. Juan Pérez García",
                "email": "vet001@veterinaria.com",
                "dni": "12345678",
                "permisos": {
                    "realizar_triaje": True,
                    "realizar_consultas": True,
                    "gestionar_usuarios": False
                },
                "session_data": {
                    "codigo_cmvp": "CMVP12345",
                    "especialidad_id": 1,
                    "disposicion": "Libre",
                    "turno": "Mañana"
                }
            }
        }


class UserStatusValidationResponse(BaseModel):
    """Schema para respuesta de validación de estado"""
    valid: bool
    message: str
    user_id: int
    status_details: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "valid": True,
                "message": "Usuario válido",
                "user_id": 1,
                "status_details": {
                    "estado": "Activo",
                    "ultimo_login": "2024-01-15T10:30:00",
                    "bloqueado": False
                }
            }
        }


class PermissionCheckResponse(BaseModel):
    """Schema para respuesta de verificación de permisos"""
    has_permission: bool
    user_type: str
    permission: str
    message: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "has_permission": True,
                "user_type": "Veterinario",
                "permission": "realizar_triaje",
                "message": "Permiso concedido"
            }
        }


class UserPermissionsResponse(BaseModel):
    """Schema para respuesta completa de permisos de usuario"""
    user_type: str
    permisos: Dict[str, bool]
    total_permisos: int
    permisos_activos: int

    class Config:
        schema_extra = {
            "example": {
                "user_type": "Veterinario",
                "permisos": {
                    "ver_dashboard": True,
                    "gestionar_usuarios": False,
                    "realizar_triaje": True,
                    "realizar_consultas": True
                },
                "total_permisos": 13,
                "permisos_activos": 8
            }
        }


class ActiveSessionsResponse(BaseModel):
    """Schema para respuesta de sesiones activas"""
    total_sessions: int
    sessions: List[Dict[str, Any]]
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "total_sessions": 3,
                "sessions": [
                    {
                        "user_id": 1,
                        "username": "admin001",
                        "tipo_usuario": "Administrador",
                        "login_time": "2024-01-15T08:00:00",
                        "last_activity": "2024-01-15T10:30:00",
                        "ip_address": "192.168.1.100"
                    }
                ],
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class LogoutResponse(BaseModel):
    """Schema para respuesta de logout"""
    success: bool
    message: str
    user_id: Optional[int] = None
    logout_time: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Sesión cerrada exitosamente",
                "user_id": 1,
                "logout_time": "2024-01-15T10:30:00"
            }
        }


# ===== SCHEMAS ADICIONALES =====

class LoginAttemptInfo(BaseModel):
    """Schema para información de intentos de login"""
    username: str
    attempts: int
    last_attempt: Optional[datetime] = None
    blocked_until: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "vet001",
                "attempts": 2,
                "last_attempt": "2024-01-15T10:25:00",
                "blocked_until": None
            }
        }


class AuthenticationStats(BaseModel):
    """Schema para estadísticas de autenticación"""
    successful_logins_today: int
    failed_logins_today: int
    active_sessions: int
    blocked_users: int
    success_rate: float

    class Config:
        schema_extra = {
            "example": {
                "successful_logins_today": 25,
                "failed_logins_today": 3,
                "active_sessions": 8,
                "blocked_users": 0,
                "success_rate": 89.3
            }
        }