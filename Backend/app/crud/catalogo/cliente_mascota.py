# app/crud/catalogo/cliente_mascota.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.cliente_mascota import ClienteMascota
from app.schemas.catalogo_schemas import ClienteMascotaCreate


# ===== CLIENTE_MASCOTA COMPLETO =====
class CRUDClienteMascota(CRUDBase[ClienteMascota, ClienteMascotaCreate, None]):

    def get_by_cliente(self, db: Session, *, cliente_id: int) -> List[ClienteMascota]:
        """Obtener todas las relaciones de un cliente"""
        return db.query(ClienteMascota).filter(ClienteMascota.id_cliente == cliente_id).all()

    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[ClienteMascota]:
        """Obtener todas las relaciones de una mascota"""
        return db.query(ClienteMascota).filter(ClienteMascota.id_mascota == mascota_id).all()

    def exists_relationship(self, db: Session, *, cliente_id: int, mascota_id: int) -> bool:
        """Verificar si existe la relación cliente-mascota"""
        return db.query(ClienteMascota).filter(
            and_(
                ClienteMascota.id_cliente == cliente_id,
                ClienteMascota.id_mascota == mascota_id
            )
        ).first() is not None

    def get_relationship(self, db: Session, *, cliente_id: int, mascota_id: int) -> Optional[ClienteMascota]:
        """Obtener relación específica cliente-mascota"""
        return db.query(ClienteMascota).filter(
            and_(
                ClienteMascota.id_cliente == cliente_id,
                ClienteMascota.id_mascota == mascota_id
            )
        ).first()

    def create_relationship(self, db: Session, *, cliente_id: int, mascota_id: int) -> Optional[ClienteMascota]:
        """Crear relación cliente-mascota si no existe"""
        if self.exists_relationship(db, cliente_id=cliente_id, mascota_id=mascota_id):
            return None

        relacion = ClienteMascota(
            id_cliente=cliente_id,
            id_mascota=mascota_id
        )
        db.add(relacion)
        db.commit()
        db.refresh(relacion)
        return relacion

    def remove_relationship(self, db: Session, *, cliente_id: int, mascota_id: int) -> bool:
        """Eliminar relación específica cliente-mascota"""
        relacion = self.get_relationship(db, cliente_id=cliente_id, mascota_id=mascota_id)
        if relacion:
            db.delete(relacion)
            db.commit()
            return True
        return False

    def get_mascotas_info_by_cliente(self, db: Session, *, cliente_id: int) -> List[Dict[str, Any]]:
        """Obtener información completa de mascotas de un cliente"""
        from app.models.mascota import Mascota
        from app.models.raza import Raza

        resultado = db.query(
            ClienteMascota.id_cliente_mascota,
            Mascota.id_mascota,
            Mascota.nombre,
            Mascota.sexo,
            Mascota.color,
            Mascota.edad_anios,
            Mascota.edad_meses,
            Mascota.esterilizado,
            Raza.nombre_raza
        ).join(Mascota, ClienteMascota.id_mascota == Mascota.id_mascota) \
            .outerjoin(Raza, Mascota.id_raza == Raza.id_raza) \
            .filter(ClienteMascota.id_cliente == cliente_id).all()

        return [
            {
                "id_cliente_mascota": r.id_cliente_mascota,
                "id_mascota": r.id_mascota,
                "nombre": r.nombre,
                "sexo": r.sexo,
                "color": r.color,
                "edad_anios": r.edad_anios,
                "edad_meses": r.edad_meses,
                "esterilizado": r.esterilizado,
                "raza": r.nombre_raza
            }
            for r in resultado
        ]

    def get_clientes_info_by_mascota(self, db: Session, *, mascota_id: int) -> List[Dict[str, Any]]:
        """Obtener información completa de clientes de una mascota"""
        from app.models.clientes import Cliente

        resultado = db.query(
            ClienteMascota.id_cliente_mascota,
            Cliente.id_cliente,
            Cliente.nombre,
            Cliente.apellido_paterno,
            Cliente.apellido_materno,
            Cliente.email,
            Cliente.telefono,
            Cliente.estado
        ).join(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente) \
            .filter(ClienteMascota.id_mascota == mascota_id).all()

        return [
            {
                "id_cliente_mascota": r.id_cliente_mascota,
                "id_cliente": r.id_cliente,
                "nombre_completo": f"{r.nombre} {r.apellido_paterno} {r.apellido_materno}",
                "email": r.email,
                "telefono": r.telefono,
                "estado": r.estado
            }
            for r in resultado
        ]

    def get_all_relationships_with_details(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[
        Dict[str, Any]]:
        """Obtener todas las relaciones con información detallada"""
        from app.models.clientes import Cliente
        from app.models.mascota import Mascota
        from app.models.raza import Raza

        resultado = db.query(
            ClienteMascota.id_cliente_mascota,
            ClienteMascota.id_cliente,
            ClienteMascota.id_mascota,
            Cliente.nombre.label('cliente_nombre'),
            Cliente.apellido_paterno,
            Cliente.email,
            Mascota.nombre.label('mascota_nombre'),
            Mascota.sexo,
            Raza.nombre_raza
        ).join(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente) \
            .join(Mascota, ClienteMascota.id_mascota == Mascota.id_mascota) \
            .outerjoin(Raza, Mascota.id_raza == Raza.id_raza) \
            .offset(skip).limit(limit).all()

        return [
            {
                "id_cliente_mascota": r.id_cliente_mascota,
                "id_cliente": r.id_cliente,
                "id_mascota": r.id_mascota,
                "cliente": f"{r.cliente_nombre} {r.apellido_paterno}",
                "cliente_email": r.email,
                "mascota": r.mascota_nombre,
                "mascota_sexo": r.sexo,
                "raza": r.nombre_raza
            }
            for r in resultado
        ]

    def transfer_mascota(self, db: Session, *, mascota_id: int, cliente_anterior_id: int,
                         cliente_nuevo_id: int) -> bool:
        """Transferir mascota de un cliente a otro"""
        # Verificar que existe la relación actual
        if not self.exists_relationship(db, cliente_id=cliente_anterior_id, mascota_id=mascota_id):
            return False

        # Verificar que no existe ya con el nuevo cliente
        if self.exists_relationship(db, cliente_id=cliente_nuevo_id, mascota_id=mascota_id):
            return False

        try:
            # Eliminar relación anterior
            self.remove_relationship(db, cliente_id=cliente_anterior_id, mascota_id=mascota_id)

            # Crear nueva relación
            self.create_relationship(db, cliente_id=cliente_nuevo_id, mascota_id=mascota_id)

            return True
        except Exception:
            db.rollback()
            return False

    def get_clientes_sin_mascotas(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener clientes que no tienen mascotas"""
        from app.models.clientes import Cliente

        resultado = db.query(Cliente) \
            .outerjoin(ClienteMascota, Cliente.id_cliente == ClienteMascota.id_cliente) \
            .filter(ClienteMascota.id_cliente_mascota.is_(None)).all()

        return [
            {
                "id_cliente": cliente.id_cliente,
                "nombre_completo": f"{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}",
                "email": cliente.email,
                "telefono": cliente.telefono
            }
            for cliente in resultado
        ]

    def get_mascotas_sin_cliente(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener mascotas que no tienen cliente asignado"""
        from app.models.mascota import Mascota
        from app.models.raza import Raza

        resultado = db.query(Mascota) \
            .outerjoin(ClienteMascota, Mascota.id_mascota == ClienteMascota.id_mascota) \
            .outerjoin(Raza, Mascota.id_raza == Raza.id_raza) \
            .filter(ClienteMascota.id_cliente_mascota.is_(None)).all()

        return [
            {
                "id_mascota": mascota.id_mascota,
                "nombre": mascota.nombre,
                "sexo": mascota.sexo,
                "edad_anios": mascota.edad_anios,
                "raza": mascota.raza.nombre_raza if mascota.raza else None
            }
            for mascota in resultado
        ]

    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de relaciones cliente-mascota"""
        from app.models.clientes import Cliente
        from app.models.mascota import Mascota

        total_relaciones = db.query(ClienteMascota).count()
        total_clientes = db.query(Cliente).count()
        total_mascotas = db.query(Mascota).count()

        clientes_con_mascotas = db.query(ClienteMascota.id_cliente).distinct().count()
        mascotas_con_cliente = db.query(ClienteMascota.id_mascota).distinct().count()

        # Cliente con más mascotas
        cliente_top = db.query(
            ClienteMascota.id_cliente,
            func.count(ClienteMascota.id_mascota).label('total_mascotas')
        ).group_by(ClienteMascota.id_cliente) \
            .order_by(func.count(ClienteMascota.id_mascota).desc()).first()

        promedio_mascotas = total_relaciones / clientes_con_mascotas if clientes_con_mascotas > 0 else 0

        return {
            "total_relaciones": total_relaciones,
            "total_clientes": total_clientes,
            "total_mascotas": total_mascotas,
            "clientes_con_mascotas": clientes_con_mascotas,
            "mascotas_con_cliente": mascotas_con_cliente,
            "clientes_sin_mascotas": total_clientes - clientes_con_mascotas,
            "mascotas_sin_cliente": total_mascotas - mascotas_con_cliente,
            "promedio_mascotas_por_cliente": round(promedio_mascotas, 2),
            "cliente_con_mas_mascotas": {
                "id_cliente": cliente_top.id_cliente,
                "total_mascotas": cliente_top.total_mascotas
            } if cliente_top else None
        }

    def bulk_assign_mascotas(self, db: Session, *, cliente_id: int, mascota_ids: List[int]) -> Tuple[int, List[str]]:
        """Asignar múltiples mascotas a un cliente"""
        asignadas = 0
        errores = []

        for mascota_id in mascota_ids:
            try:
                if self.create_relationship(db, cliente_id=cliente_id, mascota_id=mascota_id):
                    asignadas += 1
                else:
                    errores.append(f"Mascota {mascota_id} ya está asignada al cliente")
            except Exception as e:
                errores.append(f"Error con mascota {mascota_id}: {str(e)}")

        return asignadas, errores

    def remove_all_relationships_by_cliente(self, db: Session, *, cliente_id: int) -> int:
        """Eliminar todas las relaciones de un cliente"""
        relaciones = self.get_by_cliente(db, cliente_id=cliente_id)
        count = len(relaciones)

        for relacion in relaciones:
            db.delete(relacion)

        db.commit()
        return count

    def remove_all_relationships_by_mascota(self, db: Session, *, mascota_id: int) -> int:
        """Eliminar todas las relaciones de una mascota"""
        relaciones = self.get_by_mascota(db, mascota_id=mascota_id)
        count = len(relaciones)

        for relacion in relaciones:
            db.delete(relacion)

        db.commit()
        return count


# Instancia única


cliente_mascota = CRUDClienteMascota(ClienteMascota)
