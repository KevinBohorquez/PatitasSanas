# app/crud/dashboard_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract, or_
from typing import Dict, List, Any
from datetime import datetime, date, timedelta
from app.models.clientes import Cliente
from app.models.mascota import Mascota
from app.models.veterinario import Veterinario
from app.models.consulta import Consulta
from app.models.cita import Cita
from app.models.servicio import Servicio
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje

class CRUDDashboard:
    
    def get_stats_generales(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas generales del sistema"""
        today = date.today()
        
        return {
            "total_clientes": db.query(Cliente).count(),
            "clientes_activos": db.query(Cliente).filter(Cliente.estado == "Activo").count(),
            "total_mascotas": db.query(Mascota).count(),
            "total_veterinarios": db.query(Veterinario).count(),
            "veterinarios_disponibles": db.query(Veterinario).filter(
                and_(
                    Veterinario.estado == "Activo",
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

    def get_veterinarios_performance(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> List[Dict[str, Any]]:
        """Obtener performance de veterinarios"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()
        
        resultado = db.query(
            Veterinario.nombre,
            Veterinario.apellido_paterno,
            func.count(Consulta.id_consulta).label('total_consultas'),
            func.count(Triaje.id_triaje).label('total_triajes')
        ).outerjoin(Consulta, Veterinario.id_veterinario == Consulta.id_veterinario)\
         .outerjoin(Triaje, Veterinario.id_veterinario == Triaje.id_veterinario)\
         .filter(
            and_(
                Veterinario.estado == "Activo",
                or_(
                    Consulta.fecha_consulta.between(fecha_inicio, fecha_fin),
                    Consulta.fecha_consulta.is_(None)
                )
            )
         )\
         .group_by(Veterinario.id_veterinario, Veterinario.nombre, Veterinario.apellido_paterno)\
         .order_by(desc('total_consultas')).all()
        
        return [
            {
                "veterinario": f"{r.nombre} {r.apellido_paterno}",
                "total_consultas": r.total_consultas or 0,
                "total_triajes": r.total_triajes or 0
            }
            for r in resultado
        ]

    def get_urgencias_por_clasificacion(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> List[Dict[str, Any]]:
        """Obtener urgencias por clasificación"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=7)
        if not fecha_fin:
            fecha_fin = date.today()
        
        resultado = db.query(
            Triaje.clasificacion_urgencia,
            func.count(Triaje.id_triaje).label('total')
        ).filter(
            Triaje.fecha_hora_triaje.between(fecha_inicio, fecha_fin)
        ).group_by(Triaje.clasificacion_urgencia)\
         .order_by(desc('total')).all()
        
        return [
            {
                "clasificacion": r.clasificacion_urgencia,
                "total": r.total
            }
            for r in resultado
        ]

    def get_clientes_con_mas_mascotas(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener clientes con más mascotas"""
        resultado = db.query(
            Cliente.nombre,
            Cliente.apellido_paterno,
            Cliente.email,
            func.count(Mascota.id_mascota).label('total_mascotas')
        ).join(Mascota, Cliente.id_cliente == Mascota.id_cliente)\
         .group_by(Cliente.id_cliente, Cliente.nombre, Cliente.apellido_paterno, Cliente.email)\
         .order_by(desc('total_mascotas'))\
         .limit(limit).all()
        
        return [
            {
                "cliente": f"{r.nombre} {r.apellido_paterno}",
                "email": r.email,
                "total_mascotas": r.total_mascotas
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

    def get_agenda_del_dia(self, db: Session, *, fecha: date = None) -> Dict[str, Any]:
        """Obtener agenda del día"""
        if not fecha:
            fecha = date.today()
        
        # Citas programadas
        citas = db.query(Cita).filter(
            and_(
                func.date(Cita.fecha_hora_programada) == fecha,
                Cita.estado_cita == "Programada"
            )
        ).order_by(Cita.fecha_hora_programada).all()
        
        # Consultas del día
        consultas = db.query(Consulta).filter(
            func.date(Consulta.fecha_consulta) == fecha
        ).order_by(Consulta.fecha_consulta).all()
        
        # Solicitudes pendientes
        solicitudes_pendientes = db.query(SolicitudAtencion).filter(
            SolicitudAtencion.estado == "Pendiente"
        ).count()
        
        return {
            "fecha": fecha.isoformat(),
            "citas_programadas": len(citas),
            "consultas_realizadas": len(consultas),
            "solicitudes_pendientes": solicitudes_pendientes,
            "citas": [
                {
                    "id_cita": cita.id_cita,
                    "hora": cita.fecha_hora_programada.strftime("%H:%M"),
                    "id_mascota": cita.id_mascota,
                    "id_servicio": cita.id_servicio
                }
                for cita in citas
            ]
        }

    def get_reporte_semanal(self, db: Session, *, fecha_inicio: date = None) -> Dict[str, Any]:
        """Obtener reporte semanal"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=7)
        
        fecha_fin = fecha_inicio + timedelta(days=7)
        
        return {
            "periodo": f"{fecha_inicio.isoformat()} - {fecha_fin.isoformat()}",
            "consultas_realizadas": db.query(Consulta).filter(
                Consulta.fecha_consulta.between(fecha_inicio, fecha_fin)
            ).count(),
            "nuevos_clientes": db.query(Cliente).filter(
                func.date(Cliente.fecha_registro).between(fecha_inicio, fecha_fin)
            ).count(),
            "citas_programadas": db.query(Cita).filter(
                and_(
                    func.date(Cita.fecha_hora_programada).between(fecha_inicio, fecha_fin),
                    Cita.estado_cita == "Programada"
                )
            ).count(),
            "urgencias_criticas": db.query(Triaje).filter(
                and_(
                    Triaje.fecha_hora_triaje.between(fecha_inicio, fecha_fin),
                    Triaje.clasificacion_urgencia == "Critico"
                )
            ).count()
        }

# Instancia única
dashboard = CRUDDashboard()