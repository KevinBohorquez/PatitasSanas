# app/api/v1/endpoints/consultas/citas.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.config.database import get_db
from app.crud.consulta import cita
from app.crud.veterinario_crud import veterinario
from app.models import Cita, ResultadoServicio, ServicioSolicitado, Servicio, Veterinario, Mascota
from app.schemas.consulta_schema import CitaResponse, CitaCreate

router = APIRouter()

@router.post("/cita", response_model=CitaResponse, status_code=status.HTTP_201_CREATED)
async def create_cita(
    cita_data: CitaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva cita programada
    """
    try:
        # Verificar que la mascota existe
        from app.crud.mascota_crud import mascota
        mascota_obj = mascota.get(db, cita_data.id_mascota)
        if not mascota_obj:
            raise HTTPException(
                status_code=400,
                detail="Mascota no encontrada"
            )

        # Verificar que el servicio solicitado existe
        if cita_data.id_servicio_solicitado:
            from app.crud.consulta import servicio_solicitado
            servicio_obj = servicio_solicitado.get(db, cita_data.id_servicio_solicitado)
            if not servicio_obj:
                raise HTTPException(
                    status_code=400,
                    detail="Servicio solicitado no encontrado"
                )

        # Verificar que el veterinario asignado existe (SC-016 / F4).
        # El campo es opcional: si no se envía, la cita queda sin asignar.
        if cita_data.id_veterinario:
            vet_obj = veterinario.get(db, cita_data.id_veterinario)
            if not vet_obj:
                raise HTTPException(
                    status_code=400,
                    detail="Veterinario no encontrado"
                )

        # Crear la cita
        cita_dict = cita_data.dict()
        cita_dict["estado_cita"] = "Programada"
        nueva_cita = cita.create(db, obj_in=cita_dict)

        return nueva_cita

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear cita: {str(e)}"
        )


@router.get("/cita", response_model=List[CitaResponse])
async def get_citas(
    db: Session = Depends(get_db),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    mascota_id: Optional[int] = Query(None, description="Filtrar por mascota"),
    servicio_solicitado_id: Optional[int] = Query(None, description="Filtrar por servicio solicitado"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener lista de citas
    """
    try:
        if estado:
            citas = cita.get_by_estado(db, estado_cita=estado)
        elif mascota_id:
            citas = cita.get_by_mascota(db, mascota_id=mascota_id)
        elif servicio_solicitado_id:
            citas = db.query(cita.model).filter(
                cita.model.id_servicio_solicitado == servicio_solicitado_id
            ).order_by(cita.model.fecha_hora_programada).limit(limit).all()
        else:
            citas = cita.get_multi(db, limit=limit)

        return citas[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener citas: {str(e)}"
        )


@router.get("/cita/{cita_id}", response_model=CitaResponse)
async def get_cita(
    cita_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener una cita específica por ID
    """
    try:
        cita_obj = cita.get(db, cita_id)
        if not cita_obj:
            raise HTTPException(
                status_code=404,
                detail="Cita no encontrada"
            )
        return cita_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener cita: {str(e)}"
        )


@router.get("/citas/enriquecidas")
async def get_citas_enriquecidas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Buscar por nombre de mascota"),
    estado: Optional[str] = Query(None, description="Filtrar por estado de la cita"),
):
    """
    Lista de citas ya enriquecida (mascota, servicio y veterinario) resuelta en UNA sola
    consulta con JOINs, paginada y filtrada en el servidor.

    Reemplaza el patrón N+1 del frontend (1 + N*3 peticiones HTTP: mascota, servicio y
    veterinario por cada fila) por una única respuesta. Todos los JOIN son a filas únicas
    (claves), así que no hay riesgo de multiplicar filas.
    """
    try:
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

        return {
            "citas": citas,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener citas enriquecidas: {str(e)}"
        )


@router.patch("/cita/{cita_id}/atender", response_model=CitaResponse)
async def atender_cita(
    cita_id: int,
    db: Session = Depends(get_db)
):
    """
    Marcar cita como atendida y registrar ingreso automaticamente (HU-13)
    """
    try:
        cita_obj = cita.get(db, cita_id)
        if not cita_obj:
            raise HTTPException(
                status_code=404,
                detail="Cita no encontrada"
            )
        if cita_obj.estado_cita != "Programada":
            raise HTTPException(
                status_code=400,
                detail=f"La cita esta en estado '{cita_obj.estado_cita}', solo se puede atender citas programadas"
            )

        cita_atendida = cita.marcar_atendida(db, cita_id=cita_id)
        return cita_atendida

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al atender cita: {str(e)}"
        )


@router.delete("/cita/{cita_id}")
async def delete_cita(
        cita_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar una cita
    """
    cita_obj = cita.get(db, cita_id)
    if not cita_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    # SC-039 / SC-044 (F20 / F28): no borrar una cita con dependientes. La cascada del
    # ORM eliminaba el Resultado_servicio en silencio (pérdida del registro clínico), y
    # el Movimiento_Financiero (FK NO ACTION) hacía fallar el borrado con 500.
    from app.models.movimiento_financiero import MovimientoFinanciero
    dependientes = []
    if db.query(ResultadoServicio).filter(ResultadoServicio.id_cita == cita_id).first():
        dependientes.append("un resultado de servicio")
    if db.query(MovimientoFinanciero).filter(MovimientoFinanciero.id_cita == cita_id).first():
        dependientes.append("un movimiento financiero")
    if dependientes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar la cita: tiene {' y '.join(dependientes)} asociado(s).",
        )

    cita.remove(db, id=cita_id)
    return {"message": "Cita eliminada correctamente", "success": True}


@router.get("/citaServicio/{cita_id}")
async def get_cita_servicio_by_id(cita_id: int, db: Session = Depends(get_db)):
    try:
        # Importar los modelos necesarios
        from app.models.cita import Cita
        from app.models.servicio import Servicio
        from app.models.servicio_solicitado import ServicioSolicitado  # Asegúrate de importar este modelo

        # Realizar la consulta para obtener la cita con el nombre del servicio
        cita_obj = db.query(Cita, Servicio.nombre_servicio) \
            .join(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio) \
            .filter(Cita.id_cita == cita_id).first()

        if not cita_obj:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        # Devolver la respuesta con los detalles de la cita y el nombre del servicio
        return {
            "id_cita": cita_obj.Cita.id_cita,
            "fecha_hora_programada": cita_obj.Cita.fecha_hora_programada,
            "estado_cita": cita_obj.Cita.estado_cita,
            "nombre_servicio": cita_obj.nombre_servicio  # Nombre del servicio asociado
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cita: {str(e)}")


@router.get("/citaVeterinario/{cita_id}")
async def get_cita_veterinario_by_id(cita_id: int, db: Session = Depends(get_db)):
    try:
        # Obtener la cita con el servicio asociado y veterinario
        cita = db.query(
                Cita.id_cita,
                Cita.fecha_hora_programada,
                Cita.estado_cita,
                Servicio.nombre_servicio,
                Veterinario.nombre.label("veterinario_nombre"),
                Veterinario.apellido_paterno.label("veterinario_apellido")
            ) \
            .join(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio) \
            .join(ResultadoServicio, ResultadoServicio.id_cita == Cita.id_cita) \
            .join(Veterinario, ResultadoServicio.id_veterinario == Veterinario.id_veterinario) \
            .filter(Cita.id_cita == cita_id) \
            .first()

        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        return {
            "id_cita": cita.id_cita,
            "fecha_hora_programada": cita.fecha_hora_programada,
            "estado_cita": cita.estado_cita,
            "nombre_servicio": cita.nombre_servicio,
            "veterinario": f"{cita.veterinario_nombre} {cita.veterinario_apellido}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cita: {str(e)}")


@router.get("/citaMascota/{cita_id}")
async def get_mascota_from_cita(cita_id: int, db: Session = Depends(get_db)):
    try:
        # Realizar el JOIN entre la tabla Cita y Mascota
        result = db.query(Cita.id_cita, Mascota.nombre).join(Mascota, Cita.id_mascota == Mascota.id_mascota) \
            .filter(Cita.id_cita == cita_id).first()

        if not result:
            raise HTTPException(status_code=404, detail="Cita o mascota no encontrada")

        return {
            "id_cita": result.id_cita,
            "nombre_mascota": result.nombre
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cita: {str(e)}")
