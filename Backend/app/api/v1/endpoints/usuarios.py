# app/api/v1/endpoints/usuarios.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.config.database import get_db
from app.crud.usuario_crud import usuario
from app.crud.auth_crud import auth
from app.models.usuario import Usuario
from app.schemas.usuario_schema import (
    UsuarioCreate, UsuarioUpdate, UsuarioLogin, PasswordChange, PasswordReset,
    UsuarioResponse, UsuarioWithProfileResponse, UsuarioListResponse,
    AuthResponse, SessionInfoResponse, EstadisticasUsuarios, UsuarioSearch
)
from app.schemas.base_schema import MessageResponse

router = APIRouter()


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
        usuario_data: UsuarioCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo usuario base (sin perfil específico)
    """
    try:
        # Verificar que no existe el username
        if usuario.exists_by_username(db, username=usuario_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese username"
            )

        # Crear usuario
        nuevo_usuario = usuario.create(db, obj_in=usuario_data)

        return nuevo_usuario

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear usuario: {str(e)}"
        )


@router.post("/with-profile", response_model=UsuarioWithProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario_with_profile(
        user_data: dict,
        db: Session = Depends(get_db)
):
    """
    Crear usuario con perfil específico (Administrador, Veterinario, Recepcionista)

    Ejemplo de payload:
    {
        "user_data": {
            "username": "admin001",
            "contraseña": "password123"
        },
        "profile_data": {
            "nombre": "Juan",
            "apellido_paterno": "Pérez",
            "apellido_materno": "García",
            "dni": "12345678",
            "telefono": "987654321",
            "email": "juan@example.com",
            "fecha_ingreso": "2024-01-01",
            "genero": "M"
        },
        "user_type": "Administrador"
    }
    """
    try:
        user_info = user_data.get("user_data", {})
        profile_info = user_data.get("profile_data", {})
        user_type = user_data.get("user_type", "")

        if not user_type or user_type not in ["Administrador", "Veterinario", "Recepcionista"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_type debe ser Administrador, Veterinario o Recepcionista"
            )

        # Verificar username único
        if usuario.exists_by_username(db, username=user_info.get("username", "")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese username"
            )

        # Crear usuario con perfil
        nuevo_usuario = usuario.create_with_profile(
            db,
            user_data=user_info,
            profile_data=profile_info,
            user_type=user_type
        )

        # Obtener usuario con perfil
        usuario_completo = usuario.get_with_profile(db, user_id=nuevo_usuario.id_usuario)

        return {
            "id_usuario": nuevo_usuario.id_usuario,
            "username": nuevo_usuario.username,
            "tipo_usuario": nuevo_usuario.tipo_usuario,
            "estado": nuevo_usuario.estado,
            "fecha_creacion": nuevo_usuario.fecha_creacion,
            "perfil": usuario_completo["perfil"] if usuario_completo else None,
            "nombre_completo": f"{usuario_completo['perfil'].nombre} {usuario_completo['perfil'].apellido_paterno}" if usuario_completo and
                                                                                                                       usuario_completo[
                                                                                                                           "perfil"] else None,
            "email": usuario_completo["perfil"].email if usuario_completo and usuario_completo["perfil"] else None,
            "dni": usuario_completo["perfil"].dni if usuario_completo and usuario_completo["perfil"] else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear usuario con perfil: {str(e)}"
        )


@router.get("/", response_model=UsuarioListResponse)
async def get_usuarios(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        tipo_usuario: Optional[str] = Query(None, description="Filtrar por tipo"),
        estado: Optional[str] = Query(None, description="Filtrar por estado"),
        activos_solo: bool = Query(False, description="Solo usuarios activos")
):
    """
    Obtener lista de usuarios con paginación
    """
    try:
        skip = (page - 1) * per_page

        query = db.query(Usuario)

        if tipo_usuario:
            query = query.filter(Usuario.tipo_usuario == tipo_usuario)

        if estado:
            query = query.filter(Usuario.estado == estado)
        elif activos_solo:
            query = query.filter(Usuario.estado == "Activo")

        total = query.count()
        usuarios = query.order_by(Usuario.fecha_creacion.desc()) \
            .offset(skip) \
            .limit(per_page) \
            .all()

        return {
            "usuarios": usuarios,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
        usuario_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener un usuario específico por ID
    """
    try:
        usuario_obj = usuario.get(db, usuario_id)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuario: {str(e)}"
        )


@router.get("/{usuario_id}/with-profile", response_model=UsuarioWithProfileResponse)
async def get_usuario_with_profile(
        usuario_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener usuario con información del perfil específico
    """
    try:
        usuario_completo = usuario.get_with_profile(db, user_id=usuario_id)
        if not usuario_completo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        usuario_obj = usuario_completo["usuario"]
        perfil = usuario_completo["perfil"]

        return {
            "id_usuario": usuario_obj.id_usuario,
            "username": usuario_obj.username,
            "tipo_usuario": usuario_obj.tipo_usuario,
            "estado": usuario_obj.estado,
            "fecha_creacion": usuario_obj.fecha_creacion,
            "perfil": perfil,
            "nombre_completo": f"{perfil.nombre} {perfil.apellido_paterno}" if perfil else None,
            "email": perfil.email if perfil else None,
            "dni": perfil.dni if perfil else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuario con perfil: {str(e)}"
        )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
        usuario_id: int,
        usuario_data: UsuarioUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un usuario
    """
    try:
        usuario_obj = usuario.get(db, usuario_id)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Validar username único si se está actualizando
        update_data = usuario_data.dict(exclude_unset=True)
        if "username" in update_data:
            if usuario.exists_by_username(db, username=update_data["username"], exclude_id=usuario_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un usuario con ese username"
                )

        return usuario.update(db, db_obj=usuario_obj, obj_in=usuario_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar usuario: {str(e)}"
        )


@router.delete("/{usuario_id}", response_model=MessageResponse)
async def delete_usuario(
        usuario_id: int,
        db: Session = Depends(get_db),
        permanent: bool = Query(False, description="Eliminación permanente")
):
    """
    Eliminar usuario (soft delete por defecto, permanente opcional)
    """
    try:
        usuario_obj = usuario.get(db, usuario_id)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if permanent:
            success = usuario.delete_user_complete(db, user_id=usuario_id)
            message = "Usuario eliminado permanentemente" if success else "Error al eliminar usuario"
        else:
            usuario.deactivate_user(db, user_id=usuario_id)
            message = "Usuario desactivado"

        return {
            "message": message,
            "success": True,
            "usuario_id": usuario_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar usuario: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login_usuario(
        login_data: UsuarioLogin,
        db: Session = Depends(get_db)
):
    """
    Autenticar usuario
    """
    try:
        # Autenticar usando el auth CRUD
        auth_result = auth.authenticate_user(
            db,
            username=login_data.username,
            password=login_data.contraseña
        )

        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username o contraseña incorrectos"
            )

        usuario_obj = auth_result["usuario"]
        perfil = auth_result["perfil"]

        return {
            "success": True,
            "message": "Login exitoso",
            "usuario": {
                "id_usuario": usuario_obj.id_usuario,
                "username": usuario_obj.username,
                "tipo_usuario": usuario_obj.tipo_usuario,
                "estado": usuario_obj.estado,
                "fecha_creacion": usuario_obj.fecha_creacion
            },
            "tipo_usuario": auth_result["tipo_usuario"],
            "permisos": auth_result["permisos"],
            "session_info": {
                "nombre_completo": f"{perfil.nombre} {perfil.apellido_paterno}" if perfil else None,
                "email": perfil.email if perfil else None,
                "dni": perfil.dni if perfil else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en login: {str(e)}"
        )


@router.patch("/{usuario_id}/change-password", response_model=MessageResponse)
async def change_password(
        usuario_id: int,
        password_data: PasswordChange,
        db: Session = Depends(get_db)
):
    """
    Cambiar contraseña de usuario
    """
    try:
        # Verificar contraseña actual
        usuario_obj = usuario.get(db, usuario_id)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Usar auth CRUD para cambio de contraseña
        success, message = auth.change_password(
            db,
            user_id=usuario_id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return {
            "message": message,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )


@router.patch("/{usuario_id}/reset-password", response_model=MessageResponse)
async def reset_password(
        usuario_id: int,
        reset_data: PasswordReset,
        db: Session = Depends(get_db)
):
    """
    Resetear contraseña de usuario (solo para administradores)
    """
    try:
        # Verificar que el usuario existe
        usuario_obj = usuario.get(db, usuario_id)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Usar auth CRUD para reseteo
        success, message = auth.reset_password(
            db,
            username=reset_data.username,
            new_password=reset_data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return {
            "message": message,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al resetear contraseña: {str(e)}"
        )


@router.patch("/{usuario_id}/activate", response_model=MessageResponse)
async def activate_usuario(
        usuario_id: int,
        db: Session = Depends(get_db)
):
    """
    Activar usuario
    """
    try:
        usuario_obj = usuario.activate_user(db, user_id=usuario_id)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return {
            "message": "Usuario activado exitosamente",
            "success": True,
            "usuario_id": usuario_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al activar usuario: {str(e)}"
        )


@router.patch("/{usuario_id}/deactivate", response_model=MessageResponse)
async def deactivate_usuario(
        usuario_id: int,
        db: Session = Depends(get_db)
):
    """
    Desactivar usuario
    """
    try:
        usuario_obj = usuario.deactivate_user(db, user_id=usuario_id)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return {
            "message": "Usuario desactivado exitosamente",
            "success": True,
            "usuario_id": usuario_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar usuario: {str(e)}"
        )


@router.post("/search", response_model=UsuarioListResponse)
async def search_usuarios(
        search_params: UsuarioSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar usuarios con filtros avanzados
    """
    try:
        usuarios_result, total = usuario.search_usuarios(db, search_params=search_params)

        return {
            "usuarios": usuarios_result,
            "total": total,
            "page": search_params.page,
            "per_page": search_params.per_page,
            "total_pages": (total + search_params.per_page - 1) // search_params.per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de usuarios: {str(e)}"
        )


@router.get("/username/{username}", response_model=UsuarioResponse)
async def get_usuario_by_username(
        username: str,
        db: Session = Depends(get_db)
):
    """
    Obtener usuario por username
    """
    try:
        usuario_obj = usuario.get_by_username(db, username=username)
        if not usuario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar usuario: {str(e)}"
        )


@router.get("/tipo/{tipo_usuario}")
async def get_usuarios_by_tipo(
        tipo_usuario: str,
        db: Session = Depends(get_db),
        activos_solo: bool = Query(True, description="Solo usuarios activos")
):
    """
    Obtener usuarios por tipo
    """
    try:
        usuarios_list = usuario.get_by_tipo(db, tipo_usuario=tipo_usuario, activos_solo=activos_solo)

        return {
            "tipo_usuario": tipo_usuario,
            "activos_solo": activos_solo,
            "usuarios": usuarios_list,
            "total": len(usuarios_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios por tipo: {str(e)}"
        )


@router.get("/with-profiles/list")
async def get_usuarios_with_profiles(
        db: Session = Depends(get_db),
        skip: int = Query(0, ge=0, description="Elementos a omitir"),
        limit: int = Query(100, ge=1, le=200, description="Límite de elementos")
):
    """
    Obtener usuarios con información de sus perfiles
    """
    try:
        usuarios_list = usuario.get_usuarios_con_perfiles(db, skip=skip, limit=limit)

        return {
            "usuarios_con_perfiles": usuarios_list,
            "total": len(usuarios_list),
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios con perfiles: {str(e)}"
        )


@router.get("/estadisticas/resumen", response_model=EstadisticasUsuarios)
async def get_estadisticas_usuarios(
        db: Session = Depends(get_db)
):
    """
    Obtener estadísticas completas de usuarios
    """
    try:
        stats = usuario.get_estadisticas_usuarios(db)
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/recientes/list")
async def get_usuarios_recientes(
        db: Session = Depends(get_db),
        dias: int = Query(7, ge=1, le=30, description="Últimos X días"),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """
    Obtener usuarios creados recientemente
    """
    try:
        usuarios_list = usuario.get_usuarios_recientes(db, dias=dias, limit=limit)

        return {
            "usuarios_recientes": usuarios_list,
            "total": len(usuarios_list),
            "periodo_dias": dias
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios recientes: {str(e)}"
        )


@router.get("/{usuario_id}/session-info", response_model=SessionInfoResponse)
async def get_session_info(
        usuario_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener información de sesión del usuario
    """
    try:
        session_info = auth.get_user_session_info(db, user_id=usuario_id)
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return session_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener información de sesión: {str(e)}"
        )


@router.post("/{usuario_id}/logout", response_model=MessageResponse)
async def logout_usuario(
        usuario_id: int,
        db: Session = Depends(get_db)
):
    """
    Cerrar sesión del usuario
    """
    try:
        success = auth.logout_user(db, user_id=usuario_id)

        return {
            "message": "Sesión cerrada exitosamente" if success else "Error al cerrar sesión",
            "success": success
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al cerrar sesión: {str(e)}"
        )


@router.get("/debug/verify-username/{username}")
async def verify_username_available(
        username: str,
        db: Session = Depends(get_db)
):
    """
    Verificar si un username está disponible
    """
    try:
        exists = usuario.exists_by_username(db, username=username)

        return {
            "username": username,
            "exists": exists,
            "available": not exists
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al verificar username: {str(e)}"
        )