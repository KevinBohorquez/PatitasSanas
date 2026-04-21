# app/models/solicitud_atencion.py
from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, ForeignKey
from app.models.base import Base


class SolicitudAtencion(Base):
    __tablename__ = "Solicitud_atencion"

    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))
    id_recepcionista = Column(Integer, ForeignKey('Recepcionista.id_recepcionista'))
    fecha_hora_solicitud = Column(DateTime)
    tipo_solicitud = Column(SQLEnum(
        'Consulta urgente', 
        'Consulta normal', 
        'Servicio programado', 
        name='tipo_solicitud_enum'
    ), nullable=False)
    estado = Column(SQLEnum(
        'Pendiente', 
        'En triaje', 
        'En atencion', 
        'Completada', 
        'Cancelada', 
        name='estado_solicitud_enum'
    ), default='Pendiente')