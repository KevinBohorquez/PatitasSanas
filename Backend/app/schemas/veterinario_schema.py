# app/schemas/veterinario_schema.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date
from .base_schema import BaseResponse, PaginationResponse, validate_dni, validate_telefono, validate_name


# ===== SCHEMAS DE INPUT (REQUEST) =====

class VeterinarioCreate(BaseModel):
    """Schema para crear un veterinario"""
    id_usuario: int  # ← AGREGADO: ID del usuario ya creado
    id_especialidad: int
    codigo_CMVP: str
    tipo_veterinario: str  # 'Medico General' o 'Especializado'
    fecha_nacimiento: date
    genero: str  # 'F' o 'M'
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: EmailStr  # Para validar que coincida con el usuario
    fecha_ingreso: date
    turno: str  # 'Mañana', 'Tarde', 'Noche'
    disposicion: str = "Libre"

    # Validators
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)
    _validate_apellido_paterno = validator('apellido_paterno', allow_reuse=True)(validate_name)
    _validate_apellido_materno = validator('apellido_materno', allow_reuse=True)(validate_name)
    _validate_dni = validator('dni', allow_reuse=True)(validate_dni)
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)

    @validator('codigo_CMVP')
    def validate_codigo_cmvp(cls, v):
        if len(v.strip()) < 6:
            raise ValueError('Código CMVP debe tener al menos 6 caracteres')
        return v.strip()

    @validator('tipo_veterinario')
    def validate_tipo_veterinario(cls, v):
        if v not in ['Medico General', 'Especializado']:
            raise ValueError('Tipo debe ser Medico General o Especializado')
        return v

    @validator('genero')
    def validate_genero(cls, v):
        if v not in ['F', 'M']:
            raise ValueError('Género debe ser F o M')
        return v

    @validator('turno')
    def validate_turno(cls, v):
        if v not in ['Mañana', 'Tarde', 'Noche']:
            raise ValueError('Turno debe ser Mañana, Tarde o Noche')
        return v

    @validator('disposicion')
    def validate_disposicion(cls, v):
        if v not in ['Libre', 'Ocupado', 'Fuera de turno']:
            raise ValueError('Disposición debe ser Libre u Ocupado u Fuera de turno')
        return v


class VeterinarioUpdate(BaseModel):
    """Schema para actualizar un veterinario"""
    id_especialidad: Optional[int] = None
    codigo_CMVP: Optional[str] = None
    tipo_veterinario: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    disposicion: Optional[str] = None
    turno: Optional[str] = None

    # Validators para campos opcionales
    _validate_telefono = validator('telefono', allow_reuse=True)(validate_telefono)

    @validator('codigo_CMVP')
    def validate_codigo_cmvp(cls, v):
        if v and len(v.strip()) < 6:
            raise ValueError('Código CMVP debe tener al menos 6 caracteres')
        return v.strip() if v else v

    @validator('tipo_veterinario')
    def validate_tipo_veterinario(cls, v):
        if v and v not in ['Medico General', 'Especializado']:
            raise ValueError('Tipo debe ser Medico General o Especializado')
        return v

    @validator('turno')
    def validate_turno(cls, v):
        if v and v not in ['Mañana', 'Tarde', 'Noche']:
            raise ValueError('Turno debe ser Mañana, Tarde o Noche')
        return v

    @validator('disposicion')
    def validate_disposicion(cls, v):
        if v and v not in ['Libre', 'Ocupado']:
            raise ValueError('Disposición debe ser Libre u Ocupado')
        return v


class VeterinarioLogin(BaseModel):
    """Schema para login de veterinario"""
    email: EmailStr
    contraseña: str


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class VeterinarioResponse(BaseResponse):
    """Schema para devolver información de veterinario"""
    id_veterinario: int
    id_usuario: int  # ← AGREGADO: Para mostrar la relación
    id_especialidad: int
    codigo_CMVP: str
    tipo_veterinario: str
    fecha_nacimiento: date
    genero: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: str
    fecha_ingreso: date
    disposicion: str
    turno: str
    # Nota: NO incluimos contraseña por seguridad


class VeterinarioWithEspecialidadResponse(VeterinarioResponse):
    """Schema para veterinario con detalles de especialidad"""
    especialidad_descripcion: Optional[str] = None


class VeterinarioWithUserResponse(VeterinarioResponse):
    """Schema para veterinario con información del usuario"""
    usuario_estado: Optional[str] = None  # Estado del usuario asociado
    usuario_tipo: Optional[str] = None  # Tipo del usuario asociado


class VeterinarioListResponse(PaginationResponse):
    """Schema para lista de veterinarios"""
    veterinarios: list[VeterinarioResponse]


# ===== SCHEMAS DE BÚSQUEDA =====

class VeterinarioSearch(BaseModel):
    """Schema para búsqueda de veterinarios"""
    nombre: Optional[str] = None
    dni: Optional[str] = None
    id_especialidad: Optional[int] = None
    tipo_veterinario: Optional[str] = None
    disposicion: Optional[str] = None
    turno: Optional[str] = None
    id_usuario: Optional[int] = None  # ← AGREGADO: Para buscar por usuario
    page: int = 1
    per_page: int = 20