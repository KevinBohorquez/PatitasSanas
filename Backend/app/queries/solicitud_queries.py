# app/queries/solicitud_queries.py
"""
Consultas de lectura para Solicitud_atencion.

A diferencia del CRUD (acceso a una sola entidad), aquí viven los ensamblados
multi-tabla: JOINs, subconsultas y proyecciones para la vista. No son
persistencia de un recurso sino consultas de lectura optimizadas que sirven a un
endpoint concreto, por eso se separan de las clases CRUD.
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, or_, not_

from app.models import Triaje, Veterinario, SolicitudAtencion
from app.models.mascota import Mascota
from app.models.cliente_mascota import ClienteMascota
from app.models.clientes import Cliente


def listar_enriquecidas(
    db: Session,
    *,
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    estado: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Lista de solicitudes ya enriquecida (mascota, dueño y veterinario) resuelta
    en UNA sola consulta con JOINs, paginada y filtrada en el servidor.

    Reemplaza el patrón N+1 del frontend (1 + N*3 peticiones HTTP) por una única
    respuesta. Devuelve (items, total) para que el endpoint arme el envelope.
    """
    # Un cliente "principal" por mascota: el de menor id_cliente. Replica el
    # clientes[0] que tomaba el frontend y evita que el JOIN multiplique filas
    # cuando una mascota tiene varios clientes asociados.
    pc = (
        db.query(
            ClienteMascota.id_mascota.label("id_mascota"),
            func.min(ClienteMascota.id_cliente).label("id_cliente"),
        )
        .group_by(ClienteMascota.id_mascota)
        .subquery()
    )

    # El triaje más antiguo por solicitud, para resolver un único veterinario
    # asignado (la asignación vive en Triaje, no en la solicitud).
    pt = (
        db.query(
            Triaje.id_solicitud.label("id_solicitud"),
            func.min(Triaje.id_triaje).label("id_triaje"),
        )
        .group_by(Triaje.id_solicitud)
        .subquery()
    )
    triaje_vet = aliased(Triaje)

    # concat_ws ignora los NULL (a diferencia de CONCAT, que devolvería NULL si
    # falta el apellido materno).
    nombre_duenio = func.concat_ws(
        " ", Cliente.nombre, Cliente.apellido_paterno, Cliente.apellido_materno
    )
    nombre_vet = func.concat_ws(" ", Veterinario.nombre, Veterinario.apellido_paterno)

    query = (
        db.query(
            SolicitudAtencion,
            Mascota.nombre.label("nombre_mascota"),
            nombre_duenio.label("nombre_dueno"),
            nombre_vet.label("nombre_veterinario"),
        )
        .join(Mascota, Mascota.id_mascota == SolicitudAtencion.id_mascota)
        .outerjoin(pc, pc.c.id_mascota == SolicitudAtencion.id_mascota)
        .outerjoin(Cliente, Cliente.id_cliente == pc.c.id_cliente)
        .outerjoin(pt, pt.c.id_solicitud == SolicitudAtencion.id_solicitud)
        .outerjoin(triaje_vet, triaje_vet.id_triaje == pt.c.id_triaje)
        .outerjoin(Veterinario, Veterinario.id_veterinario == triaje_vet.id_veterinario)
    )

    if estado:
        query = query.filter(SolicitudAtencion.estado == estado)

    if search and search.strip():
        like = f"%{search.strip()}%"
        query = query.filter(or_(Mascota.nombre.ilike(like), nombre_duenio.ilike(like)))

    total = query.count()

    rows = (
        query.order_by(SolicitudAtencion.fecha_hora_solicitud.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    solicitudes = [
        {
            "id_solicitud": s.id_solicitud,
            "id_mascota": s.id_mascota,
            "id_recepcionista": s.id_recepcionista,
            "fecha_hora_solicitud": s.fecha_hora_solicitud,
            "tipo_solicitud": s.tipo_solicitud,
            "estado": s.estado,
            "nombre_mascota": nombre_mascota or "Desconocida",
            "nombre_dueño": (nombre_dueno or "").strip() or "Sin dueño asignado",
            "nombre_veterinario": (nombre_veterinario or "").strip() or "Sin asignar",
        }
        for s, nombre_mascota, nombre_dueno, nombre_veterinario in rows
    ]

    return solicitudes, total


def get_veterinario_asignado(db: Session, *, solicitud_id: int) -> Optional[Veterinario]:
    """
    Veterinario asignado a una solicitud, resuelto por la cadena
    Solicitud -> Triaje -> Veterinario (la asignación la crea el trigger en el
    Triaje, no en la solicitud). Devuelve None si no hay ninguno asignado.
    """
    return (
        db.query(Veterinario)
        .join(Triaje, Triaje.id_veterinario == Veterinario.id_veterinario)
        .filter(Triaje.id_solicitud == solicitud_id)
        .first()
    )


def listar_por_veterinario(
    db: Session,
    *,
    id_veterinario: int,
    estado: Optional[str] = None,
    tipo_solicitud: Optional[str] = None,
    limit: int = 50,
) -> List[dict]:
    """
    Solicitudes visibles para un veterinario: las asignadas por triaje MÁS las
    pendientes sin triaje (que el trigger no pudo asignar y de otro modo serían
    invisibles para todos). Cada una ya enriquecida con nombre de mascota y del
    cliente principal (elimina el N+1 del front: /mascotas/{id}/details + /clientes/{id}).
    """
    # Solicitudes asignadas a este veterinario vía triaje.
    triajes = db.query(Triaje).filter(Triaje.id_veterinario == id_veterinario).all()
    solicitud_ids = [triaje.id_solicitud for triaje in triajes]

    # Solicitudes sin triaje (no asignadas por el trigger). Si el trigger no
    # encontró un veterinario disponible, la solicitud queda sin triaje y sería
    # invisible; se incluyen aquí para que el veterinario pueda verlas.
    solicitudes_sin_triaje_ids = db.query(SolicitudAtencion.id_solicitud).filter(
        not_(SolicitudAtencion.id_solicitud.in_(
            db.query(Triaje.id_solicitud)
        )),
        SolicitudAtencion.estado == 'Pendiente'
    ).all()
    solicitud_ids_sin_triaje = [s.id_solicitud for s in solicitudes_sin_triaje_ids]

    # Unir ambos conjuntos (triaje del vet + sin triaje).
    solicitud_ids = list(set(solicitud_ids) | set(solicitud_ids_sin_triaje))
    if not solicitud_ids:
        return []

    # Cliente "principal" por mascota (menor id_cliente), igual criterio que /enriquecidas.
    pc = (
        db.query(
            ClienteMascota.id_mascota.label("id_mascota"),
            func.min(ClienteMascota.id_cliente).label("id_cliente"),
        )
        .group_by(ClienteMascota.id_mascota)
        .subquery()
    )
    nombre_cliente = func.concat_ws(
        " ", Cliente.nombre, Cliente.apellido_paterno, Cliente.apellido_materno
    )

    query = (
        db.query(
            SolicitudAtencion,
            Mascota.nombre.label("nombre_mascota"),
            nombre_cliente.label("nombre_cliente"),
        )
        .filter(SolicitudAtencion.id_solicitud.in_(solicitud_ids))
        .outerjoin(Mascota, Mascota.id_mascota == SolicitudAtencion.id_mascota)
        .outerjoin(pc, pc.c.id_mascota == SolicitudAtencion.id_mascota)
        .outerjoin(Cliente, Cliente.id_cliente == pc.c.id_cliente)
    )

    if estado:
        query = query.filter(SolicitudAtencion.estado == estado)
    if tipo_solicitud:
        query = query.filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud)

    # Las más recientes primero: con muchas solicitudes asignadas, el límite ya no
    # oculta las recién creadas (antes, sin ORDER BY, el límite cortaba por id
    # ascendente y el veterinario no veía sus solicitudes nuevas).
    rows = query.order_by(
        SolicitudAtencion.fecha_hora_solicitud.desc(),
        SolicitudAtencion.id_solicitud.desc(),
    ).limit(limit).all()

    return [
        {
            "id_solicitud": s.id_solicitud,
            "id_mascota": s.id_mascota,
            "id_recepcionista": s.id_recepcionista,
            "fecha_hora_solicitud": s.fecha_hora_solicitud,
            "tipo_solicitud": s.tipo_solicitud,
            "estado": s.estado,
            "nombre_mascota": nombre_mascota,
            "nombre_cliente": nombre_cli,
        }
        for s, nombre_mascota, nombre_cli in rows
    ]
