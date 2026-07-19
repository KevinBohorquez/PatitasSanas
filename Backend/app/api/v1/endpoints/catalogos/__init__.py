# app/api/v1/endpoints/catalogos/__init__.py
"""Router agregador de catálogos: un módulo por recurso."""
from fastapi import APIRouter

from . import razas
from . import tipos_animal
from . import especialidades
from . import tipos_servicio
from . import servicios
from . import patologias
from . import cliente_mascota
from . import general

router = APIRouter()
router.include_router(razas.router)
router.include_router(tipos_animal.router)
router.include_router(especialidades.router)
router.include_router(tipos_servicio.router)
router.include_router(servicios.router)
router.include_router(patologias.router)
router.include_router(cliente_mascota.router)
router.include_router(general.router)
