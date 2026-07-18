# app/queries/reportes_queries.py
"""
Consultas de lectura para los reportes PDF.

Ensamblados multi-tabla que alimentan los PDF de citas e historial clínico. No son
persistencia de una sola entidad y por eso viven fuera del CRUD; el endpoint sólo
da forma a los datos para el generador de PDF.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import (
    Cita, Mascota, Cliente, ClienteMascota, ServicioSolicitado, Consulta,
    Veterinario, Usuario, HistorialClinico, Raza, Diagnostico,
)


def listar_citas_reporte(
    db: Session, *, inicio_dt: Optional[datetime] = None, fin_dt: Optional[datetime] = None
) -> List[tuple]:
    """Citas con mascota, cliente y veterinario para el reporte PDF de citas."""
    query = db.query(Cita, Mascota, Cliente, Veterinario, Usuario).select_from(Cita) \
        .outerjoin(Mascota, Cita.id_mascota == Mascota.id_mascota) \
        .outerjoin(ClienteMascota, Mascota.id_mascota == ClienteMascota.id_mascota) \
        .outerjoin(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente) \
        .outerjoin(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
        .outerjoin(Consulta, ServicioSolicitado.id_consulta == Consulta.id_consulta) \
        .outerjoin(Veterinario, Consulta.id_veterinario == Veterinario.id_veterinario) \
        .outerjoin(Usuario, Veterinario.id_usuario == Usuario.id_usuario)

    if inicio_dt:
        query = query.filter(Cita.fecha_hora_programada >= inicio_dt)
    if fin_dt:
        query = query.filter(Cita.fecha_hora_programada <= fin_dt)

    return query.order_by(Cita.fecha_hora_programada.asc()).all()


def get_mascota_reporte(db: Session, *, mascota_id: int) -> Optional[Tuple[Mascota, Raza, Cliente]]:
    """Mascota con su raza y cliente principal para la cabecera del PDF de historial."""
    return (
        db.query(Mascota, Raza, Cliente).select_from(Mascota)
        .outerjoin(Raza, Mascota.id_raza == Raza.id_raza)
        .outerjoin(ClienteMascota, Mascota.id_mascota == ClienteMascota.id_mascota)
        .outerjoin(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente)
        .filter(Mascota.id_mascota == mascota_id)
        .first()
    )


def listar_historial_reporte(
    db: Session, *, mascota_id: int,
    inicio_dt: Optional[datetime] = None, fin_dt: Optional[datetime] = None
) -> List[tuple]:
    """Eventos de historial con consulta, diagnóstico y veterinario para el PDF."""
    query = db.query(HistorialClinico, Consulta, Diagnostico, Veterinario, Usuario).select_from(HistorialClinico) \
        .outerjoin(Consulta, HistorialClinico.id_consulta == Consulta.id_consulta) \
        .outerjoin(Diagnostico, HistorialClinico.id_diagnostico == Diagnostico.id_diagnostico) \
        .outerjoin(Veterinario, HistorialClinico.id_veterinario == Veterinario.id_veterinario) \
        .outerjoin(Usuario, Veterinario.id_usuario == Usuario.id_usuario) \
        .filter(HistorialClinico.id_mascota == mascota_id)

    if inicio_dt:
        query = query.filter(HistorialClinico.fecha_evento >= inicio_dt)
    if fin_dt:
        query = query.filter(HistorialClinico.fecha_evento <= fin_dt)

    return query.order_by(HistorialClinico.fecha_evento.desc()).all()
