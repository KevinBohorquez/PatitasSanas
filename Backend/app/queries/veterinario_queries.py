# app/queries/veterinario_queries.py
"""
Consultas de lectura para el veterinario.

Proyecciones multi-entidad (resultados+citas, dashboard con próxima cita,
pendientes, solicitudes asignadas y últimas atenciones) que ensamblan varias
tablas y no son persistencia de una sola entidad, por eso viven fuera del CRUD.
"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import ResultadoServicio, Cita, Mascota, ServicioSolicitado, Servicio
from app.models.veterinario import Veterinario
from app.models.especialidad import Especialidad
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje


def get_resultados_citas(db: Session, *, id_veterinario: int) -> List[dict]:
    """Resultados de servicio (con su cita) realizados por un veterinario."""
    resultados = (
        db.query(ResultadoServicio)
        .join(Cita, ResultadoServicio.id_cita == Cita.id_cita)
        .filter(ResultadoServicio.id_veterinario == id_veterinario)
        .options(joinedload(ResultadoServicio.cita))
        .all()
    )

    return [
        {
            "id_resultado": r.id_resultado,
            "resultado": r.resultado,
            "interpretacion": r.interpretacion,
            "archivo_adjunto": r.archivo_adjunto,
            "fecha_realizacion": r.fecha_realizacion,
            "cita": {
                "id_cita": r.cita.id_cita,
                "fecha_hora_programada": r.cita.fecha_hora_programada,
                "estado_cita": r.cita.estado_cita,
                "requiere_ayuno": r.cita.requiere_ayuno,
                "observaciones": r.cita.observaciones,
            },
        }
        for r in resultados
    ]


def get_citas_programadas(db: Session, *, id_veterinario: int) -> List[dict]:
    """Citas PROGRAMADAS asignadas al veterinario (por Cita.id_veterinario)."""
    citas = (
        db.query(Cita)
        .filter(
            Cita.id_veterinario == id_veterinario,
            Cita.estado_cita == "Programada",
        )
        .order_by(Cita.fecha_hora_programada.asc())
        .all()
    )

    # Mismo envoltorio { "cita": {...} } que /resultados-citas para reutilizar el
    # render del frontend (que pide mascota/servicio/veterinario por id_cita).
    return [
        {
            "cita": {
                "id_cita": c.id_cita,
                "fecha_hora_programada": c.fecha_hora_programada,
                "estado_cita": c.estado_cita,
                "requiere_ayuno": c.requiere_ayuno,
                "observaciones": c.observaciones,
            }
        }
        for c in citas
    ]


def get_dashboard(db: Session, *, id_usuario: int) -> Optional[dict]:
    """
    Resumen del panel de inicio del veterinario: perfil, próxima cita, número de
    citas pendientes, solicitudes asignadas y últimas atenciones. Devuelve None si
    el veterinario no existe.
    """
    vet = (
        db.query(Veterinario, Especialidad.descripcion)
        .outerjoin(Especialidad, Especialidad.id_especialidad == Veterinario.id_especialidad)
        .filter(Veterinario.id_usuario == id_usuario)
        .first()
    )
    if not vet:
        return None
    vet_obj, especialidad_desc = vet
    vet_id = vet_obj.id_veterinario

    # Próxima cita programada del veterinario (con mascota y servicio).
    prox = (
        db.query(Cita, Mascota.nombre, Servicio.nombre_servicio)
        .outerjoin(Mascota, Mascota.id_mascota == Cita.id_mascota)
        .outerjoin(ServicioSolicitado, ServicioSolicitado.id_servicio_solicitado == Cita.id_servicio_solicitado)
        .outerjoin(Servicio, Servicio.id_servicio == ServicioSolicitado.id_servicio)
        .filter(Cita.id_veterinario == vet_id, Cita.estado_cita == "Programada")
        .order_by(Cita.fecha_hora_programada.asc())
        .first()
    )
    proxima_cita = None
    if prox:
        c, masc_nombre, serv_nombre = prox
        proxima_cita = {
            "id_cita": c.id_cita,
            "fecha_hora_programada": c.fecha_hora_programada,
            "mascota": masc_nombre,
            "servicio": serv_nombre,
            "requiere_ayuno": c.requiere_ayuno,
        }

    # Pendientes de atender: citas programadas asignadas al veterinario.
    pendientes = (
        db.query(func.count(Cita.id_cita))
        .filter(Cita.id_veterinario == vet_id, Cita.estado_cita == "Programada")
        .scalar()
    )

    # Solicitudes asignadas: las de los triajes que hizo el veterinario.
    triaje_solicitud_ids = [
        row[0] for row in db.query(Triaje.id_solicitud).filter(Triaje.id_veterinario == vet_id).all()
    ]
    # Solo las que aún no han sido atendidas (excluye Completada y Cancelada).
    estados_no_atendidos = ["Pendiente", "En triaje", "En atencion"]
    solicitudes_items = []
    total_solicitudes = 0
    if triaje_solicitud_ids:
        total_solicitudes = (
            db.query(func.count(SolicitudAtencion.id_solicitud))
            .filter(
                SolicitudAtencion.id_solicitud.in_(triaje_solicitud_ids),
                SolicitudAtencion.estado.in_(estados_no_atendidos),
            )
            .scalar()
        )
        filas = (
            db.query(SolicitudAtencion, Mascota.nombre)
            .outerjoin(Mascota, Mascota.id_mascota == SolicitudAtencion.id_mascota)
            .filter(
                SolicitudAtencion.id_solicitud.in_(triaje_solicitud_ids),
                SolicitudAtencion.estado.in_(estados_no_atendidos),
            )
            .order_by(SolicitudAtencion.fecha_hora_solicitud.desc())
            .limit(8)
            .all()
        )
        solicitudes_items = [
            {
                "id_solicitud": s.id_solicitud,
                "mascota": masc,
                "tipo_solicitud": s.tipo_solicitud,
                "estado": s.estado,
                "fecha": s.fecha_hora_solicitud,
            }
            for s, masc in filas
        ]

    # Últimas atenciones: citas ya atendidas por el veterinario.
    atendidas = (
        db.query(Cita, Mascota.nombre, Servicio.nombre_servicio)
        .outerjoin(Mascota, Mascota.id_mascota == Cita.id_mascota)
        .outerjoin(ServicioSolicitado, ServicioSolicitado.id_servicio_solicitado == Cita.id_servicio_solicitado)
        .outerjoin(Servicio, Servicio.id_servicio == ServicioSolicitado.id_servicio)
        .filter(Cita.id_veterinario == vet_id, Cita.estado_cita == "Atendida")
        .order_by(Cita.fecha_hora_programada.desc())
        .limit(5)
        .all()
    )
    ultimas_atenciones = [
        {
            "id_cita": c.id_cita,
            "fecha": c.fecha_hora_programada,
            "mascota": masc,
            "servicio": serv,
        }
        for c, masc, serv in atendidas
    ]

    return {
        "veterinario": {
            "nombre": f"{vet_obj.nombre} {vet_obj.apellido_paterno}".strip(),
            "especialidad": especialidad_desc,
            "turno": vet_obj.turno,
            "disposicion": vet_obj.disposicion,
        },
        "proxima_cita": proxima_cita,
        "pendientes_atender": pendientes or 0,
        "solicitudes_asignadas": {
            "total": total_solicitudes or 0,
            "items": solicitudes_items,
        },
        "ultimas_atenciones": ultimas_atenciones,
    }
