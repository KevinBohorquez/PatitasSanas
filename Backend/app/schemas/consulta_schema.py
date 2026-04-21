# app/schemas/consulta_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from .base_schema import BaseResponse, PaginationResponse

# ===== SOLICITUD ATENCIÓN =====

class SolicitudAtencionCreate(BaseModel):
    """Schema para crear solicitud de atención"""
    id_mascota: int
    id_recepcionista: int
    tipo_solicitud: str  # 'Consulta urgente', 'Consulta normal', 'Servicio programado'
    fecha_hora_solicitud: Optional[datetime] = None
    
    @validator('tipo_solicitud')
    def validate_tipo_solicitud(cls, v):
        tipos_validos = ['Consulta urgente', 'Consulta normal', 'Servicio programado']
        if v not in tipos_validos:
            raise ValueError(f'Tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v


class SolicitudAtencionResponse(BaseResponse):
    """Schema para respuesta de solicitud"""
    id_solicitud: int
    id_mascota: int
    id_recepcionista: int
    fecha_hora_solicitud: Optional[datetime]
    tipo_solicitud: str
    estado: str


# ===== TRIAJE =====

class TriajeCreate(BaseModel):
    """Schema para crear triaje"""
    id_solicitud: int
    id_veterinario: int
    peso_mascota: float
    latido_por_minuto: int
    frecuencia_respiratoria_rpm: int
    temperatura: float
    frecuencia_pulso: int
    clasificacion_urgencia: str
    talla: Optional[float] = None
    tiempo_capilar: Optional[str] = None
    color_mucosas: Optional[str] = None
    porce_deshidratacion: Optional[float] = None
    condicion_corporal: str = "Ideal"
    fecha_hora_triaje: Optional[datetime] = None
    
    @validator('peso_mascota')
    def validate_peso(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Peso debe estar entre 0 y 100 kg')
        return v
    
    @validator('latido_por_minuto')
    def validate_latido(cls, v):
        if v < 40 or v > 300:
            raise ValueError('Latidos por minuto debe estar entre 40 y 300')
        return v
    
    @validator('temperatura')
    def validate_temperatura(cls, v):
        if v < 35.0 or v > 42.0:
            raise ValueError('Temperatura debe estar entre 35.0 y 42.0°C')
        return v


class TriajeResponse(BaseResponse):
    """Schema para respuesta de triaje"""
    id_triaje: int
    id_solicitud: int
    id_veterinario: int
    fecha_hora_triaje: datetime
    peso_mascota: float
    latido_por_minuto: int
    talla: float
    tiempo_capilar: str
    color_mucosas: str
    frecuencia_pulso: int
    porce_deshidratacion: float
    frecuencia_respiratoria_rpm: int
    temperatura: float
    clasificacion_urgencia: str
    condicion_corporal: str


# app/schemas/triaje_schemas.py - Agregar a tu archivo existente

class TriajeUpdate(BaseModel):
    """Schema para actualizar triaje"""
    id_veterinario: Optional[int] = None
    peso_mascota: Optional[float] = None
    latido_por_minuto: Optional[int] = None
    frecuencia_respiratoria_rpm: Optional[int] = None
    temperatura: Optional[float] = None
    frecuencia_pulso: Optional[int] = None
    clasificacion_urgencia: Optional[str] = None
    talla: Optional[float] = None
    tiempo_capilar: Optional[str] = None
    color_mucosas: Optional[str] = None
    porce_deshidratacion: Optional[float] = None
    condicion_corporal: Optional[str] = None

    @validator('peso_mascota')
    def validate_peso(cls, v):
        if v is not None and (v <= 0 or v > 100):
            raise ValueError('Peso debe estar entre 0 y 100 kg')
        return v

    @validator('latido_por_minuto')
    def validate_latido(cls, v):
        if v is not None and (v < 40 or v > 300):
            raise ValueError('Latidos por minuto debe estar entre 40 y 300')
        return v

    @validator('frecuencia_respiratoria_rpm')
    def validate_frecuencia_respiratoria(cls, v):
        if v is not None and (v < 10 or v > 150):
            raise ValueError('Frecuencia respiratoria debe estar entre 10 y 150')
        return v

    @validator('temperatura')
    def validate_temperatura(cls, v):
        if v is not None and (v < 35.0 or v > 42.0):
            raise ValueError('Temperatura debe estar entre 35.0 y 42.0°C')
        return v

    @validator('frecuencia_pulso')
    def validate_frecuencia_pulso(cls, v):
        if v is not None and (v < 30 or v > 250):
            raise ValueError('Frecuencia de pulso debe estar entre 30 y 250')
        return v

    @validator('talla')
    def validate_talla(cls, v):
        if v is not None and (v <= 0 or v > 200):
            raise ValueError('Talla debe estar entre 0 y 200 cm')
        return v

    @validator('porce_deshidratacion')
    def validate_porce_deshidratacion(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Porcentaje de deshidratación debe estar entre 0 y 100')
        return v

    @validator('tiempo_capilar')
    def validate_tiempo_capilar(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError('Tiempo capilar debe tener al menos 1 caracter')
        return v

    @validator('color_mucosas')
    def validate_color_mucosas(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError('Color de mucosas debe tener al menos 3 caracteres')
        return v

    @validator('condicion_corporal')
    def validate_condicion_corporal(cls, v):
        valid_conditions = ['Muy delgado', 'Delgado', 'Ideal', 'Sobrepeso', 'Obeso']
        if v is not None and v not in valid_conditions:
            raise ValueError(f'Condición corporal debe ser una de: {valid_conditions}')
        return v

    @validator('clasificacion_urgencia')
    def validate_clasificacion_urgencia(cls, v):
        valid_classifications = ['No urgente', 'Poco urgente', 'Urgente', 'Muy urgente', 'Critico']
        if v is not None and v not in valid_classifications:
            raise ValueError(f'Clasificación de urgencia debe ser una de: {valid_classifications}')
        return v

# ===== CONSULTA =====

class ConsultaCreate(BaseModel):
    """Schema para crear consulta"""
    id_triaje: int
    id_veterinario: int
    tipo_consulta: str
    motivo_consulta: Optional[str] = None
    sintomas_observados: Optional[str] = None
    diagnostico_preliminar: Optional[str] = None
    observaciones: Optional[str] = None
    condicion_general: str
    es_seguimiento: bool = False
    fecha_consulta: Optional[datetime] = None
    
    @validator('tipo_consulta')
    def validate_tipo_consulta(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Tipo de consulta debe tener al menos 5 caracteres')
        return v.strip()
    
    @validator('condicion_general')
    def validate_condicion_general(cls, v):
        condiciones = ['Excelente', 'Buena', 'Regular', 'Mala', 'Critica']
        if v not in condiciones:
            raise ValueError(f'Condición debe ser una de: {", ".join(condiciones)}')
        return v


class ConsultaResponse(BaseResponse):
    """Schema para respuesta de consulta"""
    id_consulta: int
    id_triaje: int
    id_veterinario: int
    tipo_consulta: str
    fecha_consulta: datetime
    motivo_consulta: Optional[str]
    condicion_general: str
    es_seguimiento: bool

class ConsultaUpdate(BaseModel):
    tipo_consulta: str
    motivo_consulta: Optional[str] = None
    sintomas_observados: Optional[str] = None
    diagnostico_preliminar: Optional[str] = None
    observaciones: Optional[str] = None
    condicion_general: str
    es_seguimiento: bool = False

# ===== DIAGNÓSTICO =====

class DiagnosticoCreate(BaseModel):
    """Schema para crear diagnóstico"""
    id_consulta: int
    id_patologia: int
    diagnostico: str
    tipo_diagnostico: str = "Presuntivo"
    estado_patologia: str = "Activa"
    fecha_diagnostico: Optional[datetime] = None
    
    @validator('diagnostico')
    def validate_diagnostico(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Diagnóstico debe tener al menos 5 caracteres')
        return v.strip()

class DiagnosticoUpdate(BaseModel):
    """Schema para actualizar diagnóstico"""
    id_consulta: Optional[int] = None
    id_patologia: Optional[int] = None
    diagnostico: Optional[str] = None
    tipo_diagnostico: Optional[str] = None
    estado_patologia: Optional[str] = None
    fecha_diagnostico: Optional[datetime] = None

class DiagnosticoResponse(BaseResponse):
    """Schema para respuesta de diagnóstico"""
    id_diagnostico: int
    id_consulta: int
    id_patologia: int
    tipo_diagnostico: str
    fecha_diagnostico: datetime
    estado_patologia: str
    diagnostico: str



# ===== TRATAMIENTO =====

class TratamientoCreate(BaseModel):
    """Schema para crear tratamiento"""
    id_consulta: int
    id_patologia: int
    tipo_tratamiento: str
    fecha_inicio: date
    eficacia_tratamiento: Optional[str] = None
    
    @validator('tipo_tratamiento')
    def validate_tipo_tratamiento(cls, v):
        tipos = ['Medicamentoso', 'Quirurgico', 'Terapeutico', 'Preventivo']
        if v not in tipos:
            raise ValueError(f'Tipo debe ser uno de: {", ".join(tipos)}')
        return v


class TratamientoResponse(BaseResponse):
    """Schema para respuesta de tratamiento"""
    id_tratamiento: int
    id_consulta: int
    id_patologia: int
    fecha_inicio: date
    eficacia_tratamiento: Optional[str]
    tipo_tratamiento: str


class TratamientoUpdate(BaseModel):
    """Schema para actualizar tratamiento"""
    id_consulta: Optional[int] = None
    id_patologia: Optional[int] = None
    tipo_tratamiento: Optional[str] = None
    fecha_inicio: Optional[date] = None
    eficacia_tratamiento: Optional[str] = None

    @validator('tipo_tratamiento')
    def validate_tipo_tratamiento(cls, v):
        if v is not None:
            tipos = ['Medicamentoso', 'Quirurgico', 'Terapeutico', 'Preventivo']
            if v not in tipos:
                raise ValueError(f'Tipo debe ser uno de: {", ".join(tipos)}')
        return v

# ===== CITA =====

class CitaCreate(BaseModel):
    """Schema para crear cita"""
    id_mascota: int
    fecha_hora_programada: datetime
    id_servicio_solicitado: Optional[int] = None
    requiere_ayuno: Optional[bool] = None
    observaciones: Optional[str] = None
    
    @validator('observaciones')
    def validate_observaciones(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('Observaciones debe tener al menos 3 caracteres')
        return v.strip() if v else v


class CitaUpdate(BaseModel):
    """Schema para actualizar cita"""
    fecha_hora_programada: Optional[datetime] = None
    estado_cita: Optional[str] = None
    requiere_ayuno: Optional[bool] = None
    observaciones: Optional[str] = None
    
    @validator('estado_cita')
    def validate_estado_cita(cls, v):
        if v and v not in ['Programada', 'Cancelada', 'Atendida']:
            raise ValueError('Estado debe ser Programada, Cancelada o Atendida')
        return v


class CitaResponse(BaseResponse):
    """Schema para respuesta de cita"""
    id_cita: int
    id_mascota: int
    id_servicio_solicitado: Optional[int]
    fecha_hora_programada: datetime
    estado_cita: str
    requiere_ayuno: Optional[bool]
    observaciones: Optional[str]


# ===== SERVICIO SOLICITADO =====

class ServicioSolicitadoCreate(BaseModel):
    """Schema para crear servicio solicitado"""
    id_consulta: int
    id_servicio: int
    prioridad: Optional[str] = "Normal"
    comentario_opcional: Optional[str] = None
    fecha_solicitado: Optional[datetime] = None
    
    @validator('prioridad')
    def validate_prioridad(cls, v):
        if v and v not in ['Urgente', 'Normal', 'Programable']:
            raise ValueError('Prioridad debe ser Urgente, Normal o Programable')
        return v


class ServicioSolicitadoResponse(BaseResponse):
    """Schema para respuesta de servicio solicitado"""
    id_servicio_solicitado: int
    id_consulta: int
    id_servicio: int
    fecha_solicitado: Optional[datetime]
    prioridad: Optional[str]
    estado_examen: str
    comentario_opcional: Optional[str]


class ServicioSolicitadoUpdate(BaseModel):
    """Schema para actualizar servicio solicitado"""
    id_consulta: Optional[int] = None
    id_servicio: Optional[int] = None
    prioridad: Optional[str] = None
    comentario_opcional: Optional[str] = None
    fecha_solicitado: Optional[datetime] = None
    estado_examen: Optional[str] = None

    @validator('prioridad')
    def validate_prioridad(cls, v):
        if v and v not in ['Urgente', 'Normal', 'Programable']:
            raise ValueError('Prioridad debe ser Urgente, Normal o Programable')
        return v


class ServicioCitaCreate(BaseModel):
    # Datos para Servicio_Solicitado
    id_veterinario: int
    id_servicio: int
    prioridad: str
    comentario_opcional: Optional[str] = None

    # Datos para Cita
    fecha_hora_programada: datetime
    requiere_ayuno: bool
    observaciones: Optional[str] = None

# ===== RESULTADO SERVICIO =====

class ResultadoServicioCreate(BaseModel):
    """Schema para crear resultado de servicio"""
    id_cita: int
    id_veterinario: int
    resultado: str
    interpretacion: Optional[str] = None
    archivo_adjunto: Optional[str] = None
    fecha_realizacion: Optional[datetime] = None
    
    @validator('resultado')
    def validate_resultado(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Resultado debe tener al menos 5 caracteres')
        return v.strip()


class ResultadoServicioResponse(BaseResponse):
    """Schema para respuesta de resultado de servicio"""
    id_resultado: int
    id_cita: int
    id_veterinario: int
    resultado: str
    interpretacion: Optional[str]
    archivo_adjunto: Optional[str]
    fecha_realizacion: datetime


class ResultadoServicioUpdate(BaseModel):
    """Schema para actualizar el resultado de servicio"""

    resultado: Optional[str] = None
    interpretacion: Optional[str] = None
    archivo_adjunto: Optional[str] = None
    fecha_realizacion: Optional[datetime] = None

    class Config:
        min_anystr_length = 3  # Si se aplica a otros campos de longitud mínima
        anystr_strip_whitespace = True  # Eliminar espacios al principio y final

    # Validador para el campo 'resultado'
    @classmethod
    def validate_resultado(cls, v: str) -> str:
        if len(v.strip()) < 5:
            raise ValueError('El resultado debe tener al menos 5 caracteres')
        return v.strip()

# ===== HISTORIAL CLÍNICO =====

class HistorialClinicoCreate(BaseModel):
    """Schema para crear historial clínico"""
    id_mascota: int
    tipo_evento: str
    descripcion_evento: str
    id_consulta: Optional[int] = None
    id_diagnostico: Optional[int] = None
    id_tratamiento: Optional[int] = None
    id_veterinario: Optional[int] = None
    edad_meses: Optional[int] = None
    peso_momento: Optional[float] = None
    observaciones: Optional[str] = None
    fecha_evento: Optional[datetime] = None
    
    @validator('tipo_evento')
    def validate_tipo_evento(cls, v):
        if len(v.strip()) < 4:
            raise ValueError('Tipo de evento debe tener al menos 4 caracteres')
        return v.strip()
    
    @validator('descripcion_evento')
    def validate_descripcion_evento(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Descripción debe tener al menos 5 caracteres')
        return v.strip()


class HistorialClinicoResponse(BaseResponse):
    """Schema para respuesta de historial clínico"""
    id_historial: int
    id_mascota: int
    fecha_evento: datetime
    tipo_evento: str
    descripcion_evento: str
    edad_meses: Optional[int]
    peso_momento: Optional[float]
    observaciones: Optional[str]


# ===== SCHEMAS DE BÚSQUEDA Y LISTADOS =====

class ConsultaSearch(BaseModel):
    """Schema para búsqueda de consultas"""
    id_mascota: Optional[int] = None
    id_veterinario: Optional[int] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    condicion_general: Optional[str] = None
    es_seguimiento: Optional[bool] = None
    page: int = 1
    per_page: int = 20


class CitaSearch(BaseModel):
    """Schema para búsqueda de citas"""
    id_mascota: Optional[int] = None
    id_servicio: Optional[int] = None
    estado_cita: Optional[str] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    page: int = 1
    per_page: int = 20


class HistorialSearch(BaseModel):
    """Schema para búsqueda de historial"""
    id_mascota: int
    tipo_evento: Optional[str] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    page: int = 1
    per_page: int = 20


class DiagnosticoCompletoUpdate(BaseModel):
    """Schema para actualizar todos los campos del formulario"""
    # Campos de DIAGNOSTICO
    tipo_diagnostico: Optional[str] = None
    diagnostico: Optional[str] = None
    estado_patologia: Optional[str] = None

    # Campos de PATOLOGIA
    nombre_patologia: Optional[str] = None
    especie_afecta: Optional[str] = None
    es_contagioso: Optional[bool] = None
    es_cronico: Optional[bool] = None
    gravedad_patologia: Optional[str] = None

    # Campos de TRATAMIENTO
    fecha_inicio: Optional[date] = None
    tipo_tratamiento: Optional[str] = None
    eficacia_tratamiento: Optional[str] = None

    @validator('diagnostico')
    def validate_diagnostico(cls, v):
        if v is not None and len(v.strip()) < 5:
            raise ValueError('Diagnóstico debe tener al menos 5 caracteres')
        return v.strip() if v else v

    @validator('tipo_diagnostico')
    def validate_tipo_diagnostico(cls, v):
        if v is not None and v not in ['Presuntivo', 'Confirmado', 'Descartado']:
            raise ValueError('Tipo diagnóstico debe ser Presuntivo o Confirmado')
        return v

    @validator('estado_patologia')
    def validate_estado_patologia(cls, v):
        if v is not None and v not in ['Activa', 'Controlada', 'Curada', 'En seguimiento']:
            raise ValueError('Estado patología debe ser Activa o Inactiva')
        return v

    @validator('nombre_patologia')
    def validate_nombre_patologia(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError('Nombre de patología debe tener al menos 3 caracteres')
        return v.strip().title() if v else v

    @validator('especie_afecta')
    def validate_especie_afecta(cls, v):
        if v is not None and v not in ['Perro', 'Gato', 'Ambas']:
            raise ValueError('Especie afecta debe ser Perro, Gato o Ambas')
        return v

    @validator('gravedad_patologia')
    def validate_gravedad_patologia(cls, v):
        if v is not None and v not in ['Leve', 'Moderada', 'Grave', 'Critica']:
            raise ValueError('Gravedad patología debe ser Leve, Moderada o Severa')
        return v

    @validator('tipo_tratamiento')
    def validate_tipo_tratamiento(cls, v):
        if v is not None and v not in ['Medicamentoso', 'Quirurgico', 'Terapeutico', 'Preventivo']:
            raise ValueError('Tipo tratamiento debe ser Medicamento, Cirugía o Terapia')
        return v

    @validator('eficacia_tratamiento')
    def validate_eficacia_tratamiento(cls, v):
        if v is not None and v not in ['Muy buena', 'Buena', 'Regular', 'Mala']:
            raise ValueError('Eficacia tratamiento debe ser Muy buena, Bueno, Regular o Malo')
        return v
