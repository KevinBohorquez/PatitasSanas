# app/models/__init__.py
from app.models.base import Base

# Modelos de usuarios y autenticación
from app.models.usuario import Usuario
from app.models.administrador import Administrador

# Modelos principales
from app.models.clientes import Cliente
from app.models.mascota import Mascota
from app.models.veterinario import Veterinario
from app.models.recepcionista import Recepcionista

# Modelos de catálogos
from app.models.raza import Raza
from app.models.tipo_animal import TipoAnimal
from app.models.especialidad import Especialidad
from app.models.tipo_servicio import TipoServicio
from app.models.servicio import Servicio
from app.models.patologia import Patologia

# Modelos de procesos
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje
from app.models.consulta import Consulta
from app.models.servicio_solicitado import ServicioSolicitado
from app.models.cita import Cita
from app.models.resultado_servicio import ResultadoServicio
from app.models.diagnostico import Diagnostico
from app.models.tratamiento import Tratamiento
from app.models.historial_clinico import HistorialClinico

# Modelos de relación
from app.models.cliente_mascota import ClienteMascota

# Exportar todos los modelos para fácil importación
__all__ = [
    "Base",
    # Usuarios y autenticación
    "Usuario",
    "Administrador",
    # Principales
    "Cliente",
    "Mascota",
    "Veterinario",
    "Recepcionista",
    # Catálogos
    "Raza",
    "TipoAnimal",
    "Especialidad",
    "TipoServicio",
    "Servicio",
    "Patologia",
    # Procesos
    "SolicitudAtencion",
    "Triaje",
    "Consulta",
    "ServicioSolicitado",
    "Cita",
    "ResultadoServicio",
    "Diagnostico",
    "Tratamiento",
    "HistorialClinico",
    # Relaciones
    "ClienteMascota"
]