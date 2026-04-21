# app/api/v1/endpoints/administradores.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud.administrador_crud import administrador
from app.models.administrador import Administrador
from app.schemas.administrador_schema import (
    AdministradorCreate, AdministradorUpdate, AdministradorResponse,
    AdministradorWithUsuarioResponse, AdministradorListResponse,
    AdministradorSearch, EstadisticasAdministradores, AdministradorPasswordChange,
)
from app.schemas.base_schema import MessageResponse

router = APIRouter()


@router.post("/", response_model=AdministradorResponse, status_code=status.HTTP_201_CREATED)
async def create_administrador(
        admin_data: AdministradorCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo administrador con usuario
    """
    try:
        # Validar duplicados
        if administrador.exists_by_dni(db, dni=admin_data.dni):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un administrador con ese DNI"
            )

        if administrador.exists_by_email(db, email=admin_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un administrador con ese email"
            )

        # Verificar que el username no exista
        from app.crud.usuario_crud import usuario as usuario_crud
        if usuario_crud.exists_by_username(db, username=admin_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese username"
            )

        return administrador.create_complete(db, admin_data=admin_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear administrador: {str(e)}"
        )


@router.get("/", response_model=AdministradorListResponse)
async def get_administradores(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        genero: Optional[str] = Query(None, description="Filtrar por género"),
        activos_solo: bool = Query(False, description="Solo administradores activos")
):
    """
    Obtener lista de administradores con paginación
    """
    try:
        skip = (page - 1) * per_page

        if activos_solo:
            administradores = administrador.get_administradores_activos(db)
            total = len(administradores)
            # Aplicar paginación manual
            administradores = administradores[skip:skip + per_page]
        else:
            query = db.query(Administrador)

            if genero:
                query = query.filter(Administrador.genero == genero)

            total = query.count()
            administradores = query.order_by(Administrador.fecha_ingreso.desc()) \
                .offset(skip).limit(per_page).all()

        return {
            "administradores": administradores,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener administradores: {str(e)}"
        )


@router.get("/{admin_id}", response_model=AdministradorResponse)
async def get_administrador(
        admin_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener un administrador específico por ID
    """
    try:
        admin_obj = administrador.get(db, admin_id)
        if not admin_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )
        return admin_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener administrador: {str(e)}"
        )


@router.get("/{admin_id}/complete", response_model=AdministradorWithUsuarioResponse)
async def get_administrador_complete(
        admin_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener administrador con información completa de usuario
    """
    try:
        admin_with_usuario = administrador.get_with_usuario(db, admin_id=admin_id)
        if not admin_with_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )

        return {
            **admin_with_usuario["administrador"].__dict__,
            "usuario": admin_with_usuario["usuario"].__dict__ if admin_with_usuario["usuario"] else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener administrador completo: {str(e)}"
        )


@router.put("/{admin_id}", response_model=AdministradorResponse)
async def update_administrador(
        admin_id: int,
        admin_data: AdministradorUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un administrador
    """
    try:
        # Verificar que existe
        admin_obj = administrador.get(db, admin_id)
        if not admin_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )

        return administrador.update_profile(db, admin_id=admin_id, profile_data=admin_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar administrador: {str(e)}"
        )


@router.delete("/{admin_id}", response_model=MessageResponse)
async def delete_administrador(
        admin_id: int,
        db: Session = Depends(get_db),
        permanent: bool = Query(False, description="Eliminación permanente")
):
    """
    Eliminar un administrador (desactivar por defecto)
    """
    try:
        admin_obj = administrador.get(db, admin_id)
        if not admin_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )

        if permanent:
            from app.crud.usuario_crud import usuario as usuario_crud
            usuario_crud.delete_user_complete(db, user_id=admin_obj.id_usuario)
            message = "Administrador eliminado permanentemente"
        else:
            administrador.deactivate_user_account(db, admin_id=admin_id)
            message = "Administrador desactivado"

        return {"message": message, "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar administrador: {str(e)}"
        )


@router.post("/search", response_model=AdministradorListResponse)
async def search_administradores(
        search_params: AdministradorSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar administradores con filtros avanzados
    """
    try:
        administradores_result, total = administrador.search_administradores(db, search_params=search_params)

        return {
            "administradores": administradores_result,
            "total": total,
            "page": search_params.page,
            "per_page": search_params.per_page,
            "total_pages": (total + search_params.per_page - 1) // search_params.per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de administradores: {str(e)}"
        )


@router.get("/dni/{dni}", response_model=AdministradorResponse)
async def get_administrador_by_dni(
        dni: str,
        db: Session = Depends(get_db)
):
    """
    Obtener administrador por DNI
    """
    try:
        if len(dni) != 8 or not dni.isdigit():
            raise HTTPException(
                status_code=400,
                detail="DNI debe tener exactamente 8 dígitos"
            )

        admin_obj = administrador.get_by_dni(db, dni=dni)
        if not admin_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )
        return admin_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar administrador: {str(e)}"
        )


@router.get("/email/{email}", response_model=AdministradorResponse)
async def get_administrador_by_email(
        email: str,
        db: Session = Depends(get_db)
):
    """
    Obtener administrador por email
    """
    try:
        admin_obj = administrador.get_by_email(db, email=email)
        if not admin_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )
        return admin_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar administrador: {str(e)}"
        )


@router.get("/genero/{genero}")
async def get_administradores_by_genero(
        genero: str,
        db: Session = Depends(get_db)
):
    """
    Obtener administradores por género
    """
    try:
        if genero not in ['F', 'M']:
            raise HTTPException(
                status_code=400,
                detail="Género debe ser F o M"
            )

        administradores_list = administrador.get_by_genero(db, genero=genero)

        return {
            "genero": genero,
            "genero_descripcion": "Femenino" if genero == 'F' else "Masculino",
            "administradores": administradores_list,
            "total": len(administradores_list)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener administradores por género: {str(e)}"
        )


@router.get("/activos/list")
async def get_administradores_activos(
        db: Session = Depends(get_db)
):
    """
    Obtener solo administradores activos
    """
    try:
        administradores_activos = administrador.get_administradores_activos(db)

        return {
            "administradores_activos": administradores_activos,
            "total": len(administradores_activos)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener administradores activos: {str(e)}"
        )


@router.get("/recientes/list")
async def get_administradores_recientes(
        db: Session = Depends(get_db),
        dias: int = Query(30, ge=1, le=365, description="Días hacia atrás"),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """
    Obtener administradores ingresados recientemente
    """
    try:
        administradores_recientes = administrador.get_recientes(db, dias=dias, limit=limit)

        return {
            "administradores_recientes": administradores_recientes,
            "total": len(administradores_recientes),
            "periodo_dias": dias
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener administradores recientes: {str(e)}"
        )


@router.get("/estadisticas/general", response_model=EstadisticasAdministradores)
async def get_estadisticas_administradores(
        db: Session = Depends(get_db)
):
    """
    Obtener estadísticas generales de administradores
    """
    try:
        stats = administrador.get_estadisticas(db)
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/with-usuario-info/list")
async def get_administradores_with_usuario_info(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """
    Obtener administradores con información completa de usuario
    """
    try:
        skip = (page - 1) * per_page

        administradores_info = administrador.get_all_with_usuario_info(
            db, skip=skip, limit=per_page
        )

        # Contar total para paginación
        total = db.query(Administrador).count()

        return {
            "administradores": administradores_info,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener administradores con info de usuario: {str(e)}"
        )


@router.patch("/{admin_id}/activate", response_model=MessageResponse)
async def activate_administrador(
        admin_id: int,
        db: Session = Depends(get_db)
):
    """
    Activar cuenta de usuario del administrador
    """
    try:
        success = administrador.activate_user_account(db, admin_id=admin_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )

        return {
            "message": "Administrador activado exitosamente",
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al activar administrador: {str(e)}"
        )


@router.patch("/{admin_id}/deactivate", response_model=MessageResponse)
async def deactivate_administrador(
        admin_id: int,
        db: Session = Depends(get_db)
):
    """
    Desactivar cuenta de usuario del administrador
    """
    try:
        success = administrador.deactivate_user_account(db, admin_id=admin_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )

        return {
            "message": "Administrador desactivado exitosamente",
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar administrador: {str(e)}"
        )


@router.patch("/{admin_id}/change-password", response_model=MessageResponse)
async def change_administrador_password(
        admin_id: int,
        password_data: AdministradorPasswordChange,
        db: Session = Depends(get_db)
):
    """
    Cambiar contraseña de un administrador
    """
    try:
        if password_data.admin_id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de administrador no coincide"
            )

        success = administrador.change_user_password(
            db,
            admin_id=admin_id,
            new_password=password_data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrador no encontrado"
            )

        return {
            "message": "Contraseña cambiada exitosamente",
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )


@router.get("/debug/info")
async def debug_administrador_info(db: Session = Depends(get_db)):
    """
    Endpoint para depurar información de la tabla Administrador
    """
    try:
        # Obtener información de la tabla
        result = db.execute("DESCRIBE Administrador").fetchall()
        columns = [{"Field": row[0], "Type": row[1], "Null": row[2], "Key": row[3]} for row in result]

        # Contar registros
        total_count = db.query(Administrador).count()

        return {
            "table_info": {
                "name": "Administrador",
                "columns": columns,
                "total_records": total_count
            }
        }

    except Exception as e:
        return {
            "error": f"Error al obtener información: {str(e)}"
        }