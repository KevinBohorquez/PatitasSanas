# app/queries/veterinario_queries.py
"""
Consultas de lectura para el veterinario.

Proyecciones multi-entidad (resultados+citas, dashboard con próxima cita,
pendientes, solicitudes asignadas y últimas atenciones) que ensamblan varias
tablas y no son persistencia de una sola entidad, por eso viven fuera del CRUD.
"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import ResultadoServicio, Cita, Mascota, ServicioSolicitado, Servicio
from app.models.veterinario import Veterinario
from app.models.especialidad import Especialidad
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje


# Nombre del veterinario asociado a una cita, resuelto por Resultado_servicio (igual
# que el endpoint /consultas/citaVeterinario). concat_ws ignora los NULL.
_nombre_vet = func.concat_ws(" ", Veterinario.nombre, Veterinario.apellido_paterno)


def get_resultados_citas(db: Session, *, id_veterinario: int) -> List[dict]:
    """
    Resultados de servicio (con su cita) realizados por un veterinario, YA
    enriquecidos con nombre de mascota, servicio y veterinario en una sola consulta
    (reemplaza el N+1 del front: citaMascota/citaServicio/citaVeterinario por fila).
    """
    rows = (
        db.query(
            ResultadoServicio.id_resultado,
            ResultadoServicio.resultado,
            ResultadoServicio.interpretacion,
            ResultadoServicio.archivo_adjunto,
            ResultadoServicio.fecha_realizacion,
            Cita.id_cita,
            Cita.fecha_hora_programada,
            Cita.estado_cita,
            Cita.requiere_ayuno,
            Cita.observaciones,
            Mascota.nombre.label("nombre_mascota"),
            Servicio.nombre_servicio.label("nombre_servicio"),
            _nombre_vet.label("nombre_veterinario"),
        )
        .join(Cita, ResultadoServicio.id_cita == Cita.id_cita)
        .filter(ResultadoServicio.id_veterinario == id_veterinario)
        .outerjoin(Mascota, Mascota.id_mascota == Cita.id_mascota)
        .outerjoin(ServicioSolicitado, ServicioSolicitado.id_servicio_solicitado == Cita.id_servicio_solicitado)
        .outerjoin(Servicio, Servicio.id_servicio == ServicioSolicitado.id_servicio)
        .outerjoin(Veterinario, Veterinario.id_veterinario == ResultadoServicio.id_veterinario)
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
                "id_cita": r.id_cita,
                "fecha_hora_programada": r.fecha_hora_programada,
                "estado_cita": r.estado_cita,
                "requiere_ayuno": r.requiere_ayuno,
                "observaciones": r.observaciones,
            },
            "nombre_mascota": r.nombre_mascota,
            "nombre_servicio": r.nombre_servicio,
            "nombre_veterinario": r.nombre_veterinario,
        }
        for r in rows
    ]


def get_citas_programadas(db: Session, *, id_veterinario: int) -> List[dict]:
    """
    Citas PROGRAMADAS asignadas al veterinario (por Cita.id_veterinario), YA
    enriquecidas con nombre de mascota, servicio y veterinario en una sola consulta
    (reemplaza el N+1 del front: citaMascota/citaServicio/citaVeterinario por fila).
    El veterinario se resuelve por Resultado_servicio, igual que /consultas/citaVeterinario.
    """
    rows = (
        db.query(
            Cita.id_cita,
            Cita.fecha_hora_programada,
            Cita.estado_cita,
            Cita.requiere_ayuno,
            Cita.observaciones,
            Mascota.nombre.label("nombre_mascota"),
            Servicio.nombre_servicio.label("nombre_servicio"),
            _nombre_vet.label("nombre_veterinario"),
        )
        .filter(
            Cita.id_veterinario == id_veterinario,
            Cita.estado_cita == "Programada",
        )
        .outerjoin(Mascota, Mascota.id_mascota == Cita.id_mascota)
        .outerjoin(ServicioSolicitado, ServicioSolicitado.id_servicio_solicitado == Cita.id_servicio_solicitado)
        .outerjoin(Servicio, Servicio.id_servicio == ServicioSolicitado.id_servicio)
        .outerjoin(ResultadoServicio, ResultadoServicio.id_cita == Cita.id_cita)
        .outerjoin(Veterinario, Veterinario.id_veterinario == ResultadoServicio.id_veterinario)
        .order_by(Cita.fecha_hora_programada.asc())
        .all()
    )

    # Mismo envoltorio { "cita": {...} } + nombres, para el render del frontend.
    return [
        {
            "cita": {
                "id_cita": r.id_cita,
                "fecha_hora_programada": r.fecha_hora_programada,
                "estado_cita": r.estado_cita,
                "requiere_ayuno": r.requiere_ayuno,
                "observaciones": r.observaciones,
            },
            "nombre_mascota": r.nombre_mascota,
            "nombre_servicio": r.nombre_servicio,
            "nombre_veterinario": r.nombre_veterinario,
        }
        for r in rows
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
