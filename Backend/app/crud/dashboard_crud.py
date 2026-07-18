# app/crud/dashboard_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from typing import Dict, List, Any
from datetime import datetime, date, timedelta
from app.models.clientes import Cliente
from app.models.mascota import Mascota
from app.models.veterinario import Veterinario
from app.models.consulta import Consulta
from app.models.cita import Cita
from app.models.servicio import Servicio
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.usuario import Usuario

class CRUDDashboard:
    
    def get_stats_generales(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas generales del sistema"""
        today = date.today()
        
        return {
            "total_clientes": db.query(Cliente).count(),
            "clientes_activos": db.query(Cliente).filter(Cliente.estado == "Activo").count(),
            "total_mascotas": db.query(Mascota).count(),
            "total_veterinarios": db.query(Veterinario).count(),
            "veterinarios_disponibles": db.query(Veterinario).join(
                Usuario,
                Veterinario.id_usuario == Usuario.id_usuario
            ).filter(
                and_(
                    Usuario.estado == "Activo",
                    Veterinario.disposicion == "Libre"
                )
            ).count(),
            "consultas_hoy": db.query(Consulta).filter(
                func.date(Consulta.fecha_consulta) == today
            ).count(),
            "citas_pendientes": db.query(Cita).filter(
                and_(
                    Cita.estado_cita == "Programada",
                    Cita.fecha_hora_programada >= datetime.now()
                )
            ).count(),
            "solicitudes_pendientes": db.query(SolicitudAtencion).filter(
                SolicitudAtencion.estado == "Pendiente"
            ).count()
        }

    def get_consultas_por_mes(self, db: Session, *, año: int = None) -> List[Dict[str, Any]]:
        """Obtener consultas agrupadas por mes"""
        if not año:
            año = datetime.now().year
        
        resultado = db.query(
            extract('month', Consulta.fecha_consulta).label('mes'),
            func.count(Consulta.id_consulta).label('total_consultas')
        ).filter(
            extract('year', Consulta.fecha_consulta) == año
        ).group_by(
            extract('month', Consulta.fecha_consulta)
        ).order_by('mes').all()
        
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        return [
            {
                "mes": meses[r.mes - 1],
                "total_consultas": r.total_consultas
            }
            for r in resultado
        ]

    def get_mascotas_por_especie(self, db: Session) -> List[Dict[str, Any]]:
        """Obtener distribución de mascotas por especie"""
        from app.models.raza import Raza
        from app.models.tipo_animal import TipoAnimal
        
        resultado = db.query(
            TipoAnimal.descripcion.label('especie'),
            func.count(Mascota.id_mascota).label('total')
        ).join(Raza, Mascota.id_raza == Raza.id_raza)\
         .join(TipoAnimal, Raza.id_raza == TipoAnimal.id_raza)\
         .group_by(TipoAnimal.descripcion).all()
        
        return [
            {
                "especie": r.especie,
                "total": r.total
            }
            for r in resultado
        ]

    def get_servicios_mas_solicitados(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener servicios más solicitados"""
        from app.models.servicio_solicitado import ServicioSolicitado
        
        resultado = db.query(
            Servicio.nombre_servicio,
            func.count(ServicioSolicitado.id_servicio_solicitado).label('total_solicitudes')
        ).join(ServicioSolicitado, Servicio.id_servicio == ServicioSolicitado.id_servicio)\
         .group_by(Servicio.id_servicio, Servicio.nombre_servicio)\
         .order_by(desc('total_solicitudes'))\
         .limit(limit).all()
        
        return [
            {
                "servicio": r.nombre_servicio,
                "total_solicitudes": r.total_solicitudes
            }
            for r in resultado
        ]

    def get_ingresos_por_servicio(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> List[Dict[str, Any]]:
        """Obtener ingresos estimados por servicio"""
        from app.models.servicio_solicitado import ServicioSolicitado
        
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()
        
        resultado = db.query(
            Servicio.nombre_servicio,
            func.count(ServicioSolicitado.id_servicio_solicitado).label('cantidad'),
            Servicio.precio,
            (func.count(ServicioSolicitado.id_servicio_solicitado) * Servicio.precio).label('ingreso_estimado')
        ).join(ServicioSolicitado, Servicio.id_servicio == ServicioSolicitado.id_servicio)\
         .filter(
            ServicioSolicitado.fecha_solicitado.between(fecha_inicio, fecha_fin)
         )\
         .group_by(Servicio.id_servicio, Servicio.nombre_servicio, Servicio.precio)\
         .order_by(desc('ingreso_estimado')).all()
        
        return [
            {
                "servicio": r.nombre_servicio,
                "cantidad": r.cantidad,
                "precio_unitario": float(r.precio),
                "ingreso_estimado": float(r.ingreso_estimado)
            }
            for r in resultado
        ]

    def get_tasa_asistencia(self, db: Session) -> Dict[str, Any]:
        """Obtener tasa de asistencia agrupando citas por estado_cita"""
        resultado = db.query(
            Cita.estado_cita,
            func.count(Cita.id_cita).label('total')
        ).group_by(Cita.estado_cita).all()

        conteos = {r.estado_cita: r.total for r in resultado}

        programadas = conteos.get('Programada', 0)
        canceladas = conteos.get('Cancelada', 0)
        atendidas = conteos.get('Atendida', 0)
        total_resueltas = atendidas + canceladas
        tasa = round((atendidas / total_resueltas * 100), 2) if total_resueltas > 0 else 0.0

        return {
            "Programada": programadas,
            "Cancelada": canceladas,
            "Atendida": atendidas,
            "tasa_asistencia": tasa
        }

# Instancia única
dashboard = CRUDDashboard()
