# app/schemas/mascota_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from .base_schema import BaseResponse, PaginationResponse, validate_name


# ===== SCHEMAS DE INPUT (REQUEST) =====

class MascotaCreate(BaseModel):
    """Schema para crear una mascota"""
    id_raza: int
    nombre: str
    sexo: str  # 'Macho' o 'Hembra'
    color: Optional[str] = None
    edad_anios: Optional[int] = None
    edad_meses: Optional[int] = None
    esterilizado: bool = False
    imagen: Optional[str] = None

    # Validators
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)

    @validator('sexo')
    def validate_sexo(cls, v):
        if v not in ['Macho', 'Hembra']:
            raise ValueError('Sexo debe ser Macho o Hembra')
        return v

    @validator('edad_anios')
    def validate_edad_anios(cls, v):
        if v is not None and (v < 0 or v > 25):
            raise ValueError('Edad en años debe estar entre 0 y 25')
        return v

    @validator('edad_meses')
    def validate_edad_meses(cls, v):
        if v is not None and (v < 0 or v > 11):
            raise ValueError('Edad en meses debe estar entre 0 y 11')
        return v

    @validator('color')
    def validate_color(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('Color debe tener al menos 3 caracteres')
        return v.strip().title() if v else v


class MascotaUpdate(BaseModel):
    """Schema para actualizar una mascota"""
    id_raza: Optional[int] = None
    nombre: Optional[str] = None
    sexo: Optional[str] = None
    color: Optional[str] = None
    edad_anios: Optional[int] = None
    edad_meses: Optional[int] = None
    esterilizado: Optional[bool] = None
    imagen: Optional[str] = None

    # Mismo validators que Create
    _validate_nombre = validator('nombre', allow_reuse=True)(validate_name)

    @validator('sexo')
    def validate_sexo(cls, v):
        if v and v not in ['Macho', 'Hembra']:
            raise ValueError('Sexo debe ser Macho o Hembra')
        return v


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class MascotaResponse(BaseResponse):
    """Schema para devolver información de mascota"""
    id_mascota: int
    id_raza: int
    nombre: str
    sexo: str
    color: Optional[str]
    edad_anios: Optional[int]
    edad_meses: Optional[int]
    esterilizado: bool
    imagen: Optional[str]


class MascotaListResponse(PaginationResponse):
    """Schema para lista de mascotas"""
    mascotas: list[MascotaResponse]


# ===== SCHEMAS DE BÚSQUEDA =====

class MascotaSearch(BaseModel):
    """Schema para búsqueda de mascotas"""
    nombre: Optional[str] = None
    id_raza: Optional[int] = None
    sexo: Optional[str] = None
    esterilizado: Optional[bool] = None
    page: int = 1
    per_page: int = 20


# ===== SCHEMAS ADICIONALES PARA RELACIONES =====

class MascotaClienteCreate(BaseModel):
    """Schema para crear relación mascota-cliente"""
    id_mascota: int
    id_cliente: int


class MascotaWithClienteResponse(MascotaResponse):
    """Schema para mascota con información del cliente asociado"""
    cliente: Optional[dict] = None

    class Config:
        from_attributes = True


class MascotaWithRazaResponse(MascotaResponse):
    """Schema para mascota con información de la raza"""
    raza: Optional[dict] = None

    class Config:
        from_attributes = True


class MascotaCompleteResponse(MascotaResponse):
    """Schema para mascota con toda la información relacionada"""
    cliente: Optional[dict] = None
    raza: Optional[dict] = None

    class Config:
        from_attributes = True