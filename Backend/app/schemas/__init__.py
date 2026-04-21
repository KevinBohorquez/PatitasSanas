# app/schemas/__init__.py

# Schemas base
from .base_schema import BaseResponse, PaginationResponse, MessageResponse
# Nota: ErrorResponse no existe en base_schema, lo removemos o lo agregamos

# Schemas principales
from .clientes_schema import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    ClienteListResponse, ClienteSearch
)

from .mascota_schema import (
    MascotaCreate, MascotaUpdate, MascotaResponse,
    MascotaSearch, MascotaClienteCreate, MascotaWithClienteResponse,
    MascotaWithRazaResponse, MascotaCompleteResponse
)

from .veterinario_schema import (
    VeterinarioCreate, VeterinarioUpdate,
    VeterinarioResponse, VeterinarioWithEspecialidadResponse,
    VeterinarioListResponse, VeterinarioSearch
)

from .recepcionista_schema import (
    RecepcionistaCreate, RecepcionistaUpdate,
    RecepcionistaResponse, RecepcionistaListResponse, RecepcionistaSearch
)

# Schemas de catálogos
from .catalogo_schemas import (
    RazaCreate, RazaResponse,
    TipoAnimalCreate, TipoAnimalResponse,
    EspecialidadCreate, EspecialidadResponse,
    TipoServicioCreate, TipoServicioResponse,
    ServicioCreate, ServicioUpdate, ServicioResponse, ServicioWithTipoResponse,
    PatologiaCreate, PatologiaResponse
)

# Schemas de procesos clínicos
from .consulta_schema import (
    # Solicitud y Triaje
    SolicitudAtencionCreate, SolicitudAtencionResponse,
    TriajeCreate, TriajeResponse,

    # Consulta y Diagnóstico
    ConsultaCreate, ConsultaResponse,
    DiagnosticoCreate, DiagnosticoResponse,
    TratamientoCreate, TratamientoResponse,

    # Servicios y Citas
    ServicioSolicitadoCreate, ServicioSolicitadoResponse,
    CitaCreate, CitaUpdate, CitaResponse,
    ResultadoServicioCreate, ResultadoServicioResponse,

    # Historial
    HistorialClinicoCreate, HistorialClinicoResponse,

    # Búsquedas
    ConsultaSearch, CitaSearch, HistorialSearch
)

__all__ = [
    # Base
    "BaseResponse", "PaginationResponse", "MessageResponse",

    # Cliente
    "ClienteCreate", "ClienteUpdate", "ClienteResponse",
    "ClienteListResponse", "ClienteSearch",

    # Mascota (CORREGIDO - usando los nombres que SÍ importas)
    "MascotaCreate", "MascotaUpdate", "MascotaResponse",
    "MascotaSearch", "MascotaClienteCreate", "MascotaWithClienteResponse",
    "MascotaWithRazaResponse", "MascotaCompleteResponse",

    # Veterinario
    "VeterinarioCreate", "VeterinarioUpdate",
    "VeterinarioResponse", "VeterinarioWithEspecialidadResponse",
    "VeterinarioListResponse", "VeterinarioSearch",

    # Recepcionista
    "RecepcionistaCreate", "RecepcionistaUpdate",
    "RecepcionistaResponse", "RecepcionistaListResponse", "RecepcionistaSearch",

    # Catálogos
    "RazaCreate", "RazaResponse",
    "TipoAnimalCreate", "TipoAnimalResponse",
    "EspecialidadCreate", "EspecialidadResponse",
    "TipoServicioCreate", "TipoServicioResponse",
    "ServicioCreate", "ServicioUpdate", "ServicioResponse", "ServicioWithTipoResponse",
    "PatologiaCreate", "PatologiaResponse",

    # Procesos clínicos
    "SolicitudAtencionCreate", "SolicitudAtencionResponse",
    "TriajeCreate", "TriajeResponse",
    "ConsultaCreate", "ConsultaResponse",
    "DiagnosticoCreate", "DiagnosticoResponse",
    "TratamientoCreate", "TratamientoResponse",
    "ServicioSolicitadoCreate", "ServicioSolicitadoResponse",
    "CitaCreate", "CitaUpdate", "CitaResponse",
    "ResultadoServicioCreate", "ResultadoServicioResponse",
    "HistorialClinicoCreate", "HistorialClinicoResponse",

    # Búsquedas
    "ConsultaSearch", "CitaSearch", "HistorialSearch"
]