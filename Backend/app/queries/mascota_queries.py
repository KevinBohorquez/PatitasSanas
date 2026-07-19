# app/queries/mascota_queries.py
"""
Consultas de lectura para Mascota.

Ensamblados multi-tabla (mascota + cliente + raza/especie + citas/atenciones) que
no son persistencia de una sola entidad y por eso viven fuera del CRUD.
"""
from typing import List, Optional, Tuple
from datetime import datetime

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models import (
    SolicitudAtencion, Recepcionista, Cita, Servicio, ServicioSolicitado, TipoAnimal, Raza,
)
from app.models.mascota import Mascota
from app.models.cliente_mascota import ClienteMascota
from app.models.clientes import Cliente


def listar_con_cliente_especie(
    db: Session, *, page: int = 1, per_page: int = 20,
    sexo: Optional[str] = None, id_raza: Optional[int] = None,
) -> Tuple[List[dict], int]:
    """Mascotas paginadas, enriquecidas con su cliente principal y su especie."""
    skip = (page - 1) * per_page

    query = db.query(Mascota)
    if sexo:
        query = query.filter(Mascota.sexo == sexo)
    if id_raza:
        query = query.filter(Mascota.id_raza == id_raza)

    total = query.count()
    mascotas = query.offset(skip).limit(per_page).all()

    result = []
    for mascota in mascotas:
        # Buscar cliente asociado
        cliente_info = None
        cliente_mascota = db.query(ClienteMascota).filter(
            ClienteMascota.id_mascota == mascota.id_mascota
        ).first()

        if cliente_mascota:
            cliente = db.query(Cliente).filter(
                Cliente.id_cliente == cliente_mascota.id_cliente
            ).first()
            if cliente:
                cliente_info = {
                    "id_cliente": cliente.id_cliente,
                    "nombre": f"{cliente.nombre} {cliente.apellido_paterno}"
                }

        # Obtener especie desde Tipo_animal
        especie = None
        tipo_animal = db.query(TipoAnimal).filter(
            TipoAnimal.id_raza == mascota.id_raza
        ).first()
        if tipo_animal:
            especie = tipo_animal.descripcion

        result.append({
            "id_mascota": mascota.id_mascota,
            "nombre": mascota.nombre,
            "sexo": mascota.sexo,
            "color": mascota.color,
            "edad_anios": mascota.edad_anios,
            "edad_meses": mascota.edad_meses,
            "esterilizado": mascota.esterilizado,
            "imagen": mascota.imagen,
            "id_raza": mascota.id_raza,
            "especie": especie,
            "cliente": cliente_info
        })

    return result, total


def listar_enriquecidas(
    db: Session, *, page: int = 1, per_page: int = 20
) -> Tuple[List[dict], int]:
    """
    Mascotas paginadas con especie, raza, próxima cita y última atención resueltas en
    UNA sola consulta con JOINs/subconsultas. Reemplaza el patrón N+1 del frontend
    (1 + N*3 peticiones: /info, /proxima-cita y /ultima-atencion por mascota) en el
    listado del veterinario. Devuelve (items, total).
    """
    now = datetime.now()

    # Próxima cita por mascota: la fecha programada futura más cercana.
    pc = (
        db.query(
            Cita.id_mascota.label("id_mascota"),
            func.min(Cita.fecha_hora_programada).label("proxima_cita"),
        )
        .filter(Cita.estado_cita == "Programada", Cita.fecha_hora_programada > now)
        .group_by(Cita.id_mascota)
        .subquery()
    )

    # Última atención por mascota: la solicitud real (completada/en atención) más reciente.
    ua = (
        db.query(
            SolicitudAtencion.id_mascota.label("id_mascota"),
            func.max(SolicitudAtencion.fecha_hora_solicitud).label("ultima_atencion"),
        )
        .filter(SolicitudAtencion.estado.in_(["Completada", "En atencion"]))
        .group_by(SolicitudAtencion.id_mascota)
        .subquery()
    )

    query = (
        db.query(
            Mascota.id_mascota,
            Mascota.nombre,
            Mascota.sexo,
            Mascota.color,
            TipoAnimal.descripcion.label("especie"),
            Raza.nombre_raza.label("raza"),
            pc.c.proxima_cita,
            ua.c.ultima_atencion,
        )
        .outerjoin(Raza, Raza.id_raza == Mascota.id_raza)
        .outerjoin(TipoAnimal, TipoAnimal.id_raza == Mascota.id_raza)
        .outerjoin(pc, pc.c.id_mascota == Mascota.id_mascota)
        .outerjoin(ua, ua.c.id_mascota == Mascota.id_mascota)
        .order_by(Mascota.id_mascota)
    )

    total = db.query(func.count(Mascota.id_mascota)).scalar()

    rows = query.offset((page - 1) * per_page).limit(per_page).all()

    items = [
        {
            "id_mascota": r.id_mascota,
            "nombre": r.nombre,
            "sexo": r.sexo,
            "color": r.color,
            "especie": r.especie,
            "raza": r.raza,
            "proxima_cita": r.proxima_cita,
            "ultima_atencion": r.ultima_atencion,
        }
        for r in rows
    ]

    return items, total


def get_cliente_y_raza(db: Session, *, mascota_id: int, id_raza: int) -> dict:
    """Cliente principal y datos de raza de una mascota (para el detalle)."""
    cliente_info = None
    cliente_mascota = db.query(ClienteMascota).filter(
        ClienteMascota.id_mascota == mascota_id
    ).first()

    if cliente_mascota:
        cliente = db.query(Cliente).filter(
            Cliente.id_cliente == cliente_mascota.id_cliente
        ).first()
        if cliente:
            cliente_info = {
                "id_cliente": cliente.id_cliente,
                "nombre": cliente.nombre,
                "apellidos": f"{cliente.apellido_paterno} {cliente.apellido_materno}",
                "telefono": cliente.telefono,
                "email": cliente.email
            }

    raza_info = None
    try:
        raza_result = db.execute(
            "SELECT nombre_raza, especie FROM Raza WHERE id_raza = :id_raza",
            {"id_raza": id_raza}
        ).fetchone()
        if raza_result:
            raza_info = {
                "nombre_raza": raza_result.nombre_raza,
                "especie": raza_result.especie
            }
    except Exception:
        pass

    return {"cliente": cliente_info, "raza": raza_info}


def get_info(db: Session, *, mascota_id: int):
    """Fila con datos de mascota + raza + especie (JOIN), o None si no existe."""
    from app.models import Raza
    return (
        db.query(
            Mascota.id_mascota,
            Mascota.nombre,
            Raza.nombre_raza.label('raza'),
            TipoAnimal.descripcion.label('especie'),
            Mascota.sexo.label('genero'),
            Mascota.color,
            Mascota.edad_anios,
            Mascota.edad_meses,
            Mascota.esterilizado,
            Mascota.imagen
        )
        .join(Raza, Mascota.id_raza == Raza.id_raza)
        .join(TipoAnimal, Raza.id_raza == TipoAnimal.id_raza)
        .filter(Mascota.id_mascota == mascota_id)
        .first()
    )


def get_proxima_cita(db: Session, *, mascota_id: int):
    """Próxima cita programada (fecha futura más cercana) de una mascota, o None."""
    return (
        db.query(
            Cita.id_cita,
            Cita.fecha_hora_programada,
            Cita.estado_cita,
            Servicio.nombre_servicio
        )
        .join(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado)
        .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio)
        .filter(
            Cita.id_mascota == mascota_id,
            Cita.estado_cita == 'Programada',
            Cita.fecha_hora_programada > datetime.now()
        )
        .order_by(Cita.fecha_hora_programada.asc())
        .first()
    )


def get_ultima_atencion(db: Session, *, mascota_id: int):
    """Última solicitud de atención real (completada/en atención) de una mascota, o None."""
    return (
        db.query(
            SolicitudAtencion.id_solicitud,
            SolicitudAtencion.fecha_hora_solicitud,
            SolicitudAtencion.tipo_solicitud,
            SolicitudAtencion.estado,
            func.concat(
                Recepcionista.nombre, ' ',
                Recepcionista.apellido_paterno
            ).label('recepcionista')
        )
        .join(Recepcionista, SolicitudAtencion.id_recepcionista == Recepcionista.id_recepcionista)
        .filter(
            SolicitudAtencion.id_mascota == mascota_id,
            SolicitudAtencion.estado.in_(['Completada', 'En atencion'])
        )
        .order_by(SolicitudAtencion.fecha_hora_solicitud.desc())
        .first()
    )


def get_id_mascota_de_consulta(db: Session, *, consulta_id: int) -> Optional[int]:
    """
    id_mascota asociado a una consulta, resuelto por la cadena
    Consulta -> Triaje -> Solicitud_atencion. Devuelve None si no se encuentra.
    """
    row = db.execute(
        text("""
        SELECT sa.id_mascota
        FROM Consulta c
        JOIN Triaje t ON c.id_triaje = t.id_triaje
        JOIN Solicitud_atencion sa ON t.id_solicitud = sa.id_solicitud
        WHERE c.id_consulta = :consulta_id
        """),
        {"consulta_id": consulta_id}
    ).fetchone()
    return row[0] if row else None


def get_cliente_servicio(db: Session, *, id_mascota: int) -> List[dict]:
    """Mascota con su cliente y servicios solicitados (4 tablas en JOIN)."""
    result = (
        db.query(Mascota, Cliente, Servicio, ServicioSolicitado)
        .join(ClienteMascota, Mascota.id_mascota == ClienteMascota.id_mascota)
        .join(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente)
        .join(ServicioSolicitado, ServicioSolicitado.id_servicio_solicitado == Mascota.id_mascota)
        .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio)
        .filter(Mascota.id_mascota == id_mascota)
        .all()
    )

    return [
        {
            "id_mascota": m.id_mascota,
            "nombre_mascota": m.nombre,
            "id_cliente": c.id_cliente,
            "nombre_cliente": f"{c.nombre} {c.apellido_paterno} {c.apellido_materno}",
            "id_servicio_solicitado": ss.id_servicio_solicitado if ss else None,
            "nombre_servicio": s.nombre_servicio if s else None,
            "id_servicio": s.id_servicio if s else None,
        }
        for m, c, s, ss in result
    ]
