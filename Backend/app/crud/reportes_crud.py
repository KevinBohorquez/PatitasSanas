# app/crud/reportes_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, extract
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from app.models.clientes import Cliente
from app.models.mascota import Mascota
from app.models.veterinario import Veterinario
from app.models.consulta import Consulta
from app.models.cita import Cita
from app.models.servicio import Servicio
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje
from app.models.diagnostico import Diagnostico
from app.models.tratamiento import Tratamiento
from app.models.servicio_solicitado import ServicioSolicitado


class CRUDReportes:
    """CRUD para generar reportes y análisis del sistema"""
    
    def get_reporte_clientes(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[str, Any]:
        """Reporte completo de clientes"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=365)
        if not fecha_fin:
            fecha_fin = date.today()
        
        # Estadísticas generales
        total_clientes = db.query(Cliente).count()
        clientes_activos = db.query(Cliente).filter(Cliente.estado == "Activo").count()
        
        # Nuevos clientes en el período
        nuevos_clientes = db.query(Cliente).filter(
            func.date(Cliente.fecha_registro).between(fecha_inicio, fecha_fin)
        ).count()
        
        # Clientes por género
        por_genero = db.query(
            Cliente.genero,
            func.count(Cliente.id_cliente).label('total')
        ).group_by(Cliente.genero).all()
        
        # Clientes con más mascotas
        clientes_con_mascotas = db.query(
            Cliente.nombre,
            Cliente.apellido_paterno,
            Cliente.email,
            func.count(Mascota.id_mascota).label('total_mascotas')
        ).outerjoin(Mascota, Cliente.id_cliente == Mascota.id_cliente)\
         .group_by(Cliente.id_cliente, Cliente.nombre, Cliente.apellido_paterno, Cliente.email)\
         .order_by(func.count(Mascota.id_mascota).desc())\
         .limit(10).all()
        
        return {
            "periodo": f"{fecha_inicio} - {fecha_fin}",
            "resumen": {
                "total_clientes": total_clientes,
                "clientes_activos": clientes_activos,
                "clientes_inactivos": total_clientes - clientes_activos,
                "nuevos_clientes_periodo": nuevos_clientes
            },
            "por_genero": [{"genero": g.genero, "total": g.total} for g in por_genero],
            "clientes_top_mascotas": [
                {
                    "cliente": f"{c.nombre} {c.apellido_paterno}",
                    "email": c.email,
                    "total_mascotas": c.total_mascotas
                } for c in clientes_con_mascotas
            ]
        }
    
    def get_reporte_veterinarios(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[str, Any]:
        """Reporte de rendimiento de veterinarios"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()
        
        # Performance por veterinario
        performance = db.query(
            Veterinario.nombre,
            Veterinario.apellido_paterno,
            Veterinario.turno,
            func.count(Consulta.id_consulta).label('total_consultas'),
            func.count(Triaje.id_triaje).label('total_triajes')
        ).outerjoin(Consulta, Veterinario.id_veterinario == Consulta.id_veterinario)\
         .outerjoin(Triaje, Veterinario.id_veterinario == Triaje.id_veterinario)\
         .filter(
            or_(
                Consulta.fecha_consulta.between(fecha_inicio, fecha_fin),
                Consulta.fecha_consulta.is_(None)
            )
         )\
         .group_by(Veterinario.id_veterinario, Veterinario.nombre, Veterinario.apellido_paterno, Veterinario.turno)\
         .order_by(func.count(Consulta.id_consulta).desc()).all()
        
        # Veterinarios por turno
        por_turno = db.query(
            Veterinario.turno,
            func.count(Veterinario.id_veterinario).label('total'),
            func.sum(func.case([(Veterinario.disposicion == 'Libre', 1)], else_=0)).label('disponibles')
        ).group_by(Veterinario.turno).all()
        
        return {
            "periodo": f"{fecha_inicio} - {fecha_fin}",
            "performance_veterinarios": [
                {
                    "veterinario": f"{v.nombre} {v.apellido_paterno}",
                    "turno": v.turno,
                    "total_consultas": v.total_consultas or 0,
                    "total_triajes": v.total_triajes or 0
                } for v in performance
            ],
            "distribucion_turnos": [
                {
                    "turno": t.turno,
                    "total": t.total,
                    "disponibles": t.disponibles or 0
                } for t in por_turno
            ]
        }
    
    def get_reporte_servicios(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[str, Any]:
        """Reporte de servicios más solicitados e ingresos"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()
        
        # Servicios más solicitados
        servicios_populares = db.query(
            Servicio.nombre_servicio,
            Servicio.precio,
            func.count(ServicioSolicitado.id_servicio_solicitado).label('total_solicitudes'),
            (func.count(ServicioSolicitado.id_servicio_solicitado) * Servicio.precio).label('ingresos_estimados')
        ).join(ServicioSolicitado, Servicio.id_servicio == ServicioSolicitado.id_servicio)\
         .filter(ServicioSolicitado.fecha_solicitado.between(fecha_inicio, fecha_fin))\
         .group_by(Servicio.id_servicio, Servicio.nombre_servicio, Servicio.precio)\
         .order_by(func.count(ServicioSolicitado.id_servicio_solicitado).desc())\
         .limit(15).all()
        
        # Ingresos totales estimados
        ingresos_totales = sum([s.ingresos_estimados or 0 for s in servicios_populares])
        
        # Servicios por estado
        servicios_por_estado = db.query(
            ServicioSolicitado.estado_examen,
            func.count(ServicioSolicitado.id_servicio_solicitado).label('total')
        ).filter(ServicioSolicitado.fecha_solicitado.between(fecha_inicio, fecha_fin))\
         .group_by(ServicioSolicitado.estado_examen).all()
        
        return {
            "periodo": f"{fecha_inicio} - {fecha_fin}",
            "servicios_populares": [
                {
                    "servicio": s.nombre_servicio,
                    "precio_unitario": float(s.precio),
                    "total_solicitudes": s.total_solicitudes,
                    "ingresos_estimados": float(s.ingresos_estimados or 0)
                } for s in servicios_populares
            ],
            "ingresos_totales_estimados": ingresos_totales,
            "servicios_por_estado": [
                {"estado": e.estado_examen, "total": e.total} for e in servicios_por_estado
            ]
        }
    
    def get_reporte_consultas(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[str, Any]:
        """Reporte de consultas y diagnósticos"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()
        
        # Consultas por día
        consultas_por_dia = db.query(
            func.date(Consulta.fecha_consulta).label('fecha'),
            func.count(Consulta.id_consulta).label('total_consultas')
        ).filter(Consulta.fecha_consulta.between(fecha_inicio, fecha_fin))\
         .group_by(func.date(Consulta.fecha_consulta))\
         .order_by(func.date(Consulta.fecha_consulta)).all()
        
        # Diagnósticos más frecuentes
        from app.models.patologia import Patologia
        diagnosticos_frecuentes = db.query(
            Patologia.nombre_patologia,
            Patologia.gravedad,
            func.count(Diagnostico.id_diagnostico).label('total_diagnosticos')
        ).join(Diagnostico, Patologia.id_patologia == Diagnostico.id_patologia)\
         .join(Consulta, Diagnostico.id_consulta == Consulta.id_consulta)\
         .filter(Consulta.fecha_consulta.between(fecha_inicio, fecha_fin))\
         .group_by(Patologia.id_patologia, Patologia.nombre_patologia, Patologia.gravedad)\
         .order_by(func.count(Diagnostico.id_diagnostico).desc())\
         .limit(10).all()
        
        # Condición general de pacientes
        condiciones = db.query(
            Consulta.condicion_general,
            func.count(Consulta.id_consulta).label('total')
        ).filter(Consulta.fecha_consulta.between(fecha_inicio, fecha_fin))\
         .group_by(Consulta.condicion_general).all()
        
        return {
            "periodo": f"{fecha_inicio} - {fecha_fin}",
            "consultas_por_dia": [
                {"fecha": str(c.fecha), "total": c.total_consultas} for c in consultas_por_dia
            ],
            "diagnosticos_frecuentes": [
                {
                    "patologia": d.nombre_patologia,
                    "gravedad": d.gravedad,
                    "total_diagnosticos": d.total_diagnosticos
                } for d in diagnosticos_frecuentes
            ],
            "condiciones_generales": [
                {"condicion": c.condicion_general, "total": c.total} for c in condiciones
            ]
        }
    
    def get_reporte_urgencias(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[str, Any]:
        """Reporte de urgencias y triajes"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=7)
        if not fecha_fin:
            fecha_fin = date.today()
        
        # Urgencias por clasificación
        urgencias = db.query(
            Triaje.clasificacion_urgencia,
            func.count(Triaje.id_triaje).label('total'),
            func.avg(Triaje.temperatura).label('temp_promedio'),
            func.avg(Triaje.peso_mascota).label('peso_promedio')
        ).filter(Triaje.fecha_hora_triaje.between(fecha_inicio, fecha_fin))\
         .group_by(Triaje.clasificacion_urgencia)\
         .order_by(func.count(Triaje.id_triaje).desc()).all()
        
        # Casos críticos recientes
        casos_criticos = db.query(Triaje)\
                           .filter(
                               and_(
                                   Triaje.clasificacion_urgencia == 'Critico',
                                   Triaje.fecha_hora_triaje.between(fecha_inicio, fecha_fin)
                               )
                           )\
                           .order_by(desc(Triaje.fecha_hora_triaje))\
                           .limit(5).all()
        
        # Tiempo promedio de atención
        # (Simplificado - en producción calcularías desde solicitud hasta consulta)
        solicitudes_completadas = db.query(SolicitudAtencion)\
                                    .filter(
                                        and_(
                                            SolicitudAtencion.estado == "Completada",
                                            SolicitudAtencion.fecha_hora_solicitud.between(fecha_inicio, fecha_fin)
                                        )
                                    ).count()
        
        return {
            "periodo": f"{fecha_inicio} - {fecha_fin}",
            "urgencias_por_clasificacion": [
                {
                    "clasificacion": u.clasificacion_urgencia,
                    "total": u.total,
                    "temperatura_promedio": round(float(u.temp_promedio), 1) if u.temp_promedio else 0,
                    "peso_promedio": round(float(u.peso_promedio), 1) if u.peso_promedio else 0
                } for u in urgencias
            ],
            "casos_criticos_recientes": len(casos_criticos),
            "solicitudes_completadas": solicitudes_completadas
        }
    
    def get_reporte_ejecutivo(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[str, Any]:
        """Reporte ejecutivo completo"""
        if not fecha_inicio:
            fecha_inicio = date.today() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = date.today()
        
        # KPIs principales
        total_consultas = db.query(Consulta).filter(
            Consulta.fecha_consulta.between(fecha_inicio, fecha_fin)
        ).count()
        
        total_clientes = db.query(Cliente).count()
        nuevos_clientes = db.query(Cliente).filter(
            func.date(Cliente.fecha_registro).between(fecha_inicio, fecha_fin)
        ).count()
        
        ingresos_estimados = db.query(
            func.sum(Servicio.precio * func.count(ServicioSolicitado.id_servicio_solicitado))
        ).join(ServicioSolicitado, Servicio.id_servicio == ServicioSolicitado.id_servicio)\
         .filter(ServicioSolicitado.fecha_solicitado.between(fecha_inicio, fecha_fin)).scalar() or 0
        
        # Tendencias por semana
        tendencias_semanales = db.query(
            func.year(Consulta.fecha_consulta).label('año'),
            func.week(Consulta.fecha_consulta).label('semana'),
            func.count(Consulta.id_consulta).label('consultas')
        ).filter(Consulta.fecha_consulta.between(fecha_inicio, fecha_fin))\
         .group_by(func.year(Consulta.fecha_consulta), func.week(Consulta.fecha_consulta))\
         .order_by(func.year(Consulta.fecha_consulta), func.week(Consulta.fecha_consulta)).all()
        
        return {
            "periodo": f"{fecha_inicio} - {fecha_fin}",
            "kpis_principales": {
                "total_consultas": total_consultas,
                "total_clientes": total_clientes,
                "nuevos_clientes": nuevos_clientes,
                "ingresos_estimados": float(ingresos_estimados),
                "consultas_por_dia": round(total_consultas / ((fecha_fin - fecha_inicio).days + 1), 1)
            },
            "tendencias_semanales": [
                {
                    "año": t.año,
                    "semana": t.semana,
                    "consultas": t.consultas
                } for t in tendencias_semanales
            ]
        }


# Instancia única
reportes = CRUDReportes()