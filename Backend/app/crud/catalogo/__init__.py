# app/crud/catalogo/__init__.py
"""Paquete CRUD de catálogos: un módulo por recurso. Re-exporta las instancias."""
from .raza import raza
from .tipo_animal import tipo_animal
from .especialidad import especialidad
from .tipo_servicio import tipo_servicio
from .servicio import servicio
from .patologia import patologia
from .cliente_mascota import cliente_mascota

__all__ = ["raza", "tipo_animal", "especialidad", "tipo_servicio", "servicio", "patologia", "cliente_mascota"]
