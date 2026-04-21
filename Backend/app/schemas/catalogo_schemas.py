# app/schemas/catalogo_schemas.py
from pydantic import BaseModel, validator
from typing import Optional
from .base_schema import BaseResponse

# ===== RAZA =====

class RazaCreate(BaseModel):
    """Schema para crear una raza"""
    nombre_raza: str
    
    @validator('nombre_raza')
    def validate_nombre_raza(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Nombre de raza debe tener al menos 2 caracteres')
        return v.strip().title()


class RazaResponse(BaseResponse):
    """Schema para devolver información de raza"""
    id_raza: int
    nombre_raza: str


# ===== TIPO ANIMAL =====

class TipoAnimalCreate(BaseModel):
    """Schema para crear un tipo de animal"""
    id_raza: int
    descripcion: str  # 'Perro' o 'Gato'
    
    @validator('descripcion')
    def validate_descripcion(cls, v):
        if v not in ['Perro', 'Gato']:
            raise ValueError('Descripción debe ser Perro o Gato')
        return v


class TipoAnimalResponse(BaseResponse):
    """Schema para devolver información de tipo animal"""
    id_tipo_animal: int
    id_raza: int
    descripcion: str


# ===== ESPECIALIDAD =====

class EspecialidadCreate(BaseModel):
    """Schema para crear una especialidad"""
    descripcion: str
    
    @validator('descripcion')
    def validate_descripcion(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Descripción debe tener al menos 3 caracteres')
        return v.strip().title()


class EspecialidadResponse(BaseResponse):
    """Schema para devolver información de especialidad"""
    id_especialidad: int
    descripcion: str


# ===== TIPO SERVICIO =====

class TipoServicioCreate(BaseModel):
    """Schema para crear un tipo de servicio"""
    descripcion: str
    
    @validator('descripcion')
    def validate_descripcion(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Descripción debe tener al menos 3 caracteres')
        return v.strip().title()


class TipoServicioResponse(BaseResponse):
    """Schema para devolver información de tipo servicio"""
    id_tipo_servicio: int
    descripcion: str


# ===== SERVICIO =====

class ServicioCreate(BaseModel):
    """Schema para crear un servicio"""
    id_tipo_servicio: int
    nombre_servicio: str
    precio: float
    activo: bool = True
    
    @validator('nombre_servicio')
    def validate_nombre_servicio(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Nombre del servicio debe tener al menos 3 caracteres')
        return v.strip().title()
    
    @validator('precio')
    def validate_precio(cls, v):
        if v < 0 or v > 9999.99:
            raise ValueError('Precio debe estar entre 0 y 9999.99')
        return round(v, 2)


class ServicioUpdate(BaseModel):
    """Schema para actualizar un servicio"""
    id_tipo_servicio: Optional[int] = None
    nombre_servicio: Optional[str] = None
    precio: Optional[float] = None
    activo: Optional[bool] = None


class ServicioResponse(BaseResponse):
    """Schema para devolver información de servicio"""
    id_servicio: int
    id_tipo_servicio: int
    nombre_servicio: str
    precio: float
    activo: bool


class ServicioWithTipoResponse(ServicioResponse):
    """Schema para servicio con tipo de servicio"""
    tipo_servicio_descripcion: Optional[str] = None


# ===== PATOLOGÍA =====

class PatologiaCreate(BaseModel):
    """Schema para crear una patología"""
    nombre_patologia: str
    especie_afecta: str  # 'Perro', 'Gato', 'Ambas'
    gravedad: str = "Moderada"  # 'Leve', 'Moderada', 'Grave', 'Critica'
    es_crónica: Optional[bool] = None
    es_contagiosa: Optional[bool] = None
    
    @validator('nombre_patologia')
    def validate_nombre_patologia(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Nombre de patologia debe tener al menos 3 caracteres')
        return v.strip().title()
    
    @validator('especie_afecta')
    def validate_especie_afecta(cls, v):
        if v not in ['Perro', 'Gato', 'Ambas']:
            raise ValueError('Especie afecta debe ser Perro, Gato o Ambas')
        return v
    
    @validator('gravedad')
    def validate_gravedad(cls, v):
        if v not in ['Leve', 'Moderada', 'Grave', 'Critica']:
            raise ValueError('Gravedad debe ser Leve, Moderada, Grave o Critica')
        return v


class PatologiaResponse(BaseResponse):
    """Schema para devolver información de patología"""
    id_patologia: int
    nombre_patologia: str
    especie_afecta: str
    gravedad: str
    es_crónica: Optional[bool]
    es_contagiosa: Optional[bool]


class PatologiaUpdate(BaseModel):
    """Schema para actualizar patología"""
    nombre_patologia: Optional[str] = None
    especie_afecta: Optional[str] = None
    gravedad: Optional[str] = None
    es_cronica: Optional[bool] = None
    es_contagiosa: Optional[bool] = None

    @validator('nombre_patologia')
    def validate_nombre_patologia(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError('Nombre de patologia debe tener al menos 3 caracteres')
        return v.strip().title() if v else v

    @validator('especie_afecta')
    def validate_especie_afecta(cls, v):
        if v is not None and v not in ['Perro', 'Gato', 'Ambas']:
            raise ValueError('Especie afecta debe ser Perro, Gato o Ambas')
        return v

    @validator('gravedad')
    def validate_gravedad(cls, v):
        if v is not None and v not in ['Leve', 'Moderada', 'Grave', 'Critica']:
            raise ValueError('Gravedad debe ser Leve, Moderada, Grave o Critica')
        return v

# ===== CLIENTE_MASCOTA =====

class ClienteMascotaCreate(BaseModel):
    """Schema para crear relación cliente-mascota"""
    id_cliente: int
    id_mascota: int

    @validator('id_cliente')
    def validate_id_cliente(cls, v):
        if v <= 0:
            raise ValueError('ID del cliente debe ser mayor a 0')
        return v

    @validator('id_mascota')
    def validate_id_mascota(cls, v):
        if v <= 0:
            raise ValueError('ID de la mascota debe ser mayor a 0')
        return v


class ClienteMascotaResponse(BaseResponse):
    """Schema para devolver información de relación cliente-mascota"""
    id_cliente_mascota: int
    id_cliente: int
    id_mascota: int