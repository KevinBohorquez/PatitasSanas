# app/api/v1/endpoints/mascota.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from typing import List
from app.config.database import get_db
from app.crud import mascota, cliente
from app.crud.catalogo import raza
from app.queries import mascota_queries
from app.models.mascota import Mascota
from app.models.cliente_mascota import ClienteMascota
from app.schemas import (
    MascotaCreate, MascotaUpdate, MascotaResponse, MascotaSearch
)
from app.api.deps import get_mascota_or_404

router = APIRouter()


@router.post("/imagen")
async def subir_imagen_mascota(file: UploadFile = File(...), nombre: str = Form(None)):
    """Sube una imagen a Google Drive y devuelve el enlace. `nombre` es el nombre base
    (sin extensión) con el que se guardará el archivo, para identificarlo fácilmente."""
    import os as _os
    from app.services.storage.drive_oauth import subir_imagen
    if not (file.content_type or '').startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    contenido = await file.read()
    if len(contenido) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen no debe superar 8 MB")
    ext = _os.path.splitext(file.filename or '')[1].lower() or '.jpg'
    base = (nombre or 'mascota').strip() or 'mascota'
    filename = f"{base}{ext}"
    try:
        url = subir_imagen(contenido, filename, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")
    return {"url": url}


@router.post("/", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
async def create_mascota(
        mascota_data: MascotaCreate,
        cliente_id: int = Query(..., description="ID del cliente propietario"),
        db: Session = Depends(get_db)
):
    """
    Crear una nueva mascota y asociarla a un cliente
    """
    # Verificar que el cliente existe
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente no existe"
        )

    # Verificar que la raza existe (SC-037 / F18: debe responder 400, no 500).
    raza_obj = raza.get(db, mascota_data.id_raza)
    if not raza_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Raza no existe"
        )

    # Crear la mascota
    nueva_mascota = mascota.create(db, obj_in=mascota_data)

    # Crear la relación cliente-mascota
    relacion = ClienteMascota(
        id_cliente=cliente_id,
        id_mascota=nueva_mascota.id_mascota
    )
    db.add(relacion)
    db.commit()

    return nueva_mascota


@router.get("/")
async def get_mascotas(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        sexo: Optional[str] = Query(None, description="Filtrar por sexo"),
        id_raza: Optional[int] = Query(None, description="Filtrar por raza")
):
    """
    Obtener lista de mascotas con paginación
    """
    result, total = mascota_queries.listar_con_cliente_especie(
        db, page=page, per_page=per_page, sexo=sexo, id_raza=id_raza
    )

    return {
        "mascotas": result,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/enriquecidas")
async def get_mascotas_enriquecidas(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """
    Listado de mascotas ya enriquecido (especie, raza, próxima cita y última atención)
    resuelto en UNA sola consulta con JOINs, paginado en el servidor.

    Reemplaza el patrón N+1 del listado del veterinario (1 + N*3 peticiones HTTP por
    fila: /info, /proxima-cita y /ultima-atencion) por una única respuesta.

    IMPORTANTE: debe declararse ANTES de "/{mascota_id}" para que FastAPI no intente
    parsear "enriquecidas" como un id (causaría un 422).
    """
    try:
        mascotas, total = mascota_queries.listar_enriquecidas(db, page=page, per_page=per_page)
        return {
            "mascotas": mascotas,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mascotas enriquecidas: {str(e)}"
        )


@router.get("/selector")
async def get_mascotas_selector(db: Session = Depends(get_db)):
    """
    Todas las mascotas con su especie y dueño principal, en UNA sola consulta, para los
    selectores "Mascota (Dueño)" de los formularios de Nueva Solicitud / Nueva Cita.

    Reemplaza el patrón N+1 del front (1 fetch a /catalogos/cliente-mascota/mascota/{id}
    por mascota → ~N peticiones por apertura del formulario).

    IMPORTANTE: debe declararse ANTES de "/{mascota_id}" para que FastAPI no intente
    parsear "selector" como un id (causaría un 422).
    """
    try:
        return {"mascotas": mascota_queries.listar_para_selector(db)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mascotas para selector: {str(e)}"
        )


@router.get("/{mascota_id}", response_model=MascotaResponse)
async def get_mascota(
        mascota_obj: Mascota = Depends(get_mascota_or_404)
):
    """
    Obtener una mascota específica por ID
    """
    return mascota_obj


@router.get("/{mascota_id}/details")
async def get_mascota_with_details(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener mascota con detalles del cliente y raza
    """
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    extra = mascota_queries.get_cliente_y_raza(
        db, mascota_id=mascota_id, id_raza=mascota_obj.id_raza
    )

    return {
        "id_mascota": mascota_obj.id_mascota,
        "nombre": mascota_obj.nombre,
        "sexo": mascota_obj.sexo,
        "color": mascota_obj.color,
        "edad_anios": mascota_obj.edad_anios,
        "edad_meses": mascota_obj.edad_meses,
        "esterilizado": mascota_obj.esterilizado,
        "imagen": mascota_obj.imagen,
        "id_raza": mascota_obj.id_raza,
        "cliente": extra["cliente"],
        "raza": extra["raza"]
    }


@router.put("/{mascota_id}", response_model=MascotaResponse)
async def update_mascota(
        mascota_id: int,
        mascota_data: MascotaUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar una mascota
    """
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    # Validar raza si se está actualizando (SC-037 / F18: debe responder 400, no 500).
    update_data = mascota_data.dict(exclude_unset=True)
    if "id_raza" in update_data:
        raza_obj = raza.get(db, update_data["id_raza"])
        if not raza_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Raza no existe"
            )

    return mascota.update(db, db_obj=mascota_obj, obj_in=mascota_data)


@router.get("/info/{mascota_id}")
async def get_mascota_by_id(mascota_id: int, db: Session = Depends(get_db)):
    """
    Obtener los detalles de una mascota específica: nombre, especie, raza, género, color, etc.
    """
    try:
        mascota_row = mascota_queries.get_info(db, mascota_id=mascota_id)

        if not mascota_row:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")

        # Formatear la respuesta
        result = {
            "id_mascota": mascota_row.id_mascota,
            "nombre": mascota_row.nombre,
            "especie": mascota_row.especie,
            "raza": mascota_row.raza,
            "genero": mascota_row.genero,
            "color": mascota_row.color,
            "edad_anios": mascota_row.edad_anios,
            "edad_meses": mascota_row.edad_meses,
            "esterilizado": mascota_row.esterilizado,
            "imagen": mascota_row.imagen
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la mascota: {str(e)}")



@router.delete("/{mascota_id}")
async def delete_mascota(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar una mascota
    """
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    mascota.remove(db, id=mascota_id)
    return {"message": "Mascota eliminada correctamente", "success": True}


@router.post("/search")
async def search_mascotas(
        search_params: MascotaSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar mascotas con filtros avanzados
    """
    mascotas_result, total = mascota.search_mascotas(db, search_params=search_params)

    return {
        "mascotas": mascotas_result,
        "total": total,
        "page": search_params.page,
        "per_page": search_params.per_page,
        "total_pages": (total + search_params.per_page - 1) // search_params.per_page
    }


@router.get("/cliente/{cliente_id}/list")
async def get_mascotas_by_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todas las mascotas de un cliente específico
    """
    # Verificar que el cliente existe
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    mascotas = mascota.get_mascotas_by_cliente(db, cliente_id=cliente_id)

    return {
        "cliente_id": cliente_id,
        "cliente_nombre": f"{cliente_obj.nombre} {cliente_obj.apellido_paterno}",
        "mascotas": mascotas,
        "total": len(mascotas)
    }


@router.get("/stats/por-sexo")
async def get_estadisticas_por_sexo(
        db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de mascotas por sexo
    """
    stats = mascota.count_mascotas_by_sexo(db)
    return {
        "estadisticas_por_sexo": stats,
        "total": stats["machos"] + stats["hembras"]
    }


@router.get("/no-esterilizadas/list")
async def get_mascotas_no_esterilizadas(
        db: Session = Depends(get_db)
):
    """
    Obtener mascotas no esterilizadas
    """
    mascotas = mascota.get_mascotas_no_esterilizadas(db)
    return {
        "mascotas_no_esterilizadas": mascotas,
        "total": len(mascotas)
    }

@router.get("/proxima-cita/{mascota_id}")
async def get_proxima_cita_mascota(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener la próxima cita programada de una mascota específica
    """
    try:
        proxima_cita = mascota_queries.get_proxima_cita(db, mascota_id=mascota_id)

        if not proxima_cita:
            return {
                "mascota_id": mascota_id,
                "proxima_cita": None,
                "fecha_hora_programada": None,
                "servicio": "No hay citas programadas",
                "mensaje": "No hay citas programadas"
            }

        return {
            "mascota_id": mascota_id,
            "proxima_cita": proxima_cita.id_cita,
            "fecha_hora_programada": proxima_cita.fecha_hora_programada,
            "servicio": proxima_cita.nombre_servicio,
            "estado": proxima_cita.estado_cita
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener próxima cita: {str(e)}"
        )


@router.get("/ultima-atencion/{mascota_id}")
async def get_ultima_atencion_mascota(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener la última atención recibida por una mascota específica
    """
    try:
        ultima_atencion = mascota_queries.get_ultima_atencion(db, mascota_id=mascota_id)

        if not ultima_atencion:
            return {
                "mascota_id": mascota_id,
                "ultima_atencion": None,
                "fecha_hora_solicitud": None,
                "tipo_solicitud": "--",
                "recepcionista": "--",
                "mensaje": "No hay atenciones registradas"
            }

        return {
            "mascota_id": mascota_id,
            "ultima_atencion": ultima_atencion.id_solicitud,
            "fecha_hora_solicitud": ultima_atencion.fecha_hora_solicitud,
            "tipo_solicitud": ultima_atencion.tipo_solicitud,
            "estado": ultima_atencion.estado,
            "recepcionista": ultima_atencion.recepcionista
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener última atención: {str(e)}"
        )


@router.get("/mascota_cliente_servicio/{id_mascota}", response_model=List[dict])
async def get_mascota_cliente_servicio(id_mascota: int, db: Session = Depends(get_db)):
    try:
        data = mascota_queries.get_cliente_servicio(db, id_mascota=id_mascota)

        if not data:
            raise HTTPException(status_code=404, detail="Mascota no encontrada o no tiene servicios asociados")

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")
