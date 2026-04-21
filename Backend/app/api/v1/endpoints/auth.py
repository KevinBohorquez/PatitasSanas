# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.config.database import get_db
from app.crud.auth_crud import auth
from app.schemas.auth_schema import (
    LoginRequest, LoginResponse, LoginErrorResponse,
    PasswordChangeRequest, PasswordChangeResponse,
    PasswordResetRequest, PasswordResetResponse,
    SessionInfoResponse, LogoutResponse,
    UserStatusValidationRequest, UserStatusValidationResponse,
    PermissionCheckRequest, PermissionCheckResponse,
    UserPermissionsResponse
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Iniciar sesión en el sistema
    Válido para Administradores, Veterinarios y Recepcionistas
    """
    try:
        # Autenticar usuario
        auth_result = auth.authenticate_user(
            db,
            username=login_data.username,
            password=login_data.password
        )

        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )

        usuario = auth_result["usuario"]
        perfil = auth_result["perfil"]

        # Preparar información de respuesta
        user_info = {
            "id_usuario": usuario.id_usuario,
            "username": usuario.username,
            "tipo_usuario": usuario.tipo_usuario,
            "estado": usuario.estado,
            "fecha_creacion": usuario.fecha_creacion
        }

        # Información de sesión
        session_info = auth.get_user_session_info(db, user_id=usuario.id_usuario)

        return LoginResponse(
            success=True,
            message=f"Bienvenido {session_info.get('nombre_completo', usuario.username)}",
            user_info=user_info,
            session_info=session_info,
            permisos=auth_result["permisos"],
            tipo_usuario=usuario.tipo_usuario
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/logout")
async def logout(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    Cerrar sesión del usuario
    """
    try:
        # Validar que el usuario existe
        user_data = auth.get_user_by_id(db, user_id=user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Cerrar sesión
        logout_success = auth.logout_user(db, user_id=user_id)

        if logout_success:
            return LogoutResponse(
                success=True,
                message="Sesión cerrada exitosamente",
                user_id=user_id,
                logout_time=None  # Se puede agregar timestamp real
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al cerrar sesión"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.get("/session/{user_id}", response_model=SessionInfoResponse)
async def get_session_info(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener información de la sesión actual del usuario
    """
    try:
        session_info = auth.get_user_session_info(db, user_id=user_id)

        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión no encontrada"
            )

        return SessionInfoResponse(**session_info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de sesión: {str(e)}"
        )


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
        password_data: PasswordChangeRequest,
        db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario
    """
    try:
        success, message = auth.change_password(
            db,
            user_id=password_data.user_id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )

        if success:
            return PasswordChangeResponse(
                success=True,
                message=message,
                user_id=password_data.user_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
        reset_data: PasswordResetRequest,
        db: Session = Depends(get_db)
):
    """
    Resetear contraseña (solo para administradores)
    """
    try:
        success, message = auth.reset_password(
            db,
            username=reset_data.username,
            new_password=reset_data.new_password
        )

        if success:
            return PasswordResetResponse(
                success=True,
                message=message,
                username=reset_data.username,
                reset_by="admin"  # Se puede mejorar para obtener el admin que lo hizo
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al resetear contraseña: {str(e)}"
        )


@router.post("/validate-user", response_model=UserStatusValidationResponse)
async def validate_user_status(
        validation_data: UserStatusValidationRequest,
        db: Session = Depends(get_db)
):
    """
    Validar estado actual del usuario
    """
    try:
        valid, message = auth.validate_user_status(db, user_id=validation_data.user_id)

        return UserStatusValidationResponse(
            valid=valid,
            message=message,
            user_id=validation_data.user_id,
            status_details=None  # Se puede expandir con más detalles
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar usuario: {str(e)}"
        )


@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_permission(
        permission_data: PermissionCheckRequest,
        db: Session = Depends(get_db)
):
    """
    Verificar si un tipo de usuario tiene un permiso específico
    """
    try:
        has_permission = auth.verify_permission(
            user_type=permission_data.user_type,
            permission=permission_data.permission
        )

        return PermissionCheckResponse(
            has_permission=has_permission,
            user_type=permission_data.user_type,
            permission=permission_data.permission,
            message="Permiso concedido" if has_permission else "Permiso denegado"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar permisos: {str(e)}"
        )


@router.get("/permissions/{user_type}", response_model=UserPermissionsResponse)
async def get_user_permissions(
        user_type: str,
        db: Session = Depends(get_db)
):
    """
    Obtener todos los permisos de un tipo de usuario
    """
    try:
        if user_type not in ['Administrador', 'Veterinario', 'Recepcionista']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de usuario inválido"
            )

        permisos = auth._get_user_permissions(user_type)
        permisos_activos = sum(1 for p in permisos.values() if p)

        return UserPermissionsResponse(
            user_type=user_type,
            permisos=permisos,
            total_permisos=len(permisos),
            permisos_activos=permisos_activos
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener permisos: {str(e)}"
        )


@router.get("/me/{user_id}")
async def get_current_user_profile(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener perfil completo del usuario actual
    """
    try:
        user_data = auth.get_user_by_id(db, user_id=user_id)

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        usuario = user_data["usuario"]
        perfil = user_data["perfil"]

        # Construir respuesta completa
        response = {
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "username": usuario.username,
                "tipo_usuario": usuario.tipo_usuario,
                "estado": usuario.estado,
                "fecha_creacion": usuario.fecha_creacion
            },
            "perfil": None,
            "permisos": user_data["permisos"]
        }

        if perfil:
            response["perfil"] = {
                "nombre": perfil.nombre,
                "apellido_paterno": perfil.apellido_paterno,
                "apellido_materno": perfil.apellido_materno,
                "dni": perfil.dni,
                "email": perfil.email,
                "telefono": perfil.telefono,
                "genero": perfil.genero
            }

            # Agregar campos específicos por tipo
            if usuario.tipo_usuario == "Veterinario":
                response["perfil"].update({
                    "codigo_cmvp": perfil.codigo_CMVP,
                    "id_especialidad": perfil.id_especialidad,
                    "tipo_veterinario": perfil.tipo_veterinario,
                    "disposicion": perfil.disposicion,
                    "turno": perfil.turno,
                    "fecha_nacimiento": perfil.fecha_nacimiento
                })
            elif usuario.tipo_usuario == "Recepcionista":
                response["perfil"].update({
                    "turno": perfil.turno,
                    "fecha_ingreso": perfil.fecha_ingreso
                })
            elif usuario.tipo_usuario == "Administrador":
                response["perfil"].update({
                    "fecha_ingreso": perfil.fecha_ingreso
                })

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener perfil: {str(e)}"
        )


@router.get("/health")
async def auth_health_check():
    """
    Verificar que el módulo de autenticación funciona
    """
    return {
        "status": "healthy",
        "module": "authentication",
        "endpoints": [
            "POST /login - Iniciar sesión",
            "POST /logout - Cerrar sesión",
            "GET /session/{user_id} - Info de sesión",
            "POST /change-password - Cambiar contraseña",
            "POST /reset-password - Resetear contraseña",
            "POST /validate-user - Validar usuario",
            "POST /check-permission - Verificar permisos",
            "GET /permissions/{user_type} - Obtener permisos",
            "GET /me/{user_id} - Perfil actual"
        ]
    }