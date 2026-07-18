# app/crud/consulta/__init__.py
"""Paquete CRUD de procesos clínicos: un módulo por dominio. Re-exporta instancias."""
from .solicitud_atencion import solicitud_atencion
from .triaje import triaje
from .consulta import consulta
from .diagnostico import diagnostico
from .tratamiento import tratamiento
from .cita import cita
from .servicio_solicitado import servicio_solicitado
from .resultado_servicio import resultado_servicio
from .historial_clinico import historial_clinico

__all__ = ["solicitud_atencion", "triaje", "consulta", "diagnostico", "tratamiento", "cita", "servicio_solicitado", "resultado_servicio", "historial_clinico"]
