# app/schemas/base_schema.py (CORREGIDO)
from pydantic import BaseModel, validator
from typing import Optional, Any


class BaseResponse(BaseModel):
    """Schema base para respuestas"""

    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    """Schema base para respuestas paginadas"""
    total: int
    page: int
    per_page: int
    total_pages: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema para mensajes de respuesta"""
    message: str
    success: bool = True


# ===== VALIDADORES REUTILIZABLES =====

def validate_name(name: str) -> str:
    """Validador reutilizable para nombres"""
    if not name or len(name.strip()) < 2:
        raise ValueError('El nombre debe tener al menos 2 caracteres')
    return name.strip().title()


def validate_dni(dni: str) -> str:
    """Validador para DNI peruano"""
    if len(dni) != 8 or not dni.isdigit():
        raise ValueError('DNI debe tener exactamente 8 dígitos numéricos')
    return dni


def validate_telefono(telefono: str) -> str:
    """Validador para teléfono peruano"""
    if len(telefono) != 9 or not telefono.startswith('9') or not telefono.isdigit():
        raise ValueError('Teléfono debe tener 9 dígitos y empezar con 9')
    return telefono