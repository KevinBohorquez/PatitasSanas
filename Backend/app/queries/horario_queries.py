# app/queries/horario_queries.py
"""
Consultas de lectura para los horarios.

Ensamblados que resuelven el nombre, especialidad y estado (Activo/Inactivo) de un
conjunto de veterinarios/recepcionistas para mostrarlos en el cronograma. Son
JOINs multi-tabla, no persistencia de una sola entidad, por eso viven fuera del CRUD.
"""
from sqlalchemy.orm import Session

from app.models.veterinario import Veterinario
from app.models.especialidad import Especialidad
from app.models.recepcionista import Recepcionista
from app.models.usuario import Usuario


def info_veterinarios(db: Session, ids) -> dict:
    """Nombre, especialidad y estado (Activo/Inactivo) de un conjunto de veterinarios."""
    if not ids:
        return {}
    rows = db.query(Veterinario, Especialidad.descripcion, Usuario.estado) \
        .outerjoin(Especialidad, Especialidad.id_especialidad == Veterinario.id_especialidad) \
        .outerjoin(Usuario, Usuario.id_usuario == Veterinario.id_usuario) \
        .filter(Veterinario.id_veterinario.in_(ids)).all()
    return {
        v.id_veterinario: {
            "nombre": f"{v.nombre} {v.apellido_paterno}".strip(),
            "especialidad": esp,
            "estado": est,
        }
        for v, esp, est in rows
    }


def info_recepcionistas(db: Session, ids) -> dict:
    """Nombre y estado (Activo/Inactivo) de un conjunto de recepcionistas."""
    if not ids:
        return {}
    rows = db.query(Recepcionista, Usuario.estado) \
        .outerjoin(Usuario, Usuario.id_usuario == Recepcionista.id_usuario) \
        .filter(Recepcionista.id_recepcionista.in_(ids)).all()
    return {
        r.id_recepcionista: {
            "nombre": f"{r.nombre} {r.apellido_paterno}".strip(),
            "estado": est,
        }
        for r, est in rows
    }
