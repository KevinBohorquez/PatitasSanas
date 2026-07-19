# app/queries/cita_queries.py
"""
Consultas de lectura para Cita.

Ensamblados multi-tabla (cita + mascota + servicio + veterinario) que no son
persistencia de una sola entidad y por eso viven fuera del CRUD.
"""
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Cita, ResultadoServicio, ServicioSolicitado, Servicio, Veterinario, Mascota


def listar_enriquecidas(
    db: Session, *, page: int = 1, per_page: int = 10,
    search: Optional[str] = None, estado: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Lista de citas ya enriquecida (mascota, servicio y veterinario) resuelta en
    UNA sola consulta con JOINs, paginada y filtrada en el servidor. Devuelve
    (items, total) para que el endpoint arme el envelope.
    """
    nombre_vet = func.concat_ws(" ", Veterinario.nombre, Veterinario.apellido_paterno)

    query = (
        db.query(
            Cita,
            Mascota.nombre.label("nombre_mascota"),
            Servicio.nombre_servicio.label("nombre_servicio"),
            nombre_vet.label("nombre_veterinario"),
        )
        .join(Mascota, Mascota.id_mascota == Cita.id_mascota)
        .outerjoin(
            ServicioSolicitado,
            ServicioSolicitado.id_servicio_solicitado == Cita.id_servicio_solicitado,
        )
        .outerjoin(Servicio, Servicio.id_servicio == ServicioSolicitado.id_servicio)
        .outerjoin(Veterinario, Veterinario.id_veterinario == Cita.id_veterinario)
    )

    if estado:
        query = query.filter(Cita.estado_cita == estado)
    if search and search.strip():
        query = query.filter(Mascota.nombre.ilike(f"%{search.strip()}%"))

    total = query.count()

    # Orden: la cita más reciente (recién creada) primero. Cita no tiene timestamp de
    # creación, así que se usa id_cita desc como proxy — igual criterio "lo último
    # primero" que el listado de solicitudes.
    rows = (
        query.order_by(Cita.id_cita.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    citas = [
        {
            "id_cita": c.id_cita,
            "id_mascota": c.id_mascota,
            "id_servicio_solicitado": c.id_servicio_solicitado,
            "id_veterinario": c.id_veterinario,
            "fecha_hora_programada": c.fecha_hora_programada,
            "estado_cita": c.estado_cita,
            "requiere_ayuno": c.requiere_ayuno,
            "observaciones": c.observaciones,
            "nombre_mascota": nombre_mascota or "Desconocida",
            "nombre_servicio": nombre_servicio or "Sin servicio",
            "nombre_veterinario": (nombre_veterinario or "").strip() or "Sin asignar",
        }
        for c, nombre_mascota, nombre_servicio, nombre_veterinario in rows
    ]

    return citas, total


def get_con_servicio(db: Session, *, cita_id: int):
    """Cita con el nombre de su servicio (Cita -> ServicioSolicitado -> Servicio), o None."""
    return (
        db.query(Cita, Servicio.nombre_servicio)
        .join(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado)
        .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio)
        .filter(Cita.id_cita == cita_id)
        .first()
    )


def get_con_veterinario(db: Session, *, cita_id: int):
    """Cita con servicio y veterinario (vía Resultado_servicio), o None."""
    return (
        db.query(
            Cita.id_cita,
            Cita.fecha_hora_programada,
            Cita.estado_cita,
            Servicio.nombre_servicio,
            Veterinario.nombre.label("veterinario_nombre"),
            Veterinario.apellido_paterno.label("veterinario_apellido"),
        )
        .join(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado)
        .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio)
        .join(ResultadoServicio, ResultadoServicio.id_cita == Cita.id_cita)
        .join(Veterinario, ResultadoServicio.id_veterinario == Veterinario.id_veterinario)
        .filter(Cita.id_cita == cita_id)
        .first()
    )


def get_con_mascota(db: Session, *, cita_id: int):
    """Cita con el nombre de su mascota (Cita -> Mascota), o None."""
    return (
        db.query(Cita.id_cita, Mascota.nombre)
        .join(Mascota, Cita.id_mascota == Mascota.id_mascota)
        .filter(Cita.id_cita == cita_id)
        .first()
    )
