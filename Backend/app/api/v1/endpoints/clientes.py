# app/api/v1/endpoints/clientes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud import cliente
from app.models.clientes import Cliente  # ✅ Importar el modelo directamente
from app.schemas import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    ClienteListResponse, ClienteSearch, MessageResponse
)
from app.api.deps import get_cliente_or_404, validate_pagination

router = APIRouter()


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
        cliente_data: ClienteCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo cliente
    """
    # Validar duplicados
    if cliente.exists_by_dni(db, dni=cliente_data.dni):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un cliente con ese DNI"
        )

    if cliente.exists_by_email(db, email=cliente_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un cliente con ese email"
        )

    return cliente.create(db, obj_in=cliente_data)


@router.get("/", response_model=ClienteListResponse)
async def get_clientes(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        estado: Optional[str] = Query(None, description="Filtrar por estado"),
        genero: Optional[str] = Query(None, description="Filtrar por género (F/M)")
):
    """
    Obtener lista de clientes con paginación
    """
    skip = (page - 1) * per_page

    query = db.query(Cliente)  # ✅ Usar Cliente directamente
    if estado:
        query = query.filter(Cliente.estado == estado)
    
    if genero:
        if genero not in ['F', 'M']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El género debe ser F (Femenino) o M (Masculino)"
            )
        query = query.filter(Cliente.genero == genero)

    total = query.count()
    clientes = query.offset(skip).limit(per_page).all()

    return {
        "clientes": clientes,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
        cliente_obj: Cliente = Depends(get_cliente_or_404)  # ✅ CORRECTO
):
    """
    Obtener un cliente específico por ID
    """
    return cliente_obj


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
        cliente_id: int,
        cliente_data: ClienteUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un cliente
    """
    # Verificar que existe
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    # Validar duplicados si se están actualizando
    update_data = cliente_data.dict(exclude_unset=True)

    if "dni" in update_data:
        if cliente.exists_by_dni(db, dni=update_data["dni"], exclude_id=cliente_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un cliente con ese DNI"
            )

    if "email" in update_data:
        if cliente.exists_by_email(db, email=update_data["email"], exclude_id=cliente_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un cliente con ese email"
            )

    return cliente.update(db, db_obj=cliente_obj, obj_in=cliente_data)


@router.delete("/{cliente_id}", response_model=MessageResponse)
async def delete_cliente(
        cliente_id: int,
        db: Session = Depends(get_db),
        permanent: bool = Query(False, description="Eliminación permanente")
):
    """
    Eliminar un cliente (soft delete por defecto)
    """
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    if permanent:
        cliente.remove(db, id=cliente_id)
        message = "Cliente eliminado permanentemente"
    else:
        cliente.soft_delete(db, id=cliente_id)
        message = "Cliente desactivado"

    return {"message": message, "success": True}


@router.post("/search", response_model=ClienteListResponse)
async def search_clientes(
        search_params: ClienteSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar clientes con filtros avanzados
    """
    clientes_result, total = cliente.search_clientes(db, search_params=search_params)

    return {
        "clientes": clientes_result,
        "total": total,
        "page": search_params.page,
        "per_page": search_params.per_page,
        "total_pages": (total + search_params.per_page - 1) // search_params.per_page
    }


@router.get("/{cliente_id}/mascotas")
async def get_mascotas_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todas las mascotas de un cliente
    """
    from app.crud import mascota

    # Verificar que el cliente existe
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    mascotas = mascota.get_mascotas_by_cliente(db, cliente_id=cliente_id)

    return {
        "cliente": {
            "id": cliente_obj.id_cliente,
            "nombre": f"{cliente_obj.nombre} {cliente_obj.apellido_paterno}",
            "genero": cliente_obj.genero
        },
        "mascotas": mascotas,
        "total_mascotas": len(mascotas)
    }


@router.get("/dni/{dni}", response_model=ClienteResponse)
async def get_cliente_by_dni(
        dni: str,
        db: Session = Depends(get_db)
):
    """
    Obtener cliente por DNI
    """
    cliente_obj = cliente.get_by_dni(db, dni=dni)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente_obj


@router.get("/email/{email}", response_model=ClienteResponse)
async def get_cliente_by_email(
        email: str,
        db: Session = Depends(get_db)
):
    """
    Obtener cliente por email
    """
    cliente_obj = cliente.get_by_email(db, email=email)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente_obj


# ===== NUEVOS ENDPOINTS RELACIONADOS CON GÉNERO =====

@router.get("/genero/{genero}", response_model=ClienteListResponse)
async def get_clientes_by_genero(
        genero: str,
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """
    Obtener clientes filtrados por género
    """
    if genero not in ['F', 'M']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El género debe ser F (Femenino) ou M (Masculino)"
        )
    
    clientes_result = cliente.get_clientes_by_genero(db, genero=genero)
    
    # Aplicar paginación manual
    start = (page - 1) * per_page
    end = start + per_page
    clientes_paginated = clientes_result[start:end]
    total = len(clientes_result)
    
    return {
        "clientes": clientes_paginated,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/stats/genero")
async def get_estadisticas_genero(
        db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de clientes por género
    """
    estadisticas = cliente.get_estadisticas_por_genero(db)
    
    return {
        "estadisticas": estadisticas,
        "porcentajes": {
            "femenino": round((estadisticas['F'] / estadisticas['total'] * 100), 2) if estadisticas['total'] > 0 else 0,
            "masculino": round((estadisticas['M'] / estadisticas['total'] * 100), 2) if estadisticas['total'] > 0 else 0
        }
    }