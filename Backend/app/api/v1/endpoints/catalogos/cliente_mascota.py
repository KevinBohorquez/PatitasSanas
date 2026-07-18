# app/api/v1/endpoints/catalogos/cliente_mascota.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.crud.catalogo import cliente_mascota
from app.schemas.catalogo_schemas import (
    ClienteMascotaCreate, ClienteMascotaResponse
)
from app.schemas.base_schema import MessageResponse

router = APIRouter()

# ===== ENDPOINTS PARA CLIENTE_MASCOTA =====

@router.post("/cliente-mascota/", response_model=ClienteMascotaResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente_mascota_relation(
        relacion_data: ClienteMascotaCreate,
        db: Session = Depends(get_db)
):
    """Crear relación cliente-mascota"""
    try:
        # Verificar que no existe ya la relación
        if cliente_mascota.exists_relationship(
                db,
                cliente_id=relacion_data.id_cliente,
                mascota_id=relacion_data.id_mascota
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe la relación entre este cliente y mascota"
            )

        nueva_relacion = cliente_mascota.create_relationship(
            db,
            cliente_id=relacion_data.id_cliente,
            mascota_id=relacion_data.id_mascota
        )

        if not nueva_relacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear la relación"
            )

        return nueva_relacion

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear relación cliente-mascota: {str(e)}"
        )


@router.get("/cliente-mascota/cliente/{cliente_id}")
async def get_mascotas_by_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """Obtener mascotas de un cliente con información detallada"""
    try:
        mascotas_info = cliente_mascota.get_mascotas_info_by_cliente(db, cliente_id=cliente_id)
        return {
            "id_cliente": cliente_id,
            "mascotas": mascotas_info,
            "total_mascotas": len(mascotas_info)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mascotas del cliente: {str(e)}"
        )


@router.get("/cliente-mascota/mascota/{mascota_id}")
async def get_clientes_by_mascota(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """Obtener clientes de una mascota con información detallada"""
    try:
        clientes_info = cliente_mascota.get_clientes_info_by_mascota(db, mascota_id=mascota_id)
        return {
            "id_mascota": mascota_id,
            "clientes": clientes_info,
            "total_clientes": len(clientes_info)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener clientes de la mascota: {str(e)}"
        )


@router.delete("/cliente-mascota/{cliente_id}/{mascota_id}", response_model=MessageResponse)
async def delete_cliente_mascota_relation(
        cliente_id: int,
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar relación cliente-mascota"""
    try:
        success = cliente_mascota.remove_relationship(
            db,
            cliente_id=cliente_id,
            mascota_id=mascota_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relación cliente-mascota no encontrada"
            )

        return {"message": "Relación eliminada exitosamente", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar relación: {str(e)}"
        )


@router.put("/cliente-mascota/transfer/{mascota_id}")
async def transfer_mascota(
        mascota_id: int,
        cliente_anterior_id: int = Query(..., description="ID del cliente actual"),
        cliente_nuevo_id: int = Query(..., description="ID del nuevo cliente"),
        db: Session = Depends(get_db)
):
    """Transferir mascota entre clientes"""
    try:
        success = cliente_mascota.transfer_mascota(
            db,
            mascota_id=mascota_id,
            cliente_anterior_id=cliente_anterior_id,
            cliente_nuevo_id=cliente_nuevo_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo realizar la transferencia. Verifique que existe la relación actual y que no existe con el nuevo cliente."
            )

        return {
            "message": "Mascota transferida exitosamente",
            "success": True,
            "mascota_id": mascota_id,
            "cliente_anterior": cliente_anterior_id,
            "cliente_nuevo": cliente_nuevo_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al transferir mascota: {str(e)}"
        )


@router.get("/cliente-mascota/all/with-details")
async def get_all_relations_with_details(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """Obtener todas las relaciones con información detallada"""
    try:
        skip = (page - 1) * per_page

        relaciones_info = cliente_mascota.get_all_relationships_with_details(
            db, skip=skip, limit=per_page
        )

        total = cliente_mascota.count(db)

        return {
            "relaciones": relaciones_info,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener relaciones: {str(e)}"
        )


@router.get("/cliente-mascota/clientes-sin-mascotas/list")
async def get_clientes_sin_mascotas(db: Session = Depends(get_db)):
    """Obtener clientes que no tienen mascotas"""
    try:
        clientes_sin_mascotas = cliente_mascota.get_clientes_sin_mascotas(db)
        return {
            "clientes_sin_mascotas": clientes_sin_mascotas,
            "total": len(clientes_sin_mascotas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener clientes sin mascotas: {str(e)}"
        )


@router.get("/cliente-mascota/mascotas-sin-cliente/list")
async def get_mascotas_sin_cliente(db: Session = Depends(get_db)):
    """Obtener mascotas que no tienen cliente asignado"""
    try:
        mascotas_sin_cliente = cliente_mascota.get_mascotas_sin_cliente(db)
        return {
            "mascotas_sin_cliente": mascotas_sin_cliente,
            "total": len(mascotas_sin_cliente)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mascotas sin cliente: {str(e)}"
        )


@router.get("/cliente-mascota/estadisticas/general")
async def get_cliente_mascota_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas de relaciones cliente-mascota"""
    try:
        return cliente_mascota.get_estadisticas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.post("/cliente-mascota/bulk-assign/{cliente_id}")
async def bulk_assign_mascotas_to_cliente(
        cliente_id: int,
        mascota_ids: List[int],
        db: Session = Depends(get_db)
):
    """Asignar múltiples mascotas a un cliente"""
    try:
        asignadas, errores = cliente_mascota.bulk_assign_mascotas(
            db,
            cliente_id=cliente_id,
            mascota_ids=mascota_ids
        )

        return {
            "message": f"Proceso completado: {asignadas} mascotas asignadas",
            "success": True,
            "cliente_id": cliente_id,
            "mascotas_asignadas": asignadas,
            "total_intentos": len(mascota_ids),
            "errores": errores
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en asignación masiva: {str(e)}"
        )


@router.delete("/cliente-mascota/cliente/{cliente_id}/all", response_model=MessageResponse)
async def delete_all_relations_by_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar todas las relaciones de un cliente"""
    try:
        count = cliente_mascota.remove_all_relationships_by_cliente(db, cliente_id=cliente_id)

        return {
            "message": f"Se eliminaron {count} relaciones del cliente",
            "success": True,
            "cliente_id": cliente_id,
            "relaciones_eliminadas": count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar relaciones del cliente: {str(e)}"
        )


@router.delete("/cliente-mascota/mascota/{mascota_id}/all", response_model=MessageResponse)
async def delete_all_relations_by_mascota(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar todas las relaciones de una mascota"""
    try:
        count = cliente_mascota.remove_all_relationships_by_mascota(db, mascota_id=mascota_id)

        return {
            "message": f"Se eliminaron {count} relaciones de la mascota",
            "success": True,
            "mascota_id": mascota_id,
            "relaciones_eliminadas": count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar relaciones de la mascota: {str(e)}"
        )
