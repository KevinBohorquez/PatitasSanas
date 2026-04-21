# app/crud/clientes_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from app.crud.base_crud import CRUDBase
from app.models.clientes import Cliente
from app.schemas.clientes_schema import ClienteCreate, ClienteUpdate, ClienteSearch

class CRUDCliente(CRUDBase[Cliente, ClienteCreate, ClienteUpdate]):

    def get_by_dni(self, db: Session, *, dni: str) -> Optional[Cliente]:
        """Obtener cliente por DNI"""
        return db.query(Cliente).filter(Cliente.dni == dni).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Cliente]:
        """Obtener cliente por email"""
        return db.query(Cliente).filter(Cliente.email == email).first()

    def search_clientes(self, db: Session, *, search_params: ClienteSearch) -> Tuple[List[Cliente], int]:
        """Buscar clientes con filtros múltiples"""
        query = db.query(Cliente)

        # Aplicar filtros
        if search_params.nombre:
            nombre_filter = f"%{search_params.nombre}%"
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(nombre_filter),
                    Cliente.apellido_paterno.ilike(nombre_filter),
                    Cliente.apellido_materno.ilike(nombre_filter)
                )
            )

        if search_params.dni:
            query = query.filter(Cliente.dni == search_params.dni)

        if search_params.email:
            query = query.filter(Cliente.email.ilike(f"%{search_params.email}%"))

        if search_params.estado:
            query = query.filter(Cliente.estado == search_params.estado)

        # Filtro por género
        if search_params.genero:
            query = query.filter(Cliente.genero == search_params.genero)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenamiento
        clientes = query.order_by(Cliente.fecha_registro.desc())\
                       .offset((search_params.page - 1) * search_params.per_page)\
                       .limit(search_params.per_page).all()

        return clientes, total

    def exists_by_dni(self, db: Session, *, dni: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un cliente con ese DNI"""
        query = db.query(Cliente).filter(Cliente.dni == dni)
        if exclude_id:
            query = query.filter(Cliente.id_cliente != exclude_id)
        return query.first() is not None

    def exists_by_email(self, db: Session, *, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un cliente con ese email"""
        query = db.query(Cliente).filter(Cliente.email == email)
        if exclude_id:
            query = query.filter(Cliente.id_cliente != exclude_id)
        return query.first() is not None

    def get_clientes_with_mascotas_count(self, db: Session) -> List[dict]:
        """Obtener clientes con conteo de mascotas"""
        from app.models.mascota import Mascota
        return db.query(
            Cliente.id_cliente,
            Cliente.nombre,
            Cliente.apellido_paterno,
            Cliente.email,
            Cliente.genero,  # Incluir género en la consulta
            db.func.count(Mascota.id_mascota).label('total_mascotas')
        ).outerjoin(Mascota).group_by(Cliente.id_cliente).all()

    def get_clientes_by_genero(self, db: Session, *, genero: str) -> List[Cliente]:
        """Obtener clientes filtrados por género"""
        return db.query(Cliente).filter(Cliente.genero == genero).all()

    def get_estadisticas_por_genero(self, db: Session) -> dict:
        """Obtener estadísticas de clientes por género"""
        from sqlalchemy import func

        result = db.query(
            Cliente.genero,
            func.count(Cliente.id_cliente).label('total')
        ).group_by(Cliente.genero).all()

        estadisticas = {
            'F': 0,
            'M': 0,
            'total': 0
        }

        for row in result:
            estadisticas[row.genero] = row.total
            estadisticas['total'] += row.total

        return estadisticas

# Instancia única
cliente = CRUDCliente(Cliente)