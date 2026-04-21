# app/crud/__init__.py (VERSIÓN COMPLETA)

# CRUD Base
from .base_crud import CRUDBase

# CRUD de Usuarios y Autenticación
from .usuario_crud import usuario
from .administrador_crud import administrador
from .auth_crud import auth

# CRUD Principales
from .clientes_crud import cliente
from .mascota_crud import mascota
from .veterinario_crud import veterinario
from .recepcionista_crud import recepcionista

# CRUD Catálogos (Usando los completos)
from .catalogo_crud import (
    raza, tipo_animal, especialidad, 
    tipo_servicio, servicio, patologia, cliente_mascota
)

# CRUD Procesos Clínicos
from .consulta_crud import (
    solicitud_atencion, triaje, consulta,
    diagnostico, tratamiento, cita, servicio_solicitado,
    resultado_servicio, historial_clinico
)

# CRUD Dashboard
from .dashboard_crud import dashboard

__all__ = [
    # Base
    "CRUDBase",
    
    # Usuarios y Autenticación
    "usuario",
    "administrador", 
    "auth",
    
    # Principales
    "cliente",
    "mascota", 
    "veterinario",
    "recepcionista",
    
    # Catálogos
    "raza",
    "tipo_animal",
    "especialidad",
    "tipo_servicio",
    "servicio",
    "patologia",
    "cliente_mascota",
    
    # Procesos Clínicos
    "solicitud_atencion",
    "triaje",
    "consulta",
    "diagnostico",
    "tratamiento",
    "cita",
    "servicio_solicitado",
    "resultado_servicio",
    "historial_clinico",

    
    # Otros
    "dashboard"
]