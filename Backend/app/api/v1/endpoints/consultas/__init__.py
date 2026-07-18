# app/api/v1/endpoints/consultas/__init__.py
"""Router agregador de consultas por dominio.
Orden de inclusión IMPORTANTE: 'citas' antes que 'consultas' para que las
rutas específicas (/cita, /search) precedan al comodín GET /{consulta_id}."""
from fastapi import APIRouter

from . import citas
from . import consultas
from . import diagnosticos
from . import tratamientos
from . import historial
from . import resultados

router = APIRouter()
router.include_router(citas.router)
router.include_router(consultas.router)
router.include_router(diagnosticos.router)
router.include_router(tratamientos.router)
router.include_router(historial.router)
router.include_router(resultados.router)
