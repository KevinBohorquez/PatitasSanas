# app/api/v1/endpoints/veterinarios.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import get_db
from app.crud import veterinario
from app.crud.catalogo import especialidad as especialidad_crud
from app.queries import veterinario_queries
from app.schemas import VeterinarioResponse, VeterinarioCreate, VeterinarioUpdate

router = APIRouter()


@router.get("/")
async def get_veterinarios(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        especialidad: Optional[str] = Query(None, description="Filtrar por especialidad"),
        tipo_veterinario: Optional[str] = Query(None, description="Filtrar por tipo de veterinario"),
        disposicion: Optional[str] = Query(None, description="Filtrar por disposición"),
        turno: Optional[str] = Query(None, description="Filtrar por turno"),
        solo_activos: Optional[bool] = Query(None, description="Si es true, solo devuelve veterinarios cuyo usuario está Activo")
):
    """
    Obtener lista de veterinarios con paginación
    """
    try:
        skip = (page - 1) * per_page

        veterinarios, total = veterinario.get_paginated(
            db, skip=skip, limit=per_page,
            especialidad=especialidad, tipo_veterinario=tipo_veterinario,
            disposicion=disposicion, turno=turno, solo_activos=solo_activos
        )

        return {
            "veterinarios": veterinarios,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinarios: {str(e)}"
        )


@router.get("/disponibles")
async def get_veterinarios_disponibles(
        db: Session = Depends(get_db),
        turno: Optional[str] = Query(None, description="Filtrar por turno"),
        especialidad_id: Optional[int] = Query(None, description="Filtrar por ID de especialidad")
):
    """
    Obtener veterinarios ASIGNABLES para una cita (SC-017 / F5).

    Antes filtraba disposicion='Libre', lo que dejaba la lista frecuentemente
    vacía (hueco de turnos 23:00-07:00, CONVERT_TZ NULL, etc.). Ahora devuelve
    todos los veterinarios ACTIVOS ordenados por disposición
    (Libre -> Ocupado -> Fuera de turno), para que la recepcionista siempre tenga
    a quién asignar y vea el estado de cada uno.

    IMPORTANTE: debe declararse ANTES de "/{veterinario_id}" para que FastAPI
    no intente parsear "disponibles" como un id entero (causaría un 422).
    """
    try:
        veterinarios = veterinario.get_disponibles(
            db, turno=turno, especialidad_id=especialidad_id
        )

        return {
            "veterinarios_disponibles": veterinarios,
            "total": len(veterinarios),
            "filtros": {
                "turno": turno,
                "especialidad_id": especialidad_id
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinarios disponibles: {str(e)}"
        )


@router.get("/{veterinario_id}")
async def get_veterinario(
        veterinario_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener un veterinario específico por ID
    """
    try:
        veterinario_obj = veterinario.get(db, veterinario_id)

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinario: {str(e)}"
        )


@router.get("/dni/{dni}")
async def get_veterinario_by_dni(
        dni: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por DNI
    """
    try:
        if len(dni) != 8 or not dni.isdigit():
            raise HTTPException(
                status_code=400,
                detail="DNI debe tener exactamente 8 dígitos"
            )

        veterinario_obj = veterinario.get_by_dni(db, dni=dni)

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar veterinario: {str(e)}"
        )


@router.get("/email/{email}")
async def get_veterinario_by_email(
        email: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por email
    """
    try:
        veterinario_obj = veterinario.get_by_email(db, email=email)

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar veterinario: {str(e)}"
        )


@router.get("/codigo-cmvp/{codigo_cmvp}")
async def get_veterinario_by_codigo_cmvp(
        codigo_cmvp: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por código CMVP
    """
    try:
        veterinario_obj = veterinario.get_by_codigo_cmvp(db, codigo_cmvp=codigo_cmvp)

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar veterinario: {str(e)}"
        )


@router.get("/especialidad/{especialidad_id}")
async def get_veterinarios_by_especialidad(
        especialidad_id: int,
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """
    Obtener veterinarios por ID de especialidad
    """
    try:
        skip = (page - 1) * per_page

        # Verificar que la especialidad existe
        especialidad_obj = especialidad_crud.get(db, especialidad_id)
        if not especialidad_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Especialidad no encontrada"
            )

        veterinarios, total = veterinario.get_by_especialidad(
            db, especialidad_id=especialidad_id, skip=skip, limit=per_page
        )

        return {
            "especialidad": {
                "id": especialidad_obj.id_especialidad,
                "nombre": especialidad_obj.descripcion
            },
            "veterinarios": veterinarios,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinarios por especialidad: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VeterinarioResponse)
async def create_veterinario(
        veterinario_data: VeterinarioCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo veterinario
    """
    try:
        # Verificar que la especialidad existe
        especialidad_obj = especialidad_crud.get(db, veterinario_data.id_especialidad)

        if not especialidad_obj:
            raise HTTPException(
                status_code=404,
                detail="Especialidad no encontrada"
            )

        # Verificar duplicados DNI
        if veterinario.exists_by_dni(db, dni=veterinario_data.dni):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un veterinario con este DNI"
            )

        # Verificar duplicados email
        if veterinario.exists_by_email(db, email=veterinario_data.email):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un veterinario con este email"
            )

        # Verificar duplicados código CMVP
        if veterinario.exists_by_codigo_cmvp(db, codigo_cmvp=veterinario_data.codigo_CMVP):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un veterinario con este código CMVP"
            )

        # Crear el veterinario
        nuevo_veterinario = veterinario.create(db, obj_in=veterinario_data)

        return nuevo_veterinario

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear veterinario: {str(e)}"
        )


@router.put("/{veterinario_id}", response_model=VeterinarioResponse)
async def update_veterinario(
        veterinario_id: int,
        veterinario_data: VeterinarioUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un veterinario existente
    """
    try:
        # Verificar que el veterinario existe
        veterinario_obj = veterinario.get(db, veterinario_id)
        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Verificar especialidad si se está actualizando
        if veterinario_data.id_especialidad:
            especialidad_obj = especialidad_crud.get(db, veterinario_data.id_especialidad)

            if not especialidad_obj:
                raise HTTPException(
                    status_code=404,
                    detail="Especialidad no encontrada"
                )

        # Verificar email único si se está actualizando
        if veterinario_data.email:
            if veterinario.exists_by_email(db, email=veterinario_data.email, exclude_id=veterinario_id):
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe otro veterinario con este email"
                )

        # Verificar código CMVP único si se está actualizando
        if veterinario_data.codigo_CMVP:
            if veterinario.exists_by_codigo_cmvp(db, codigo_cmvp=veterinario_data.codigo_CMVP,
                                                 exclude_id=veterinario_id):
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe otro veterinario con este código CMVP"
                )

        # Actualizar el veterinario
        veterinario_actualizado = veterinario.update(db, db_obj=veterinario_obj, obj_in=veterinario_data)

        return veterinario_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar veterinario: {str(e)}"
        )

@router.delete("/{veterinario_id}")
async def delete_veterinario(
    veterinario_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un veterinario
    """
    try:
        # Verificar que el veterinario existe
        veterinario_obj = veterinario.get(db, veterinario_id)
        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Verificar si el veterinario tiene citas pendientes o está ocupado
        if veterinario_obj.disposicion == "Ocupado":
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar un veterinario que está ocupado"
            )

        # Eliminar el veterinario
        veterinario.remove(db, id=veterinario_id)

        return {
            "message": "Veterinario eliminado exitosamente",
            "veterinario_id": veterinario_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar veterinario: {str(e)}"
        )


@router.put("/veterinario/usuario/{id_usuario}/disposicion", response_model=VeterinarioResponse)
async def update_veterinario_disposicion(
        id_usuario: int,
        db: Session = Depends(get_db)
):
    """
    Actualizar la disposición de un veterinario a 'Ocupado'
    """
    try:
        # Buscar al veterinario usando el id_usuario
        veterinario_obj = veterinario.get_by_usuario(db, id_usuario=id_usuario)

        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Crear objeto con los datos a actualizar
        disposicion_data = {"disposicion": "Ocupado"}

        # Actualizar el veterinario usando el patrón .update()
        veterinario_actualizado = veterinario.update(db, db_obj=veterinario_obj, obj_in=disposicion_data)

        return veterinario_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar disposición: {str(e)}"
        )

@router.put("/veterinario/usuario/{id_usuario}/disposicionLibre", response_model=VeterinarioResponse)
async def update_veterinario_disposicion_libre(
        id_usuario: int,
        db: Session = Depends(get_db)
):
    """
    Actualizar la disposición de un veterinario a 'Libre'.
    (SC-033 / F14: nombre de función único —antes duplicaba
    update_veterinario_disposicion— y docstring corregido, decía 'Ocupado'.)
    """
    try:
        # Buscar al veterinario usando el id_usuario
        veterinario_obj = veterinario.get_by_usuario(db, id_usuario=id_usuario)

        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Crear objeto con los datos a actualizar
        disposicion_data = {"disposicion": "Libre"}

        # Actualizar el veterinario usando el patrón .update()
        veterinario_actualizado = veterinario.update(db, db_obj=veterinario_obj, obj_in=disposicion_data)

        return veterinario_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar disposición: {str(e)}"
        )

@router.get("/resultados-citas/{id_usuario}")
def get_resultados_y_citas(id_usuario: int, db: Session = Depends(get_db)):
    # Buscar al veterinario por id_usuario
    vet = veterinario.get_by_usuario(db, id_usuario=id_usuario)
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinario no encontrado")

    return veterinario_queries.get_resultados_citas(db, id_veterinario=vet.id_veterinario)


@router.get("/citas-programadas/{id_usuario}")
def get_citas_programadas(id_usuario: int, db: Session = Depends(get_db)):
    """
    Citas PROGRAMADAS asignadas al veterinario, resueltas por Cita.id_veterinario
    (SC-016 / F4). A diferencia de /resultados-citas (que dependía de
    Resultado_servicio), incluye las citas creadas por el recepcionista que antes
    no llegaban al veterinario.
    """
    vet = veterinario.get_by_usuario(db, id_usuario=id_usuario)
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinario no encontrado")

    return veterinario_queries.get_citas_programadas(db, id_veterinario=vet.id_veterinario)


@router.get("/dashboard/{id_usuario}")
def get_dashboard_veterinario(id_usuario: int, db: Session = Depends(get_db)):
    """
    Resumen para el panel de inicio del veterinario, resuelto por su id_usuario:
    perfil (especialidad, turno, disposición), próxima cita, número de citas
    pendientes de atender, solicitudes asignadas y últimas atenciones.
    """
    data = veterinario_queries.get_dashboard(db, id_usuario=id_usuario)
    if data is None:
        raise HTTPException(status_code=404, detail="Veterinario no encontrado")
    return data
