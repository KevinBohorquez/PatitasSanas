# app/api/v1/endpoints/consultas.py - VERSIÓN CORREGIDA
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import not_, func, or_
from typing import List, Optional
from datetime import datetime

from app.config.database import get_db
from app.crud.consulta import (
    solicitud_atencion
)
from app.models import Triaje, Veterinario, SolicitudAtencion
from app.models.mascota import Mascota
from app.models.cliente_mascota import ClienteMascota
from app.models.clientes import Cliente

from app.schemas.consulta_schema import (
    SolicitudAtencionResponse, SolicitudAtencionCreate
)

router = APIRouter()

@router.post("/", response_model=SolicitudAtencionResponse, status_code=status.HTTP_201_CREATED)
async def create_solicitud_atencion(
        solicitud_data: SolicitudAtencionCreate,
        db: Session = Depends(get_db)
):
    """
    Crear una nueva solicitud de atención
    """
    try:
        # Verificar que la mascota existe
        from app.crud import mascota
        mascota_obj = mascota.get(db, solicitud_data.id_mascota)
        if not mascota_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mascota no encontrada"
            )

        # Verificar que la recepcionista existe
        from app.crud import recepcionista
        recep_obj = recepcionista.get(db, solicitud_data.id_recepcionista)
        if not recep_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recepcionista no encontrada"
            )

        # Agregar timestamp actual si no se proporciona.
        # Nota: la clave existe en el dict con valor None (el schema la define como
        # Optional=None), por lo que dict.get(clave, default) NO aplica el default y
        # dejaría fecha_hora_solicitud = NULL. Se valida el valor explícitamente.
        solicitud_dict = solicitud_data.dict()
        if not solicitud_dict.get('fecha_hora_solicitud'):
            solicitud_dict['fecha_hora_solicitud'] = datetime.now()
        solicitud_dict['estado'] = 'Pendiente'  # Estado inicial

        # Crear la solicitud
        nueva_solicitud = solicitud_atencion.create(db, obj_in=solicitud_dict)

        return nueva_solicitud

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear solicitud: {str(e)}"
        )


@router.get("/", response_model=List[SolicitudAtencionResponse])
async def get_solicitudes_atencion(
        db: Session = Depends(get_db),
        estado: Optional[str] = Query(None, description="Filtrar por estado"),
        tipo_solicitud: Optional[str] = Query(None, description="Filtrar por tipo"),
        mascota_id: Optional[int] = Query(None, description="Filtrar por mascota"),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener lista de solicitudes de atención con filtros
    """
    try:
        if estado:
            solicitudes = solicitud_atencion.get_by_estado(db, estado=estado)
        elif tipo_solicitud:
            solicitudes = solicitud_atencion.get_by_tipo(db, tipo_solicitud=tipo_solicitud)
        elif mascota_id:
            solicitudes = solicitud_atencion.get_by_mascota(db, mascota_id=mascota_id)
        else:
            solicitudes = solicitud_atencion.get_multi(db, limit=limit, order_by='-fecha_hora_solicitud')

        return solicitudes[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes: {str(e)}"
        )


@router.get("/enriquecidas")
async def get_solicitudes_enriquecidas(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
        search: Optional[str] = Query(None, description="Buscar por nombre de mascota o dueño"),
        estado: Optional[str] = Query(None, description="Filtrar por estado de la solicitud"),
):
    """
    Lista de solicitudes ya enriquecida (mascota, dueño y veterinario) resuelta en UNA
    sola consulta con JOINs, paginada y filtrada en el servidor.

    Reemplaza el patrón N+1 del frontend (1 + N*3 peticiones HTTP: mascota, cliente y
    veterinario por cada fila) por una única respuesta, y mueve la búsqueda/filtro/orden
    al servidor para escalar a muchos registros.
    """
    try:
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

        return {
            "solicitudes": solicitudes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes enriquecidas: {str(e)}"
        )


@router.get("/{solicitud_id}", response_model=SolicitudAtencionResponse)
async def get_solicitud_atencion(
        solicitud_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener una solicitud específica por ID
    """
    try:
        solicitud = solicitud_atencion.get(db, solicitud_id)
        if not solicitud:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )
        return solicitud

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitud: {str(e)}"
        )

@router.get("/{solicitud_id}/veterinario")
async def get_veterinario_de_solicitud(
        solicitud_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener el veterinario asignado a una solicitud.

    La asignación no vive en la solicitud: el trigger la crea en el Triaje,
    así que se resuelve por la cadena Solicitud -> Triaje -> Veterinario.
    Si el trigger no asignó ninguno, devuelve 'Sin asignar'.
    """
    try:
        veterinario = db.query(Veterinario) \
            .join(Triaje, Triaje.id_veterinario == Veterinario.id_veterinario) \
            .filter(Triaje.id_solicitud == solicitud_id) \
            .first()

        if not veterinario:
            return {"id_veterinario": None, "nombre_veterinario": "Sin asignar"}

        return {
            "id_veterinario": veterinario.id_veterinario,
            "nombre_veterinario": f"{veterinario.nombre} {veterinario.apellido_paterno}".strip(),
            "tipo_veterinario": veterinario.tipo_veterinario,
            "turno": veterinario.turno,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinario de la solicitud: {str(e)}"
        )


@router.delete("/{solicitud_id}")
async def delete_solicitud(
        solicitud_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar una solicitud
    """
    solicitud_atencion_obj = solicitud_atencion.get(db, solicitud_id)
    if not solicitud_atencion_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )

    # SC-038 / F19: no permitir borrar una solicitud con triaje/consulta asociados.
    # El trigger crea un triaje automáticamente al insertar la solicitud y la FK es
    # NO ACTION, por lo que el borrado directo fallaba con 500. Se devuelve un 409
    # claro y se dirige a 'Cancelar' (estado Cancelada) para no perder historia clínica.
    tiene_triaje = db.query(Triaje).filter(Triaje.id_solicitud == solicitud_id).first()
    if tiene_triaje:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una solicitud con triaje/consulta asociados. Cámbiela a 'Cancelada' en su lugar.",
        )

    solicitud_atencion.remove(db, id=solicitud_id)
    return {"message": "Solicitud eliminada correctamente", "success": True}


@router.get("/veterinario/{id_usuario}", response_model=List[SolicitudAtencionResponse])
async def get_solicitudes_by_veterinario(
        id_usuario: int,
        estado: Optional[str] = Query(None, description="Filtrar por estado de la solicitud"),
        tipo_solicitud: Optional[str] = Query(None, description="Filtrar por tipo de solicitud"),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
        db: Session = Depends(get_db)
):
    """
    Obtener solicitudes de atención relacionadas con el veterinario por id_usuario.
    """
    try:
        # 1️⃣ Buscar el veterinario
        veterinario = db.query(Veterinario).filter(Veterinario.id_usuario == id_usuario).first()
        if not veterinario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        # 2️⃣ Buscar los triajes hechos por ese veterinario
        triajes = db.query(Triaje).filter(Triaje.id_veterinario == veterinario.id_veterinario).all()

        # 3️⃣ Obtener los IDs de solicitudes asignadas por triaje
        solicitud_ids = [triaje.id_solicitud for triaje in triajes]

        # 3️⃣.b Solicitudes sin triaje (no asignadas por el trigger). Si el trigger no
        # encontró un veterinario disponible, la solicitud queda sin triaje y sería
        # invisible para todos; se incluyen aquí para que el veterinario pueda verlas.
        solicitudes_sin_triaje_ids = db.query(SolicitudAtencion.id_solicitud).filter(
            not_(SolicitudAtencion.id_solicitud.in_(
                db.query(Triaje.id_solicitud)
            )),
            SolicitudAtencion.estado == 'Pendiente'
        ).all()
        solicitud_ids_sin_triaje = [s.id_solicitud for s in solicitudes_sin_triaje_ids]

        # 3️⃣.c Unir ambos conjuntos (triaje del vet + sin triaje)
        solicitud_ids = list(set(solicitud_ids) | set(solicitud_ids_sin_triaje))
        if not solicitud_ids:
            return []

        # 4️⃣ Consulta base de solicitudes
        query = db.query(SolicitudAtencion).filter(SolicitudAtencion.id_solicitud.in_(solicitud_ids))

        # 5️⃣ Filtros opcionales
        if estado:
            query = query.filter(SolicitudAtencion.estado == estado)
        if tipo_solicitud:
            query = query.filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud)

        solicitudes = query.limit(limit).all()

        return solicitudes

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes: {str(e)}"
        )
