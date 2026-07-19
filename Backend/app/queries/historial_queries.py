# app/queries/historial_queries.py
"""
Consultas de lectura para el historial clínico.

Ensamblados multi-tabla (historial + veterinario, consultas por la cadena
Consulta -> Triaje -> Solicitud_atencion -> Mascota, diagnósticos + patología) que
no son persistencia de una sola entidad y por eso viven fuera del CRUD.
"""
from typing import List, Optional, Tuple
from datetime import datetime, date

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Veterinario, HistorialClinico, Diagnostico, Patologia
from app.models.consulta import Consulta
from app.models.triaje import Triaje
from app.models.solicitud_atencion import SolicitudAtencion


def listar_historial(
    db: Session, *, mascota_id: int,
    fecha_desde: Optional[date] = None, fecha_hasta: Optional[date] = None,
    limit: int = 50,
) -> List[Tuple[HistorialClinico, Veterinario]]:
    """Eventos de historial de una mascota con su veterinario responsable."""
    query = db.query(HistorialClinico, Veterinario) \
        .outerjoin(Veterinario, HistorialClinico.id_veterinario == Veterinario.id_veterinario) \
        .filter(HistorialClinico.id_mascota == mascota_id)

    if fecha_desde:
        query = query.filter(HistorialClinico.fecha_evento >= fecha_desde)
    if fecha_hasta:
        # Incluir todos los eventos del día 'fecha_hasta' (hasta las 23:59:59)
        fecha_hasta_completa = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(HistorialClinico.fecha_evento <= fecha_hasta_completa)

    return query.order_by(desc(HistorialClinico.fecha_evento)).limit(limit).all()


def listar_consultas(db: Session, *, mascota_id: int, limit: int = 50) -> List[Consulta]:
    """
    Consultas de una mascota por la cadena
    Consulta -> Triaje -> Solicitud_atencion -> Mascota.
    """
    return (
        db.query(Consulta)
        .join(Triaje, Triaje.id_triaje == Consulta.id_triaje)
        .join(SolicitudAtencion, SolicitudAtencion.id_solicitud == Triaje.id_solicitud)
        .filter(SolicitudAtencion.id_mascota == mascota_id)
        .order_by(Consulta.fecha_consulta.desc())
        .limit(limit)
        .all()
    )


def listar_consultas_con_veterinario(
    db: Session, *, mascota_id: int, limit: int = 50
) -> List[Tuple[Consulta, Veterinario]]:
    """Consultas de una mascota (misma cadena) con su veterinario."""
    return (
        db.query(Consulta, Veterinario)
        .join(Triaje, Triaje.id_triaje == Consulta.id_triaje)
        .join(SolicitudAtencion, SolicitudAtencion.id_solicitud == Triaje.id_solicitud)
        .outerjoin(Veterinario, Veterinario.id_veterinario == Consulta.id_veterinario)
        .filter(SolicitudAtencion.id_mascota == mascota_id)
        .order_by(Consulta.fecha_consulta.desc())
        .limit(limit)
        .all()
    )


def get_evento_historial_consulta(db: Session, *, consulta_id: int) -> Optional[HistorialClinico]:
    """Evento de historial (peso/edad/observaciones) registrado para una consulta."""
    return (
        db.query(HistorialClinico)
        .filter(HistorialClinico.id_consulta == consulta_id)
        .order_by(HistorialClinico.fecha_evento)
        .first()
    )


def listar_diagnosticos_consulta(
    db: Session, *, consulta_id: int
) -> List[Tuple[Diagnostico, Patologia]]:
    """Diagnósticos de una consulta con su patología asociada."""
    return (
        db.query(Diagnostico, Patologia)
        .outerjoin(Patologia, Patologia.id_patologia == Diagnostico.id_patologia)
        .filter(Diagnostico.id_consulta == consulta_id)
        .order_by(Diagnostico.fecha_diagnostico)
        .all()
    )
