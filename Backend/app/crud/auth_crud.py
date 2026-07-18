# app/crud/auth_crud.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Tuple
from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.veterinario import Veterinario
from app.models.recepcionista import Recepcionista
from app.config.security import hash_password, verify_password, is_hashed


class CRUDAuth:
    """CRUD para manejo de autenticación y sesiones"""
    
    def authenticate_user(self, db: Session, *, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuario y devolver información completa"""
        # Buscar usuario
        usuario = db.query(Usuario).filter(
            Usuario.username == username,
            Usuario.estado == "Activo"
        ).first()
        
        if not usuario or not verify_password(password, usuario.contraseña):
            return None

        # SC-046: migración perezosa — si la contraseña estaba en texto plano,
        # se re-hashea tras un login exitoso.
        if not is_hashed(usuario.contraseña):
            usuario.contraseña = hash_password(password)
            db.commit()

        # Obtener perfil según tipo de usuario
        perfil = self._get_user_profile(db, usuario)
        
        return {
            "usuario": usuario,
            "perfil": perfil,
            "tipo_usuario": usuario.tipo_usuario,
            "permisos": self._get_user_permissions(usuario.tipo_usuario)
        }
    
    def _get_user_profile(self, db: Session, usuario: Usuario) -> Optional[Any]:
        """Obtener perfil específico del usuario"""
        if usuario.tipo_usuario == "Administrador":
            return db.query(Administrador).filter(Administrador.id_usuario == usuario.id_usuario).first()
        elif usuario.tipo_usuario == "Veterinario":
            return db.query(Veterinario).filter(Veterinario.id_usuario == usuario.id_usuario).first()
        elif usuario.tipo_usuario == "Recepcionista":
            return db.query(Recepcionista).filter(Recepcionista.id_usuario == usuario.id_usuario).first()
        return None
    
    def _get_user_permissions(self, tipo_usuario: str) -> Dict[str, bool]:
        """Obtener permisos según tipo de usuario"""
        permissions = {
            "Administrador": {
                "ver_dashboard": True,
                "gestionar_usuarios": True,
                "gestionar_clientes": True,
                "gestionar_mascotas": True,
                "gestionar_veterinarios": True,
                "gestionar_recepcionistas": True,
                "ver_reportes": True,
                "gestionar_catalogos": True,
                "realizar_triaje": True,
                "realizar_consultas": True,
                "gestionar_citas": True,
                "ver_historial": True,
                "configurar_sistema": True
            },
            "Veterinario": {
                "ver_dashboard": True,
                "gestionar_usuarios": False,
                "gestionar_clientes": True,
                "gestionar_mascotas": True,
                "gestionar_veterinarios": False,
                "gestionar_recepcionistas": False,
                "ver_reportes": True,
                "gestionar_catalogos": False,
                "realizar_triaje": True,
                "realizar_consultas": True,
                "gestionar_citas": True,
                "ver_historial": True,
                "configurar_sistema": False
            },
            "Recepcionista": {
                "ver_dashboard": False,
                "gestionar_usuarios": False,
                "gestionar_clientes": True,
                "gestionar_mascotas": True,
                "gestionar_veterinarios": False,
                "gestionar_recepcionistas": False,
                "ver_reportes": False,
                "gestionar_catalogos": False,
                "realizar_triaje": False,
                "realizar_consultas": False,
                "gestionar_citas": True,
                "ver_historial": False,
                "configurar_sistema": False
            }
        }
        return permissions.get(tipo_usuario, {})
    
    def verify_permission(self, user_type: str, permission: str) -> bool:
        """Verificar si un tipo de usuario tiene un permiso específico"""
        permisos = self._get_user_permissions(user_type)
        return permisos.get(permission, False)
    
    def get_user_by_id(self, db: Session, *, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID con perfil completo"""
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if not usuario:
            return None
        
        perfil = self._get_user_profile(db, usuario)
        
        return {
            "usuario": usuario,
            "perfil": perfil,
            "tipo_usuario": usuario.tipo_usuario,
            "permisos": self._get_user_permissions(usuario.tipo_usuario)
        }
    
    def change_password(self, db: Session, *, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Cambiar contraseña validando la actual"""
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        
        if not usuario:
            return False, "Usuario no encontrado"
        
        if not verify_password(current_password, usuario.contraseña):
            return False, "Contraseña actual incorrecta"
        
        if len(new_password) < 3:
            return False, "La nueva contraseña debe tener al menos 3 caracteres"
        
        usuario.contraseña = hash_password(new_password)
        db.commit()
        
        return True, "Contraseña cambiada exitosamente"
    
    def reset_password(self, db: Session, *, username: str, new_password: str) -> Tuple[bool, str]:
        """Resetear contraseña (solo para administradores)"""
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        
        if not usuario:
            return False, "Usuario no encontrado"
        
        if len(new_password) < 3:
            return False, "La contraseña debe tener al menos 3 caracteres"
        
        usuario.contraseña = hash_password(new_password)
        db.commit()
        
        return True, "Contraseña reseteada exitosamente"
    
    def validate_user_status(self, db: Session, *, user_id: int) -> Tuple[bool, str]:
        """Validar estado del usuario"""
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        
        if not usuario:
            return False, "Usuario no encontrado"
        
        if usuario.estado == "Inactivo":
            return False, "Usuario inactivo"
        
        # Aquí podrías agregar validaciones adicionales como bloqueos temporales
        
        return True, "Usuario válido"
    
    def get_user_session_info(self, db: Session, *, user_id: int) -> Dict[str, Any]:
        """Obtener información de sesión del usuario"""
        user_data = self.get_user_by_id(db, user_id=user_id)
        if not user_data:
            return {}
        
        usuario = user_data["usuario"]
        perfil = user_data["perfil"]
        
        session_info = {
            "user_id": usuario.id_usuario,
            "username": usuario.username,
            "tipo_usuario": usuario.tipo_usuario,
            "estado": usuario.estado,
            "permisos": user_data["permisos"]
        }
        
        # Agregar información del perfil
        if perfil:
            session_info.update({
                "nombre_completo": f"{perfil.nombre} {perfil.apellido_paterno} {perfil.apellido_materno}",
                "email": perfil.email,
                "dni": perfil.dni
            })
            
            # Información específica por tipo
            if usuario.tipo_usuario == "Veterinario":
                session_info.update({
                    "codigo_cmvp": perfil.codigo_CMVP,
                    "especialidad_id": perfil.id_especialidad,
                    "disposicion": perfil.disposicion,
                    "turno": perfil.turno
                })
            elif usuario.tipo_usuario == "Recepcionista":
                session_info.update({
                    "turno": perfil.turno
                })
        
        return session_info
    
    def logout_user(self, db: Session, *, user_id: int) -> bool:
        """Cerrar sesión del usuario (implementar con tabla de sesiones)"""
        # Aquí implementarías lógica para invalidar tokens/sesiones
        return True


# Instancia única
auth = CRUDAuth()