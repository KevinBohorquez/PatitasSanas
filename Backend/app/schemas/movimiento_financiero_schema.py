from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from .base_schema import BaseResponse


class MovimientoFinancieroCreate(BaseModel):
    tipo: str
    categoria: str
    monto: Decimal
    concepto: str
    fecha_movimiento: Optional[datetime] = None
    id_cita: Optional[int] = None
    id_administrador: Optional[int] = None

    @validator('tipo')
    def validate_tipo(cls, v):
        if v not in ('Ingreso', 'Egreso'):
            raise ValueError('Tipo debe ser Ingreso o Egreso')
        return v

    @validator('categoria')
    def validate_categoria(cls, v):
        if v not in ('Servicio', 'Operativo', 'Nomina'):
            raise ValueError('Categoria debe ser Servicio, Operativo o Nomina')
        return v

    @validator('monto')
    def validate_monto(cls, v):
        if v < 0:
            raise ValueError('Monto no puede ser negativo')
        return v

    @validator('concepto')
    def validate_concepto(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Concepto debe tener al menos 3 caracteres')
        return v.strip()


class MovimientoFinancieroUpdate(BaseModel):
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    monto: Optional[Decimal] = None
    concepto: Optional[str] = None
    id_administrador: Optional[int] = None


class MovimientoFinancieroResponse(BaseResponse):
    id_movimiento: int
    tipo: str
    categoria: str
    monto: Decimal
    concepto: str
    fecha_movimiento: datetime
    id_cita: Optional[int] = None
    id_administrador: Optional[int] = None
