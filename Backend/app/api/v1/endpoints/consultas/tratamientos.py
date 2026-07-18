# app/api/v1/endpoints/consultas/tratamientos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.crud.consulta_crud import consulta, tratamiento, historial_clinico, triaje, solicitud_atencion
from app.schemas.consulta_schema import TratamientoCreate, TratamientoResponse

router = APIRouter()

@router.post("/{consulta_id}/tratamientos", response_model=TratamientoResponse, status_code=status.HTTP_201_CREATED)
async def create_tratamiento(
        consulta_id: int,
        tratamiento_data: TratamientoCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un tratamiento para una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        # Actualizar el id_consulta con el de la URL
        tratamiento_data.id_consulta = consulta_id

        # Crear el tratamiento
        nuevo_tratamiento = tratamiento.create(db, obj_in=tratamiento_data)

        # Agregar evento al historial clínico
        triaje_obj = triaje.get(db, consulta_obj.id_triaje)
        if triaje_obj:
            solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud)
            if solicitud_obj:
                historial_clinico.add_evento_tratamiento(
                    db,
                    mascota_id=solicitud_obj.id_mascota,
                    tratamiento_id=nuevo_tratamiento.id_tratamiento,
                    veterinario_id=consulta_obj.id_veterinario,
                    descripcion=f"Tratamiento {tratamiento_data.tipo_tratamiento} iniciado para patología"
                )

        return nuevo_tratamiento

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tratamiento: {str(e)}"
        )


@router.get("/{consulta_id}/tratamientos")
async def get_tratamientos_consulta(
        consulta_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todos los tratamientos de una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        tratamientos_list = tratamiento.get_by_consulta(db, consulta_id=consulta_id)

        return {
            "consulta_id": consulta_id,
            "tratamientos": tratamientos_list,
            "total": len(tratamientos_list)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tratamientos: {str(e)}"
        )
