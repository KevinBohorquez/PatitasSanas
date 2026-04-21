# app/crud/administrador_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.administrador import Administrador
from app.models.usuario import Usuario
from app.schemas.administrador_schema import AdministradorCreate, AdministradorUpdate, AdministradorSearch


class CRUDAdministrador(CRUDBase[Administrador, AdministradorCreate, AdministradorUpdate]):

    def get(self, db: Session, id: Any) -> Optional[Administrador]:
        """Obtener administrador por ID - override para especificar campo correcto"""
        return db.query(Administrador).filter(Administrador.id_administrador == id).first()

    def get_by_dni(self, db: Session, *, dni: str) -> Optional[Administrador]:
        """Obtener administrador por DNI"""
        return db.query(Administrador).filter(Administrador.dni == dni).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Administrador]:
        """Obtener administrador por email"""
        return db.query(Administrador).filter(Administrador.email == email).first()

    def get_by_usuario_id(self, db: Session, *, id_usuario: int) -> Optional[Administrador]:
        """Obtener administrador por ID de usuario"""
        return db.query(Administrador).filter(Administrador.id_usuario == id_usuario).first()

    def create_complete(self, db: Session, *, admin_data: AdministradorCreate) -> Administrador:
        """Crear administrador con usuario"""
        from app.crud.usuario_crud import usuario as usuario_crud

        # Preparar datos de usuario
        user_data = {
            "username": admin_data.username,
            "contraseña": admin_data.contraseña,
            "estado": "Activo"
        }

        # Preparar datos de perfil
        profile_data = admin_data.dict(exclude={"username", "contraseña"})

        # Crear usuario con perfil
        usuario_obj = usuario_crud.create_with_profile(
            db,
            user_data=user_data,
            profile_data=profile_data,
            user_type="Administrador"
        )

        # Retornar el administrador creado
        return self.get_by_usuario_id(db, id_usuario=usuario_obj.id_usuario)

    def get_with_usuario(self, db: Session, *, admin_id: int) -> Optional[Dict[str, Any]]:
        """Obtener administrador con información de usuario"""
        admin = self.get(db, admin_id)
        if not admin:
            return None

        usuario_obj = db.query(Usuario).filter(Usuario.id_usuario == admin.id_usuario).first()

        return {
            "administrador": admin,
            "usuario": usuario_obj
        }

    def search_administradores(self, db: Session, *, search_params: AdministradorSearch) -> Tuple[
        List[Administrador], int]:
        """Buscar administradores con filtros múltiples"""
        query = db.query(Administrador)

        # Aplicar filtros
        if search_params.nombre:
            nombre_filter = f"%{search_params.nombre}%"
            query = query.filter(
                or_(
                    Administrador.nombre.ilike(nombre_filter),
                    Administrador.apellido_paterno.ilike(nombre_filter),
                    Administrador.apellido_materno.ilike(nombre_filter)
                )
            )

        if search_params.dni:
            query = query.filter(Administrador.dni == search_params.dni)

        if search_params.email:
            query = query.filter(Administrador.email.ilike(f"%{search_params.email}%"))

        if search_params.genero:
            query = query.filter(Administrador.genero == search_params.genero)

        if search_params.fecha_ingreso_desde:
            query = query.filter(Administrador.fecha_ingreso >= search_params.fecha_ingreso_desde)

        if search_params.fecha_ingreso_hasta:
            query = query.filter(Administrador.fecha_ingreso <= search_params.fecha_ingreso_hasta)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenamiento
        administradores = query.order_by(Administrador.fecha_ingreso.desc()) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return administradores, total

    def exists_by_dni(self, db: Session, *, dni: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un administrador con ese DNI"""
        query = db.query(Administrador).filter(Administrador.dni == dni)
        if exclude_id:
            query = query.filter(Administrador.id_administrador != exclude_id)
        return query.first() is not None

    def exists_by_email(self, db: Session, *, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un administrador con ese email"""
        query = db.query(Administrador).filter(Administrador.email == email)
        if exclude_id:
            query = query.filter(Administrador.id_administrador != exclude_id)
        return query.first() is not None

    def get_all_with_usuario_info(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener administradores con información de usuario"""
        administradores = db.query(Administrador).offset(skip).limit(limit).all()

        result = []
        for admin in administradores:
            usuario_obj = db.query(Usuario).filter(Usuario.id_usuario == admin.id_usuario).first()
            result.append({
                "id_administrador": admin.id_administrador,
                "nombre_completo": f"{admin.nombre} {admin.apellido_paterno} {admin.apellido_materno}",
                "dni": admin.dni,
                "email": admin.email,
                "telefono": admin.telefono,
                "fecha_ingreso": admin.fecha_ingreso,
                "genero": admin.genero,
                "usuario": {
                    "id_usuario": usuario_obj.id_usuario if usuario_obj else None,
                    "username": usuario_obj.username if usuario_obj else None,
                    "estado": usuario_obj.estado if usuario_obj else None,
                    "fecha_creacion": usuario_obj.fecha_creacion if usuario_obj else None
                }
            })

        return result

    def get_administradores_activos(self, db: Session) -> List[Administrador]:
        """Obtener administradores con usuarios activos"""
        return db.query(Administrador).join(Usuario, Administrador.id_usuario == Usuario.id_usuario) \
            .filter(Usuario.estado == "Activo").all()

    def get_by_genero(self, db: Session, *, genero: str) -> List[Administrador]:
        """Obtener administradores por género"""
        return db.query(Administrador).filter(Administrador.genero == genero).all()

    def get_recientes(self, db: Session, *, dias: int = 30, limit: int = 10) -> List[Administrador]:
        """Obtener administradores ingresados recientemente"""
        from datetime import date, timedelta
        fecha_limite = date.today() - timedelta(days=dias)

        return db.query(Administrador).filter(Administrador.fecha_ingreso >= fecha_limite) \
            .order_by(Administrador.fecha_ingreso.desc()) \
            .limit(limit).all()

    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de administradores"""
        total_admins = db.query(Administrador).count()

        # Por género
        masculinos = db.query(Administrador).filter(Administrador.genero == 'M').count()
        femeninos = db.query(Administrador).filter(Administrador.genero == 'F').count()

        # Con usuario activo
        activos = db.query(Administrador).join(Usuario, Administrador.id_usuario == Usuario.id_usuario) \
            .filter(Usuario.estado == "Activo").count()

        # Por año de ingreso
        from sqlalchemy import extract, func
        por_año = db.query(
            extract('year', Administrador.fecha_ingreso).label('año'),
            func.count(Administrador.id_administrador).label('total')
        ).group_by(extract('year', Administrador.fecha_ingreso)).all()

        return {
            "total_administradores": total_admins,
            "activos": activos,
            "inactivos": total_admins - activos,
            "por_genero": {
                "masculinos": masculinos,
                "femeninos": femeninos
            },
            "por_año_ingreso": [
                {"año": int(r.año), "total": r.total} for r in por_año
            ],
            "porcentaje_activos": round((activos / total_admins * 100), 2) if total_admins > 0 else 0
        }

    def update_profile(self, db: Session, *, admin_id: int, profile_data: AdministradorUpdate) -> Optional[
        Administrador]:
        """Actualizar perfil de administrador"""
        admin = self.get(db, admin_id)
        if not admin:
            return None

        # Validar duplicados si se están actualizando
        update_data = profile_data.dict(exclude_unset=True)

        if "dni" in update_data:
            if self.exists_by_dni(db, dni=update_data["dni"], exclude_id=admin_id):
                raise ValueError("Ya existe un administrador con ese DNI")

        if "email" in update_data:
            if self.exists_by_email(db, email=update_data["email"], exclude_id=admin_id):
                raise ValueError("Ya existe un administrador con ese email")

        return self.update(db, db_obj=admin, obj_in=profile_data)

    def activate_user_account(self, db: Session, *, admin_id: int) -> bool:
        """Activar cuenta de usuario del administrador"""
        admin = self.get(db, admin_id)
        if not admin:
            return False

        from app.crud.usuario_crud import usuario as usuario_crud
        usuario_obj = usuario_crud.activate_user(db, user_id=admin.id_usuario)
        return usuario_obj is not None

    def deactivate_user_account(self, db: Session, *, admin_id: int) -> bool:
        """Desactivar cuenta de usuario del administrador"""
        admin = self.get(db, admin_id)
        if not admin:
            return False

        from app.crud.usuario_crud import usuario as usuario_crud
        usuario_obj = usuario_crud.deactivate_user(db, user_id=admin.id_usuario)
        return usuario_obj is not None

    def change_user_password(self, db: Session, *, admin_id: int, new_password: str) -> bool:
        """Cambiar contraseña del usuario administrador"""
        admin = self.get(db, admin_id)
        if not admin:
            return False

        from app.crud.usuario_crud import usuario as usuario_crud
        usuario_obj = usuario_crud.change_password(db, user_id=admin.id_usuario, new_password=new_password)
        return usuario_obj is not None


# Instancia única
administrador = CRUDAdministrador(Administrador)