# app/api/v1/endpoints/catalogos/servicios.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud.catalogo import servicio
from app.schemas.catalogo_schemas import (
    ServicioCreate, ServicioUpdate, ServicioResponse, ServicioWithTipoResponse
)
from app.schemas.base_schema import MessageResponse

router = APIRouter()

# ===== ENDPOINTS PARA SERVICIO =====

@router.post("/servicios/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
async def create_servicio(
        servicio_data: ServicioCreate,
        db: Session = Depends(get_db)
):
    """Crear un nuevo servicio"""
    try:
        # Validar duplicados
        if servicio.exists_by_nombre(db, nombre_servicio=servicio_data.nombre_servicio):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un servicio con ese nombre"
            )

        return servicio.create(db, obj_in=servicio_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear servicio: {str(e)}"
        )


@router.get("/servicios/", response_model=List[ServicioResponse])
async def get_servicios(
        db: Session = Depends(get_db),
        activos_solo: bool = Query(True, description="Solo servicios activos"),
        tipo_servicio_id: Optional[int] = Query(None, description="Filtrar por tipo")
):
    """Obtener lista de servicios"""
    try:
        if tipo_servicio_id:
            return servicio.get_by_tipo(db, tipo_servicio_id=tipo_servicio_id, solo_activos=activos_solo)
        elif activos_solo:
            return servicio.get_activos(db)
        else:
            return servicio.get_multi(db, limit=1000)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicios: {str(e)}"
        )


@router.get("/servicios/{servicio_id}", response_model=ServicioResponse)
async def get_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Obtener un servicio específico por ID"""
    try:
        servicio_obj = servicio.get(db, servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
        return servicio_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicio: {str(e)}"
        )


@router.get("/servicios/{servicio_id}/with-tipo", response_model=ServicioWithTipoResponse)
async def get_servicio_with_tipo_info(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Obtener servicio con información del tipo"""
    try:
        servicio_info = servicio.get_with_tipo_info(db, servicio_id=servicio_id)
        if not servicio_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
        return servicio_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicio con tipo: {str(e)}"
        )


@router.put("/servicios/{servicio_id}", response_model=ServicioResponse)
async def update_servicio(
        servicio_id: int,
        servicio_data: ServicioUpdate,
        db: Session = Depends(get_db)
):
    """Actualizar un servicio"""
    try:
        servicio_obj = servicio.get(db, servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        # Validar nombre único si se está actualizando
        update_data = servicio_data.dict(exclude_unset=True)
        if "nombre_servicio" in update_data:
            if servicio.exists_by_nombre(db, nombre_servicio=update_data["nombre_servicio"], exclude_id=servicio_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un servicio con ese nombre"
                )

        return servicio.update(db, db_obj=servicio_obj, obj_in=servicio_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar servicio: {str(e)}"
        )


@router.patch("/servicios/{servicio_id}/activate", response_model=MessageResponse)
async def activate_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Activar un servicio"""
    try:
        servicio_obj = servicio.activate_service(db, servicio_id=servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        return {"message": "Servicio activado exitosamente", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al activar servicio: {str(e)}"
        )


@router.patch("/servicios/{servicio_id}/deactivate", response_model=MessageResponse)
async def deactivate_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Desactivar un servicio"""
    try:
        servicio_obj = servicio.deactivate_service(db, servicio_id=servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        return {"message": "Servicio desactivado exitosamente", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar servicio: {str(e)}"
        )


@router.get("/servicios/search/nombre/{termino}")
async def search_servicios(
        termino: str,
        db: Session = Depends(get_db),
        activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
        tipo_servicio_id: Optional[int] = Query(None, description="Filtrar por tipo")
):
    """Buscar servicios por nombre"""
    try:
        servicios_encontrados = servicio.search_servicios(
            db,
            nombre=termino,
            activo=activo,
            tipo_servicio_id=tipo_servicio_id
        )
        return {
            "termino_busqueda": termino,
            "servicios": servicios_encontrados,
            "total": len(servicios_encontrados)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de servicios: {str(e)}"
        )


@router.get("/servicios/precio-range/list")
async def get_servicios_by_precio_range(
        db: Session = Depends(get_db),
        precio_min: Optional[float] = Query(None, description="Precio mínimo"),
        precio_max: Optional[float] = Query(None, description="Precio máximo")
):
    """Obtener servicios por rango de precio"""
    try:
        servicios_encontrados = servicio.get_by_precio_range(
            db,
            precio_min=precio_min,
            precio_max=precio_max
        )
        return {
            "precio_min": precio_min,
            "precio_max": precio_max,
            "servicios": servicios_encontrados,
            "total": len(servicios_encontrados)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicios por precio: {str(e)}"
        )


@router.get("/servicios/populares/top")
async def get_servicios_mas_solicitados(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """Obtener servicios más solicitados"""
    try:
        return servicio.get_mas_solicitados(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicios populares: {str(e)}"
        )


@router.get("/servicios/estadisticas/precios")
async def get_servicios_estadisticas_precios(db: Session = Depends(get_db)):
    """Obtener estadísticas de precios de servicios"""
    try:
        return servicio.get_estadisticas_precios(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas de precios: {str(e)}"
        )


@router.delete("/servicios/{servicio_id}", response_model=MessageResponse)
async def delete_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar un servicio permanentemente"""
    try:
        servicio_obj = servicio.get(db, servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        # Verificar si el servicio está siendo usado
        try:
            from app.crud.consulta import servicio_solicitado
            servicios_solicitados = servicio_solicitado.count_by_servicio(db, servicio_id=servicio_id)

            if servicios_solicitados > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede eliminar el servicio. Está siendo usado en {servicios_solicitados} solicitud(es). Considere desactivarlo en su lugar."
                )
        except ImportError:
            # Si no existe el modelo ServicioSolicitado, continuar con la eliminación
            pass

        # Eliminar el servicio
        success = servicio.remove(db, id=servicio_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el servicio"
            )

        return {
            "message": f"Servicio '{servicio_obj.nombre_servicio}' eliminado exitosamente",
            "success": True
        }

    except HTTPException as http_ex:
        # Re-raise HTTP exceptions para que FastAPI las maneje correctamente
        raise http_ex
    except Exception as e:
        # Para otros errores, crear una HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar servicio: {str(e)}"
        )
