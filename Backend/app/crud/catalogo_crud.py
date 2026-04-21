# app/crud/catalogo_crud.py (VERSIÓN COMPLETA)
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple, Dict, Any
from app.crud.base_crud import CRUDBase
from app.models.cliente_mascota import ClienteMascota
from app.models.raza import Raza
from app.models.tipo_animal import TipoAnimal
from app.models.especialidad import Especialidad
from app.models.tipo_servicio import TipoServicio
from app.models.servicio import Servicio
from app.models.patologia import Patologia
from app.schemas.catalogo_schemas import (
    RazaCreate, TipoAnimalCreate, EspecialidadCreate,
    TipoServicioCreate, ServicioCreate, ServicioUpdate, PatologiaCreate, ClienteMascotaCreate
)

# ===== RAZA COMPLETO =====
class CRUDRaza(CRUDBase[Raza, RazaCreate, None]):
    
    def get_by_nombre(self, db: Session, *, nombre_raza: str) -> Optional[Raza]:
        """Obtener raza por nombre exacto"""
        return db.query(Raza).filter(Raza.nombre_raza == nombre_raza).first()

    def search_razas(self, db: Session, *, nombre: str) -> List[Raza]:
        """Buscar razas por nombre (parcial)"""
        return db.query(Raza).filter(Raza.nombre_raza.ilike(f"%{nombre}%"))\
                             .order_by(Raza.nombre_raza).all()

    def exists_by_nombre(self, db: Session, *, nombre_raza: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una raza con ese nombre"""
        query = db.query(Raza).filter(Raza.nombre_raza == nombre_raza)
        if exclude_id:
            query = query.filter(Raza.id_raza != exclude_id)
        return query.first() is not None

    def get_razas_con_mascotas_count(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener razas con conteo de mascotas"""
        from app.models.mascota import Mascota
        
        resultado = db.query(
            Raza.id_raza,
            Raza.nombre_raza,
            func.count(Mascota.id_mascota).label('total_mascotas')
        ).outerjoin(Mascota, Raza.id_raza == Mascota.id_raza)\
         .group_by(Raza.id_raza, Raza.nombre_raza)\
         .order_by(Raza.nombre_raza).all()
        
        return [
            {
                "id_raza": r.id_raza,
                "nombre_raza": r.nombre_raza,
                "total_mascotas": r.total_mascotas or 0
            }
            for r in resultado
        ]

    def get_razas_populares(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener razas más populares por número de mascotas"""
        from app.models.mascota import Mascota
        
        resultado = db.query(
            Raza.id_raza,
            Raza.nombre_raza,
            func.count(Mascota.id_mascota).label('total_mascotas')
        ).join(Mascota, Raza.id_raza == Mascota.id_raza)\
         .group_by(Raza.id_raza, Raza.nombre_raza)\
         .order_by(func.count(Mascota.id_mascota).desc())\
         .limit(limit).all()
        
        return [
            {
                "id_raza": r.id_raza,
                "nombre_raza": r.nombre_raza,
                "total_mascotas": r.total_mascotas
            }
            for r in resultado
        ]

    def get_all_ordenadas(self, db: Session) -> List[Raza]:
        """Obtener todas las razas ordenadas alfabéticamente"""
        return db.query(Raza).order_by(Raza.nombre_raza).all()

# ===== TIPO ANIMAL COMPLETO =====
class CRUDTipoAnimal(CRUDBase[TipoAnimal, TipoAnimalCreate, None]):
    
    def get_by_raza(self, db: Session, *, raza_id: int) -> List[TipoAnimal]:
        """Obtener tipos de animal por raza"""
        return db.query(TipoAnimal).filter(TipoAnimal.id_raza == raza_id).all()

    def get_by_descripcion(self, db: Session, *, descripcion: str) -> List[TipoAnimal]:
        """Obtener tipos de animal por descripción (Perro/Gato)"""
        return db.query(TipoAnimal).filter(TipoAnimal.descripcion == descripcion).all()

    def get_with_raza_info(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener tipos de animal con información de raza"""
        resultado = db.query(
            TipoAnimal.id_tipo_animal,
            TipoAnimal.id_raza,
            TipoAnimal.descripcion,
            Raza.nombre_raza
        ).join(Raza, TipoAnimal.id_raza == Raza.id_raza)\
         .order_by(TipoAnimal.descripcion, Raza.nombre_raza).all()
        
        return [
            {
                "id_tipo_animal": r.id_tipo_animal,
                "id_raza": r.id_raza,
                "descripcion": r.descripcion,
                "nombre_raza": r.nombre_raza
            }
            for r in resultado
        ]

    def exists_combination(self, db: Session, *, raza_id: int, descripcion: str) -> bool:
        """Verificar si existe la combinación raza-descripción"""
        return db.query(TipoAnimal).filter(
            and_(
                TipoAnimal.id_raza == raza_id,
                TipoAnimal.descripcion == descripcion
            )
        ).first() is not None

    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de tipos de animal"""
        total = db.query(TipoAnimal).count()
        perros = db.query(TipoAnimal).filter(TipoAnimal.descripcion == "Perro").count()
        gatos = db.query(TipoAnimal).filter(TipoAnimal.descripcion == "Gato").count()
        
        return {
            "total_tipos": total,
            "perros": perros,
            "gatos": gatos,
            "razas_perros": perros,
            "razas_gatos": gatos
        }

# ===== ESPECIALIDAD COMPLETO =====
class CRUDEspecialidad(CRUDBase[Especialidad, EspecialidadCreate, None]):
    
    def get_by_descripcion(self, db: Session, *, descripcion: str) -> Optional[Especialidad]:
        """Obtener especialidad por descripción exacta"""
        return db.query(Especialidad).filter(Especialidad.descripcion == descripcion).first()

    def search_especialidades(self, db: Session, *, descripcion: str) -> List[Especialidad]:
        """Buscar especialidades por descripción (parcial)"""
        return db.query(Especialidad).filter(Especialidad.descripcion.ilike(f"%{descripcion}%"))\
                                    .order_by(Especialidad.descripcion).all()

    def exists_by_descripcion(self, db: Session, *, descripcion: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una especialidad con esa descripción"""
        query = db.query(Especialidad).filter(Especialidad.descripcion == descripcion)
        if exclude_id:
            query = query.filter(Especialidad.id_especialidad != exclude_id)
        return query.first() is not None

    def get_especialidades_con_veterinarios_count(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener especialidades con conteo de veterinarios"""
        from app.models.veterinario import Veterinario
        
        resultado = db.query(
            Especialidad.id_especialidad,
            Especialidad.descripcion,
            func.count(Veterinario.id_veterinario).label('total_veterinarios'),
            func.sum(
                func.case(
                    [(Veterinario.disposicion == 'Libre', 1)], 
                    else_=0
                )
            ).label('veterinarios_disponibles')
        ).outerjoin(Veterinario, Especialidad.id_especialidad == Veterinario.id_especialidad)\
         .group_by(Especialidad.id_especialidad, Especialidad.descripcion)\
         .order_by(Especialidad.descripcion).all()
        
        return [
            {
                "id_especialidad": r.id_especialidad,
                "descripcion": r.descripcion,
                "total_veterinarios": r.total_veterinarios or 0,
                "veterinarios_disponibles": r.veterinarios_disponibles or 0
            }
            for r in resultado
        ]

    def get_mas_demandadas(self, db: Session, *, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener especialidades más demandadas"""
        from app.models.veterinario import Veterinario
        from app.models.consulta import Consulta
        
        resultado = db.query(
            Especialidad.descripcion,
            func.count(Consulta.id_consulta).label('total_consultas')
        ).join(Veterinario, Especialidad.id_especialidad == Veterinario.id_especialidad)\
         .join(Consulta, Veterinario.id_veterinario == Consulta.id_veterinario)\
         .group_by(Especialidad.id_especialidad, Especialidad.descripcion)\
         .order_by(func.count(Consulta.id_consulta).desc())\
         .limit(limit).all()
        
        return [
            {
                "especialidad": r.descripcion,
                "total_consultas": r.total_consultas
            }
            for r in resultado
        ]

    def get_all_ordenadas(self, db: Session) -> List[Especialidad]:
        """Obtener todas las especialidades ordenadas alfabéticamente"""
        return db.query(Especialidad).order_by(Especialidad.descripcion).all()

# ===== TIPO SERVICIO COMPLETO =====
class CRUDTipoServicio(CRUDBase[TipoServicio, TipoServicioCreate, None]):
    
    def get_by_descripcion(self, db: Session, *, descripcion: str) -> Optional[TipoServicio]:
        """Obtener tipo de servicio por descripción exacta"""
        return db.query(TipoServicio).filter(TipoServicio.descripcion == descripcion).first()

    def exists_by_descripcion(self, db: Session, *, descripcion: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un tipo de servicio con esa descripción"""
        query = db.query(TipoServicio).filter(TipoServicio.descripcion == descripcion)
        if exclude_id:
            query = query.filter(TipoServicio.id_tipo_servicio != exclude_id)
        return query.first() is not None

    def get_tipos_con_servicios_count(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener tipos de servicio con conteo de servicios"""
        resultado = db.query(
            TipoServicio.id_tipo_servicio,
            TipoServicio.descripcion,
            func.count(Servicio.id_servicio).label('total_servicios'),
            func.sum(
                func.case(
                    [(Servicio.activo == True, 1)], 
                    else_=0
                )
            ).label('servicios_activos')
        ).outerjoin(Servicio, TipoServicio.id_tipo_servicio == Servicio.id_tipo_servicio)\
         .group_by(TipoServicio.id_tipo_servicio, TipoServicio.descripcion)\
         .order_by(TipoServicio.descripcion).all()
        
        return [
            {
                "id_tipo_servicio": r.id_tipo_servicio,
                "descripcion": r.descripcion,
                "total_servicios": r.total_servicios or 0,
                "servicios_activos": r.servicios_activos or 0
            }
            for r in resultado
        ]

    def search_tipos(self, db: Session, *, descripcion: str) -> List[TipoServicio]:
        """Buscar tipos de servicio por descripción"""
        return db.query(TipoServicio).filter(TipoServicio.descripcion.ilike(f"%{descripcion}%"))\
                                    .order_by(TipoServicio.descripcion).all()

    def get_all_ordenados(self, db: Session) -> List[TipoServicio]:
        """Obtener todos los tipos ordenados alfabéticamente"""
        return db.query(TipoServicio).order_by(TipoServicio.descripcion).all()

# ===== SERVICIO COMPLETO =====
class CRUDServicio(CRUDBase[Servicio, ServicioCreate, ServicioUpdate]):
    
    def get_by_tipo(self, db: Session, *, tipo_servicio_id: int, solo_activos: bool = True) -> List[Servicio]:
        """Obtener servicios por tipo"""
        query = db.query(Servicio).filter(Servicio.id_tipo_servicio == tipo_servicio_id)
        if solo_activos:
            query = query.filter(Servicio.activo == True)
        return query.order_by(Servicio.nombre_servicio).all()

    def get_activos(self, db: Session) -> List[Servicio]:
        """Obtener servicios activos"""
        return db.query(Servicio).filter(Servicio.activo == True)\
                                 .order_by(Servicio.nombre_servicio).all()

    def get_by_nombre(self, db: Session, *, nombre_servicio: str) -> Optional[Servicio]:
        """Obtener servicio por nombre exacto"""
        return db.query(Servicio).filter(Servicio.nombre_servicio == nombre_servicio).first()

    def search_servicios(self, db: Session, *, nombre: str = None, activo: bool = None, tipo_servicio_id: int = None) -> List[Servicio]:
        """Buscar servicios con filtros"""
        query = db.query(Servicio)
        
        if nombre:
            query = query.filter(Servicio.nombre_servicio.ilike(f"%{nombre}%"))
        
        if activo is not None:
            query = query.filter(Servicio.activo == activo)
            
        if tipo_servicio_id:
            query = query.filter(Servicio.id_tipo_servicio == tipo_servicio_id)
        
        return query.order_by(Servicio.nombre_servicio).all()

    def get_by_precio_range(self, db: Session, *, precio_min: float = None, precio_max: float = None) -> List[Servicio]:
        """Obtener servicios por rango de precio"""
        query = db.query(Servicio).filter(Servicio.activo == True)
        
        if precio_min is not None:
            query = query.filter(Servicio.precio >= precio_min)
        
        if precio_max is not None:
            query = query.filter(Servicio.precio <= precio_max)
        
        return query.order_by(Servicio.precio).all()

    def exists_by_nombre(self, db: Session, *, nombre_servicio: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un servicio con ese nombre"""
        query = db.query(Servicio).filter(Servicio.nombre_servicio == nombre_servicio)
        if exclude_id:
            query = query.filter(Servicio.id_servicio != exclude_id)
        return query.first() is not None

    def get_with_tipo_info(self, db: Session, *, servicio_id: int) -> Optional[Dict[str, Any]]:
        """Obtener servicio con información del tipo"""
        resultado = db.query(
            Servicio.id_servicio,
            Servicio.nombre_servicio,
            Servicio.precio,
            Servicio.activo,
            Servicio.id_tipo_servicio,
            TipoServicio.descripcion.label('tipo_descripcion')
        ).join(TipoServicio, Servicio.id_tipo_servicio == TipoServicio.id_tipo_servicio)\
         .filter(Servicio.id_servicio == servicio_id).first()
        
        if resultado:
            return {
                "id_servicio": resultado.id_servicio,
                "nombre_servicio": resultado.nombre_servicio,
                "precio": float(resultado.precio),
                "activo": resultado.activo,
                "id_tipo_servicio": resultado.id_tipo_servicio,
                "tipo_descripcion": resultado.tipo_descripcion
            }
        return None

    def activate_service(self, db: Session, *, servicio_id: int) -> Optional[Servicio]:
        """Activar servicio"""
        servicio_obj = self.get(db, servicio_id)
        if servicio_obj:
            servicio_obj.activo = True
            db.commit()
            db.refresh(servicio_obj)
        return servicio_obj

    def deactivate_service(self, db: Session, *, servicio_id: int) -> Optional[Servicio]:
        """Desactivar servicio"""
        servicio_obj = self.get(db, servicio_id)
        if servicio_obj:
            servicio_obj.activo = False
            db.commit()
            db.refresh(servicio_obj)
        return servicio_obj

    def get_mas_solicitados(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener servicios más solicitados"""
        from app.models.servicio_solicitado import ServicioSolicitado
        
        resultado = db.query(
            Servicio.id_servicio,
            Servicio.nombre_servicio,
            Servicio.precio,
            func.count(ServicioSolicitado.id_servicio_solicitado).label('total_solicitudes')
        ).outerjoin(ServicioSolicitado, Servicio.id_servicio == ServicioSolicitado.id_servicio)\
         .group_by(Servicio.id_servicio, Servicio.nombre_servicio, Servicio.precio)\
         .order_by(func.count(ServicioSolicitado.id_servicio_solicitado).desc())\
         .limit(limit).all()
        
        return [
            {
                "id_servicio": r.id_servicio,
                "nombre_servicio": r.nombre_servicio,
                "precio": float(r.precio),
                "total_solicitudes": r.total_solicitudes or 0
            }
            for r in resultado
        ]

    def get_estadisticas_precios(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de precios"""
        resultado = db.query(
            func.min(Servicio.precio).label('precio_minimo'),
            func.max(Servicio.precio).label('precio_maximo'),
            func.avg(Servicio.precio).label('precio_promedio'),
            func.count(Servicio.id_servicio).label('total_servicios')
        ).filter(Servicio.activo == True).first()
        
        return {
            "precio_minimo": float(resultado.precio_minimo) if resultado.precio_minimo else 0,
            "precio_maximo": float(resultado.precio_maximo) if resultado.precio_maximo else 0,
            "precio_promedio": float(resultado.precio_promedio) if resultado.precio_promedio else 0,
            "total_servicios": resultado.total_servicios or 0
        }

# ===== PATOLOGÍA COMPLETO =====
class CRUDPatologia(CRUDBase[Patologia, PatologiaCreate, None]):

    def get_by_nombre(self, db: Session, *, nombre_patologia: str) -> Optional[Patologia]:
        """Obtener patología por nombre exacto"""
        return db.query(Patologia).filter(Patologia.nombre_patologia == nombre_patologia).first()

    def get_by_especie(self, db: Session, *, especie: str) -> List[Patologia]:
        """Obtener patologías por especie"""
        return db.query(Patologia).filter(
            or_(
                Patologia.especie_afecta == especie,
                Patologia.especie_afecta == "Ambas"
            )
        ).order_by(Patologia.nombre_patologia).all()

    def get_by_gravedad(self, db: Session, *, gravedad: str) -> List[Patologia]:
        """Obtener patologías por gravedad"""
        return db.query(Patologia).filter(Patologia.gravedad == gravedad) \
            .order_by(Patologia.nombre_patologia).all()

    def get_cronicas(self, db: Session) -> List[Patologia]:
        """Obtener patologías crónicas"""
        return db.query(Patologia).filter(Patologia.es_crónica == True) \
            .order_by(Patologia.nombre_patologia).all()

    def get_contagiosas(self, db: Session) -> List[Patologia]:
        """Obtener patologías contagiosas"""
        return db.query(Patologia).filter(Patologia.es_contagiosa == True) \
            .order_by(Patologia.nombre_patologia).all()

    def search_patologias(self, db: Session, *, nombre: str = None, especie: str = None, gravedad: str = None) -> List[
        Patologia]:
        """Buscar patologías con múltiples filtros"""
        query = db.query(Patologia)

        if nombre:
            query = query.filter(Patologia.nombre_patologia.ilike(f"%{nombre}%"))

        if especie:
            query = query.filter(
                or_(
                    Patologia.especie_afecta == especie,
                    Patologia.especie_afecta == "Ambas"
                )
            )

        if gravedad:
            query = query.filter(Patologia.gravedad == gravedad)

        return query.order_by(Patologia.nombre_patologia).all()

    def exists_by_nombre(self, db: Session, *, nombre_patologia: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe una patología con ese nombre"""
        query = db.query(Patologia).filter(Patologia.nombre_patologia == nombre_patologia)
        if exclude_id:
            query = query.filter(Patologia.id_patologia != exclude_id)
        return query.first() is not None

    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de patologías"""
        total = db.query(Patologia).count()

        # Por especie
        perros = db.query(Patologia).filter(
            or_(
                Patologia.especie_afecta == "Perro",
                Patologia.especie_afecta == "Ambas"
            )
        ).count()

        gatos = db.query(Patologia).filter(
            or_(
                Patologia.especie_afecta == "Gato",
                Patologia.especie_afecta == "Ambas"
            )
        ).count()

        # Por gravedad
        por_gravedad = db.query(
            Patologia.gravedad,
            func.count(Patologia.id_patologia).label('total')
        ).group_by(Patologia.gravedad).all()

        # Características especiales
        cronicas = db.query(Patologia).filter(Patologia.es_crónica == True).count()
        contagiosas = db.query(Patologia).filter(Patologia.es_contagiosa == True).count()

        return {
            "total_patologias": total,
            "por_especie": {
                "perros": perros,
                "gatos": gatos,
                "ambas": db.query(Patologia).filter(Patologia.especie_afecta == "Ambas").count()
            },
            "por_gravedad": {gravedad.gravedad: gravedad.total for gravedad in por_gravedad},
            "caracteristicas": {
                "cronicas": cronicas,
                "contagiosas": contagiosas,
                "agudas": total - cronicas
            }
        }

    def get_mas_diagnosticadas(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener patologías más diagnosticadas"""
        from app.models.diagnostico import Diagnostico

        resultado = db.query(
            Patologia.id_patologia,
            Patologia.nombre_patologia,
            Patologia.gravedad,
            func.count(Diagnostico.id_diagnostico).label('total_diagnosticos')
        ).outerjoin(Diagnostico, Patologia.id_patologia == Diagnostico.id_patologia) \
            .group_by(Patologia.id_patologia, Patologia.nombre_patologia, Patologia.gravedad) \
            .order_by(func.count(Diagnostico.id_diagnostico).desc()) \
            .limit(limit).all()

        return [
            {
                "id_patologia": r.id_patologia,
                "nombre_patologia": r.nombre_patologia,
                "gravedad": r.gravedad,
                "total_diagnosticos": r.total_diagnosticos or 0
            }
            for r in resultado
        ]

    def get_all_ordenadas(self, db: Session) -> List[Patologia]:
        """Obtener todas las patologías ordenadas alfabéticamente"""
        return db.query(Patologia).order_by(Patologia.nombre_patologia).all()


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

# Instancias únicas
raza = CRUDRaza(Raza)
tipo_animal = CRUDTipoAnimal(TipoAnimal)
especialidad = CRUDEspecialidad(Especialidad)
tipo_servicio = CRUDTipoServicio(TipoServicio)
servicio = CRUDServicio(Servicio)
patologia = CRUDPatologia(Patologia)
cliente_mascota = CRUDClienteMascota(ClienteMascota)