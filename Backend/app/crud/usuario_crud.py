# app/crud/usuario_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.veterinario import Veterinario
from app.models.recepcionista import Recepcionista
from app.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioSearch


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):

    def get(self, db: Session, id: Any) -> Optional[Usuario]:
        """Obtener usuario por ID - override para especificar campo correcto"""
        return db.query(Usuario).filter(Usuario.id_usuario == id).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[Usuario]:
        """Obtener usuario por username"""
        return db.query(Usuario).filter(Usuario.username == username).first()

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[Usuario]:
        """Autenticar usuario (sin hash por simplicidad)"""
        usuario = self.get_by_username(db, username=username)
        if usuario and usuario.contraseña == password and usuario.estado == "Activo":
            return usuario
        return None

    def create_with_profile(self, db: Session, *, user_data: Dict[str, Any], profile_data: Dict[str, Any],
                            user_type: str) -> Usuario:
        """Crear usuario con perfil específico"""
        # Crear usuario base
        usuario_dict = {
            "username": user_data["username"],
            "contraseña": user_data["contraseña"],
            "tipo_usuario": user_type,
            "estado": user_data.get("estado", "Activo")
        }

        usuario = Usuario(**usuario_dict)
        db.add(usuario)
        db.flush()  # Para obtener el ID sin commit

        # Crear perfil específico según tipo
        try:
            if user_type == "Administrador":
                profile_data["id_usuario"] = usuario.id_usuario
                admin = Administrador(**profile_data)
                db.add(admin)

            elif user_type == "Veterinario":
                profile_data["id_usuario"] = usuario.id_usuario
                veterinario = Veterinario(**profile_data)
                db.add(veterinario)

            elif user_type == "Recepcionista":
                profile_data["id_usuario"] = usuario.id_usuario
                recepcionista = Recepcionista(**profile_data)
                db.add(recepcionista)

            db.commit()
            db.refresh(usuario)
            return usuario

        except Exception as e:
            db.rollback()
            raise e

    def get_with_profile(self, db: Session, *, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtener usuario con su perfil específico"""
        usuario = self.get(db, user_id)
        if not usuario:
            return None

        profile = None
        if usuario.tipo_usuario == "Administrador":
            profile = db.query(Administrador).filter(Administrador.id_usuario == user_id).first()
        elif usuario.tipo_usuario == "Veterinario":
            profile = db.query(Veterinario).filter(Veterinario.id_usuario == user_id).first()
        elif usuario.tipo_usuario == "Recepcionista":
            profile = db.query(Recepcionista).filter(Recepcionista.id_usuario == user_id).first()

        return {
            "usuario": usuario,
            "perfil": profile
        }

    def search_usuarios(self, db: Session, *, search_params: UsuarioSearch) -> Tuple[List[Usuario], int]:
        """Buscar usuarios con filtros múltiples"""
        query = db.query(Usuario)

        # Aplicar filtros
        if search_params.username:
            query = query.filter(Usuario.username.ilike(f"%{search_params.username}%"))

        if search_params.tipo_usuario:
            query = query.filter(Usuario.tipo_usuario == search_params.tipo_usuario)

        if search_params.estado:
            query = query.filter(Usuario.estado == search_params.estado)

        if search_params.fecha_desde:
            query = query.filter(Usuario.fecha_creacion >= search_params.fecha_desde)

        if search_params.fecha_hasta:
            query = query.filter(Usuario.fecha_creacion <= search_params.fecha_hasta)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenamiento
        usuarios = query.order_by(Usuario.fecha_creacion.desc()) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return usuarios, total

    def exists_by_username(self, db: Session, *, username: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un usuario con ese username"""
        query = db.query(Usuario).filter(Usuario.username == username)
        if exclude_id:
            query = query.filter(Usuario.id_usuario != exclude_id)
        return query.first() is not None

    def change_password(self, db: Session, *, user_id: int, new_password: str) -> Optional[Usuario]:
        """Cambiar contraseña de usuario"""
        usuario = self.get(db, user_id)
        if usuario:
            usuario.contraseña = new_password
            db.commit()
            db.refresh(usuario)
        return usuario

    def activate_user(self, db: Session, *, user_id: int) -> Optional[Usuario]:
        """Activar usuario"""
        usuario = self.get(db, user_id)
        if usuario:
            usuario.estado = "Activo"
            db.commit()
            db.refresh(usuario)
        return usuario

    def deactivate_user(self, db: Session, *, user_id: int) -> Optional[Usuario]:
        """Desactivar usuario"""
        usuario = self.get(db, user_id)
        if usuario:
            usuario.estado = "Inactivo"
            db.commit()
            db.refresh(usuario)
        return usuario

    def get_by_tipo(self, db: Session, *, tipo_usuario: str, activos_solo: bool = True) -> List[Usuario]:
        """Obtener usuarios por tipo"""
        query = db.query(Usuario).filter(Usuario.tipo_usuario == tipo_usuario)
        if activos_solo:
            query = query.filter(Usuario.estado == "Activo")
        return query.all()

    def get_usuarios_con_perfiles(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener usuarios con información de sus perfiles"""
        usuarios = db.query(Usuario).offset(skip).limit(limit).all()

        result = []
        for usuario in usuarios:
            perfil_info = self.get_with_profile(db, user_id=usuario.id_usuario)
            if perfil_info and perfil_info["perfil"]:
                perfil = perfil_info["perfil"]
                result.append({
                    "id_usuario": usuario.id_usuario,
                    "username": usuario.username,
                    "tipo_usuario": usuario.tipo_usuario,
                    "estado": usuario.estado,
                    "fecha_creacion": usuario.fecha_creacion,
                    "nombre_completo": f"{perfil.nombre} {perfil.apellido_paterno} {perfil.apellido_materno}",
                    "email": perfil.email,
                    "dni": perfil.dni
                })
            else:
                result.append({
                    "id_usuario": usuario.id_usuario,
                    "username": usuario.username,
                    "tipo_usuario": usuario.tipo_usuario,
                    "estado": usuario.estado,
                    "fecha_creacion": usuario.fecha_creacion,
                    "nombre_completo": "Sin perfil",
                    "email": "Sin email",
                    "dni": "Sin DNI"
                })

        return result

    def get_estadisticas_usuarios(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de usuarios"""
        total_usuarios = db.query(Usuario).count()
        usuarios_activos = db.query(Usuario).filter(Usuario.estado == "Activo").count()
        usuarios_inactivos = total_usuarios - usuarios_activos

        # Por tipo
        administradores = db.query(Usuario).filter(Usuario.tipo_usuario == "Administrador").count()
        veterinarios = db.query(Usuario).filter(Usuario.tipo_usuario == "Veterinario").count()
        recepcionistas = db.query(Usuario).filter(Usuario.tipo_usuario == "Recepcionista").count()

        # Activos por tipo
        admin_activos = db.query(Usuario).filter(
            and_(Usuario.tipo_usuario == "Administrador", Usuario.estado == "Activo")
        ).count()
        vet_activos = db.query(Usuario).filter(
            and_(Usuario.tipo_usuario == "Veterinario", Usuario.estado == "Activo")
        ).count()
        recep_activos = db.query(Usuario).filter(
            and_(Usuario.tipo_usuario == "Recepcionista", Usuario.estado == "Activo")
        ).count()

        return {
            "total_usuarios": total_usuarios,
            "usuarios_activos": usuarios_activos,
            "usuarios_inactivos": usuarios_inactivos,
            "porcentaje_activos": round((usuarios_activos / total_usuarios * 100), 2) if total_usuarios > 0 else 0,
            "por_tipo": {
                "administradores": {
                    "total": administradores,
                    "activos": admin_activos,
                    "inactivos": administradores - admin_activos
                },
                "veterinarios": {
                    "total": veterinarios,
                    "activos": vet_activos,
                    "inactivos": veterinarios - vet_activos
                },
                "recepcionistas": {
                    "total": recepcionistas,
                    "activos": recep_activos,
                    "inactivos": recepcionistas - recep_activos
                }
            }
        }

    def delete_user_complete(self, db: Session, *, user_id: int) -> bool:
        """Eliminar usuario y su perfil completamente"""
        usuario = self.get(db, user_id)
        if not usuario:
            return False

        try:
            # El CASCADE en las FK debería eliminar el perfil automáticamente
            db.delete(usuario)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    def get_usuarios_recientes(self, db: Session, *, dias: int = 7, limit: int = 10) -> List[Usuario]:
        """Obtener usuarios creados recientemente"""
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() - timedelta(days=dias)

        return db.query(Usuario).filter(Usuario.fecha_creacion >= fecha_limite) \
            .order_by(Usuario.fecha_creacion.desc()) \
            .limit(limit).all()


# Instancia única
usuario = CRUDUsuario(Usuario)