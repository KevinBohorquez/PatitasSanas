# app/crud/consulta_crud.py (VERSIÓN COMPLETA)
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, timedelta
from app.crud.base_crud import CRUDBase
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje
from app.models.consulta import Consulta
from app.models.diagnostico import Diagnostico
from app.models.tratamiento import Tratamiento
from app.models.historial_clinico import HistorialClinico
from app.models.cita import Cita
from app.models.servicio_solicitado import ServicioSolicitado
from app.models.resultado_servicio import ResultadoServicio
from app.schemas.consulta_schema import (
    SolicitudAtencionCreate, TriajeCreate, ConsultaCreate,
    DiagnosticoCreate, TratamientoCreate, HistorialClinicoCreate,
    CitaCreate, CitaUpdate, ServicioSolicitadoCreate, ResultadoServicioCreate,
    ConsultaSearch, CitaSearch, HistorialSearch
)


# ===== SOLICITUD ATENCIÓN COMPLETO =====
class CRUDSolicitudAtencion(CRUDBase[SolicitudAtencion, SolicitudAtencionCreate, None]):

    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[SolicitudAtencion]:
        """Obtener solicitudes por mascota"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.id_mascota == mascota_id) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_by_recepcionista(self, db: Session, *, recepcionista_id: int) -> List[SolicitudAtencion]:
        """Obtener solicitudes por recepcionista"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.id_recepcionista == recepcionista_id) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_pendientes(self, db: Session) -> List[SolicitudAtencion]:
        """Obtener solicitudes pendientes"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == "Pendiente") \
            .order_by(SolicitudAtencion.fecha_hora_solicitud).all()

    def get_by_tipo(self, db: Session, *, tipo_solicitud: str) -> List[SolicitudAtencion]:
        """Obtener solicitudes por tipo"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_by_estado(self, db: Session, *, estado: str) -> List[SolicitudAtencion]:
        """Obtener solicitudes por estado"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == estado) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_urgentes_pendientes(self, db: Session) -> List[SolicitudAtencion]:
        """Obtener solicitudes urgentes pendientes"""
        return db.query(SolicitudAtencion).filter(
            and_(
                SolicitudAtencion.tipo_solicitud == "Consulta urgente",
                SolicitudAtencion.estado.in_(["Pendiente", "En triaje"])
            )
        ).order_by(SolicitudAtencion.fecha_hora_solicitud).all()

    def cambiar_estado(self, db: Session, *, solicitud_id: int, nuevo_estado: str) -> Optional[SolicitudAtencion]:
        """Cambiar estado de la solicitud"""
        solicitud = self.get(db, solicitud_id)
        if solicitud:
            solicitud.estado = nuevo_estado
            db.commit()
            db.refresh(solicitud)
        return solicitud

    def get_estadisticas_por_estado(self, db: Session) -> Dict[str, int]:
        """Obtener estadísticas por estado"""
        return {
            "pendientes": db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == "Pendiente").count(),
            "en_triaje": db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == "En triaje").count(),
            "en_atencion": db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == "En atencion").count(),
            "completadas": db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == "Completada").count(),
            "canceladas": db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == "Cancelada").count()
        }


# ===== TRIAJE COMPLETO =====
class CRUDTriaje(CRUDBase[Triaje, TriajeCreate, None]):

    def get_by_solicitud(self, db: Session, *, solicitud_id: int) -> Optional[Triaje]:
        """Obtener triaje por solicitud"""
        return db.query(Triaje).filter(Triaje.id_solicitud == solicitud_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int, limit: int = 50) -> List[Triaje]:
        """Obtener triajes realizados por un veterinario"""
        return db.query(Triaje).filter(Triaje.id_veterinario == veterinario_id) \
            .order_by(desc(Triaje.fecha_hora_triaje)) \
            .limit(limit).all()

    def get_by_urgencia(self, db: Session, *, clasificacion: str) -> List[Triaje]:
        """Obtener triajes por nivel de urgencia"""
        return db.query(Triaje).filter(Triaje.clasificacion_urgencia == clasificacion) \
            .order_by(desc(Triaje.fecha_hora_triaje)).all()

    def get_criticos(self, db: Session) -> List[Triaje]:
        """Obtener casos críticos"""
        return db.query(Triaje).filter(Triaje.clasificacion_urgencia == "Critico") \
            .order_by(desc(Triaje.fecha_hora_triaje)).all()

    def get_criticos_recientes(self, db: Session, *, horas: int = 24) -> List[Triaje]:
        """Obtener casos críticos recientes"""
        fecha_limite = datetime.now() - timedelta(hours=horas)
        return db.query(Triaje).filter(
            and_(
                Triaje.clasificacion_urgencia == "Critico",
                Triaje.fecha_hora_triaje >= fecha_limite
            )
        ).order_by(desc(Triaje.fecha_hora_triaje)).all()

    def get_by_condicion_corporal(self, db: Session, *, condicion: str) -> List[Triaje]:
        """Obtener triajes por condición corporal"""
        return db.query(Triaje).filter(Triaje.condicion_corporal == condicion).all()

    def get_promedios_signos_vitales(self, db: Session, *, fecha_inicio: date = None, fecha_fin: date = None) -> Dict[
        str, float]:
        """Obtener promedios de signos vitales"""
        query = db.query(Triaje)

        if fecha_inicio:
            query = query.filter(Triaje.fecha_hora_triaje >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Triaje.fecha_hora_triaje <= fecha_fin)

        resultado = query.with_entities(
            func.avg(Triaje.peso_mascota).label('peso_promedio'),
            func.avg(Triaje.latido_por_minuto).label('latidos_promedio'),
            func.avg(Triaje.frecuencia_respiratoria_rpm).label('respiracion_promedio'),
            func.avg(Triaje.temperatura).label('temperatura_promedio'),
            func.avg(Triaje.frecuencia_pulso).label('pulso_promedio')
        ).first()

        return {
            "peso_promedio": float(resultado.peso_promedio) if resultado.peso_promedio else 0,
            "latidos_promedio": float(resultado.latidos_promedio) if resultado.latidos_promedio else 0,
            "respiracion_promedio": float(resultado.respiracion_promedio) if resultado.respiracion_promedio else 0,
            "temperatura_promedio": float(resultado.temperatura_promedio) if resultado.temperatura_promedio else 0,
            "pulso_promedio": float(resultado.pulso_promedio) if resultado.pulso_promedio else 0
        }


# ===== CONSULTA COMPLETO =====
class CRUDConsulta(CRUDBase[Consulta, ConsultaCreate, None]):

    def get_by_triaje(self, db: Session, *, triaje_id: int) -> Optional[Consulta]:
        """Obtener consulta por triaje"""
        return db.query(Consulta).filter(Consulta.id_triaje == triaje_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int, fecha_inicio: date = None,
                           fecha_fin: date = None) -> List[Consulta]:
        """Obtener consultas por veterinario en un rango de fechas"""
        query = db.query(Consulta).filter(Consulta.id_veterinario == veterinario_id)

        if fecha_inicio:
            query = query.filter(Consulta.fecha_consulta >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Consulta.fecha_consulta <= fecha_fin)

        return query.order_by(desc(Consulta.fecha_consulta)).all()

    def get_by_tipo(self, db: Session, *, tipo_consulta: str) -> List[Consulta]:
        """Obtener consultas por tipo"""
        return db.query(Consulta).filter(Consulta.tipo_consulta.ilike(f"%{tipo_consulta}%")) \
            .order_by(desc(Consulta.fecha_consulta)).all()

    def get_by_condicion(self, db: Session, *, condicion_general: str) -> List[Consulta]:
        """Obtener consultas por condición general"""
        return db.query(Consulta).filter(Consulta.condicion_general == condicion_general) \
            .order_by(desc(Consulta.fecha_consulta)).all()

    def search_consultas(self, db: Session, *, search_params: ConsultaSearch) -> Tuple[List[Consulta], int]:
        """Buscar consultas con filtros"""
        query = db.query(Consulta)

        if search_params.id_mascota:
            # Join con triaje y solicitud para obtener id_mascota
            query = query.join(Triaje, Consulta.id_triaje == Triaje.id_triaje) \
                .join(SolicitudAtencion, Triaje.id_solicitud == SolicitudAtencion.id_solicitud) \
                .filter(SolicitudAtencion.id_mascota == search_params.id_mascota)

        if search_params.id_veterinario:
            query = query.filter(Consulta.id_veterinario == search_params.id_veterinario)

        if search_params.fecha_desde:
            query = query.filter(Consulta.fecha_consulta >= search_params.fecha_desde)

        if search_params.fecha_hasta:
            query = query.filter(Consulta.fecha_consulta <= search_params.fecha_hasta)

        if search_params.condicion_general:
            query = query.filter(Consulta.condicion_general == search_params.condicion_general)

        if search_params.es_seguimiento is not None:
            query = query.filter(Consulta.es_seguimiento == search_params.es_seguimiento)

        total = query.count()

        consultas = query.order_by(desc(Consulta.fecha_consulta)) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return consultas, total

    def get_seguimientos(self, db: Session) -> List[Consulta]:
        """Obtener consultas de seguimiento"""
        return db.query(Consulta).filter(Consulta.es_seguimiento == True) \
            .order_by(desc(Consulta.fecha_consulta)).all()

    def get_por_fecha(self, db: Session, *, fecha: date) -> List[Consulta]:
        """Obtener consultas de una fecha específica"""
        return db.query(Consulta).filter(func.date(Consulta.fecha_consulta) == fecha) \
            .order_by(Consulta.fecha_consulta).all()

    def get_estadisticas_por_condicion(self, db: Session) -> Dict[str, int]:
        """Obtener estadísticas por condición general"""
        return {
            "excelente": db.query(Consulta).filter(Consulta.condicion_general == "Excelente").count(),
            "buena": db.query(Consulta).filter(Consulta.condicion_general == "Buena").count(),
            "regular": db.query(Consulta).filter(Consulta.condicion_general == "Regular").count(),
            "mala": db.query(Consulta).filter(Consulta.condicion_general == "Mala").count(),
            "critica": db.query(Consulta).filter(Consulta.condicion_general == "Critica").count()
        }


# ===== DIAGNÓSTICO COMPLETO =====
class CRUDDiagnostico(CRUDBase[Diagnostico, DiagnosticoCreate, None]):

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[Diagnostico]:
        """Obtener diagnósticos de una consulta"""
        return db.query(Diagnostico).filter(Diagnostico.id_consulta == consulta_id) \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def get_by_patologia(self, db: Session, *, patologia_id: int) -> List[Diagnostico]:
        """Obtener diagnósticos por patología"""
        return db.query(Diagnostico).filter(Diagnostico.id_patologia == patologia_id) \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def get_by_tipo(self, db: Session, *, tipo_diagnostico: str) -> List[Diagnostico]:
        """Obtener diagnósticos por tipo"""
        return db.query(Diagnostico).filter(Diagnostico.tipo_diagnostico == tipo_diagnostico) \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def get_by_estado_patologia(self, db: Session, *, estado_patologia: str) -> List[Diagnostico]:
        """Obtener diagnósticos por estado de patología"""
        return db.query(Diagnostico).filter(Diagnostico.estado_patologia == estado_patologia) \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def get_confirmados(self, db: Session) -> List[Diagnostico]:
        """Obtener diagnósticos confirmados"""
        return db.query(Diagnostico).filter(Diagnostico.tipo_diagnostico == "Confirmado") \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def get_presuntivos(self, db: Session) -> List[Diagnostico]:
        """Obtener diagnósticos presuntivos"""
        return db.query(Diagnostico).filter(Diagnostico.tipo_diagnostico == "Presuntivo") \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

    def confirmar_diagnostico(self, db: Session, *, diagnostico_id: int) -> Optional[Diagnostico]:
        """Confirmar un diagnóstico presuntivo"""
        diagnostico_obj = self.get(db, diagnostico_id)
        if diagnostico_obj and diagnostico_obj.tipo_diagnostico == "Presuntivo":
            diagnostico_obj.tipo_diagnostico = "Confirmado"
            db.commit()
            db.refresh(diagnostico_obj)
        return diagnostico_obj

    def get_mas_frecuentes(self, db: Session, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener patologías más diagnosticadas"""
        from app.models.patologia import Patologia

        resultado = db.query(
            Patologia.nombre_patologia,
            func.count(Diagnostico.id_diagnostico).label('total_diagnosticos')
        ).join(Patologia, Diagnostico.id_patologia == Patologia.id_patologia) \
            .group_by(Patologia.id_patologia, Patologia.nombre_patologia) \
            .order_by(func.count(Diagnostico.id_diagnostico).desc()) \
            .limit(limit).all()

        return [
            {
                "patologia": r.nombre_patologia,
                "total_diagnosticos": r.total_diagnosticos
            }
            for r in resultado
        ]


# ===== TRATAMIENTO COMPLETO =====
class CRUDTratamiento(CRUDBase[Tratamiento, TratamientoCreate, None]):

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[Tratamiento]:
        """Obtener tratamientos de una consulta"""
        return db.query(Tratamiento).filter(Tratamiento.id_consulta == consulta_id) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_by_patologia(self, db: Session, *, patologia_id: int) -> List[Tratamiento]:
        """Obtener tratamientos por patología"""
        return db.query(Tratamiento).filter(Tratamiento.id_patologia == patologia_id) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_by_tipo(self, db: Session, *, tipo_tratamiento: str) -> List[Tratamiento]:
        """Obtener tratamientos por tipo"""
        return db.query(Tratamiento).filter(Tratamiento.tipo_tratamiento == tipo_tratamiento) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_by_eficacia(self, db: Session, *, eficacia_tratamiento: str) -> List[Tratamiento]:
        """Obtener tratamientos por eficacia"""
        return db.query(Tratamiento).filter(Tratamiento.eficacia_tratamiento == eficacia_tratamiento) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_activos(self, db: Session) -> List[Tratamiento]:
        """Obtener tratamientos activos (iniciados recientemente)"""
        return db.query(Tratamiento).filter(Tratamiento.fecha_inicio <= date.today()) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def get_recientes(self, db: Session, *, dias: int = 30) -> List[Tratamiento]:
        """Obtener tratamientos iniciados en los últimos X días"""
        fecha_limite = date.today() - timedelta(days=dias)
        return db.query(Tratamiento).filter(Tratamiento.fecha_inicio >= fecha_limite) \
            .order_by(desc(Tratamiento.fecha_inicio)).all()

    def actualizar_eficacia(self, db: Session, *, tratamiento_id: int, nueva_eficacia: str) -> Optional[Tratamiento]:
        """Actualizar eficacia del tratamiento"""
        tratamiento_obj = self.get(db, tratamiento_id)
        if tratamiento_obj:
            tratamiento_obj.eficacia_tratamiento = nueva_eficacia
            db.commit()
            db.refresh(tratamiento_obj)
        return tratamiento_obj


# ===== CITA COMPLETO =====
class CRUDCita(CRUDBase[Cita, CitaCreate, CitaUpdate]):

    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[Cita]:
        """Obtener citas de una mascota"""
        return db.query(Cita).filter(Cita.id_mascota == mascota_id) \
            .order_by(desc(Cita.fecha_hora_programada)).all()

    def get_by_servicio(self, db: Session, *, servicio_id: int) -> List[Cita]:
        """Obtener citas de un servicio"""
        return db.query(Cita).filter(Cita.id_servicio == servicio_id) \
            .order_by(desc(Cita.fecha_hora_programada)).all()

    def get_by_estado(self, db: Session, *, estado_cita: str) -> List[Cita]:
        """Obtener citas por estado"""
        return db.query(Cita).filter(Cita.estado_cita == estado_cita) \
            .order_by(Cita.fecha_hora_programada).all()

    def get_programadas(self, db: Session) -> List[Cita]:
        """Obtener citas programadas"""
        return db.query(Cita).filter(Cita.estado_cita == "Programada") \
            .order_by(Cita.fecha_hora_programada).all()

    def get_por_fecha(self, db: Session, *, fecha: date) -> List[Cita]:
        """Obtener citas de una fecha específica"""
        return db.query(Cita).filter(func.date(Cita.fecha_hora_programada) == fecha) \
            .order_by(Cita.fecha_hora_programada).all()

    def get_pendientes_hoy(self, db: Session) -> List[Cita]:
        """Obtener citas programadas para hoy"""
        hoy = date.today()
        return db.query(Cita).filter(
            and_(
                func.date(Cita.fecha_hora_programada) == hoy,
                Cita.estado_cita == "Programada"
            )
        ).order_by(Cita.fecha_hora_programada).all()

    def search_citas(self, db: Session, *, search_params: CitaSearch) -> Tuple[List[Cita], int]:
        """Buscar citas con filtros"""
        query = db.query(Cita)

        if search_params.id_mascota:
            query = query.filter(Cita.id_mascota == search_params.id_mascota)

        if search_params.id_servicio:
            query = query.filter(Cita.id_servicio == search_params.id_servicio)

        if search_params.estado_cita:
            query = query.filter(Cita.estado_cita == search_params.estado_cita)

        if search_params.fecha_desde:
            query = query.filter(func.date(Cita.fecha_hora_programada) >= search_params.fecha_desde)

        if search_params.fecha_hasta:
            query = query.filter(func.date(Cita.fecha_hora_programada) <= search_params.fecha_hasta)

        total = query.count()

        citas = query.order_by(desc(Cita.fecha_hora_programada)) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return citas, total

    def verificar_disponibilidad(self, db: Session, *, fecha_hora: datetime, exclude_id: int = None) -> bool:
        """Verificar disponibilidad de horario"""
        query = db.query(Cita).filter(
            and_(
                Cita.fecha_hora_programada == fecha_hora,
                Cita.estado_cita == "Programada"
            )
        )

        if exclude_id:
            query = query.filter(Cita.id_cita != exclude_id)

        return query.first() is None

    def cancelar_cita(self, db: Session, *, cita_id: int) -> Optional[Cita]:
        """Cancelar una cita"""
        cita = self.get(db, cita_id)
        if cita and cita.estado_cita == "Programada":
            cita.estado_cita = "Cancelada"
            db.commit()
            db.refresh(cita)
        return cita

    def marcar_atendida(self, db: Session, *, cita_id: int) -> Optional[Cita]:
        """Marcar cita como atendida"""
        cita = self.get(db, cita_id)
        if cita and cita.estado_cita == "Programada":
            cita.estado_cita = "Atendida"
            db.commit()
            db.refresh(cita)
        return cita

    def reprogramar_cita(self, db: Session, *, cita_id: int, nueva_fecha_hora: datetime) -> Optional[Cita]:
        """Reprogramar una cita"""
        if not self.verificar_disponibilidad(db, fecha_hora=nueva_fecha_hora, exclude_id=cita_id):
            return None

        cita = self.get(db, cita_id)
        if cita and cita.estado_cita == "Programada":
            cita.fecha_hora_programada = nueva_fecha_hora
            db.commit()
            db.refresh(cita)
        return cita


# ===== SERVICIO SOLICITADO COMPLETO =====
class CRUDServicioSolicitado(CRUDBase[ServicioSolicitado, ServicioSolicitadoCreate, None]):

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[ServicioSolicitado]:
        """Obtener servicios solicitados de una consulta"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_consulta == consulta_id) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def get_by_servicio(self, db: Session, *, servicio_id: int) -> List[ServicioSolicitado]:
        """Obtener solicitudes de un servicio específico"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_servicio == servicio_id) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def get_by_prioridad(self, db: Session, *, prioridad: str) -> List[ServicioSolicitado]:
        """Obtener servicios por prioridad"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.prioridad == prioridad) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def get_by_estado(self, db: Session, *, estado_examen: str) -> List[ServicioSolicitado]:
        """Obtener servicios por estado de examen"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.estado_examen == estado_examen) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def get_pendientes(self, db: Session) -> List[ServicioSolicitado]:
        """Obtener servicios pendientes de programar"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.estado_examen == "Solicitado") \
            .order_by(ServicioSolicitado.fecha_solicitado).all()

    def get_urgentes(self, db: Session) -> List[ServicioSolicitado]:
        """Obtener servicios urgentes"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.prioridad == "Urgente") \
            .order_by(ServicioSolicitado.fecha_solicitado).all()

    def cambiar_estado(self, db: Session, *, servicio_solicitado_id: int, nuevo_estado: str) -> Optional[
        ServicioSolicitado]:
        """Cambiar estado del servicio solicitado"""
        servicio_sol = self.get(db, servicio_solicitado_id)
        if servicio_sol:
            servicio_sol.estado_examen = nuevo_estado
            db.commit()
            db.refresh(servicio_sol)
        return servicio_sol


# ===== RESULTADO SERVICIO COMPLETO =====
class CRUDResultadoServicio(CRUDBase[ResultadoServicio, ResultadoServicioCreate, None]):

    def get_by_cita(self, db: Session, *, cita_id: int) -> Optional[ResultadoServicio]:
        """Obtener resultado de una cita"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.id_cita == cita_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int) -> List[ResultadoServicio]:
        """Obtener resultados realizados por un veterinario"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.id_veterinario == veterinario_id) \
            .order_by(desc(ResultadoServicio.fecha_realizacion)).all()

    def get_by_fecha(self, db: Session, *, fecha: date) -> List[ResultadoServicio]:
        """Obtener resultados de una fecha"""
        return db.query(ResultadoServicio).filter(
            func.date(ResultadoServicio.fecha_realizacion) == fecha
        ).order_by(ResultadoServicio.fecha_realizacion).all()

    def get_with_archivo(self, db: Session) -> List[ResultadoServicio]:
        """Obtener resultados que tienen archivo adjunto"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.archivo_adjunto.isnot(None)) \
            .order_by(desc(ResultadoServicio.fecha_realizacion)).all()

    def get_recientes(self, db: Session, *, dias: int = 7) -> List[ResultadoServicio]:
        """Obtener resultados recientes"""
        fecha_limite = date.today() - timedelta(days=dias)
        return db.query(ResultadoServicio).filter(
            func.date(ResultadoServicio.fecha_realizacion) >= fecha_limite
        ).order_by(desc(ResultadoServicio.fecha_realizacion)).all()

    def buscar_por_contenido(self, db: Session, *, termino: str) -> List[ResultadoServicio]:
        """Buscar resultados por contenido del resultado o interpretación"""
        return db.query(ResultadoServicio).filter(
            or_(
                ResultadoServicio.resultado.ilike(f"%{termino}%"),
                ResultadoServicio.interpretacion.ilike(f"%{termino}%")
            )
        ).order_by(desc(ResultadoServicio.fecha_realizacion)).all()


# ===== HISTORIAL CLÍNICO COMPLETO =====
class CRUDHistorialClinico(CRUDBase[HistorialClinico, HistorialClinicoCreate, None]):

    def get_by_mascota(self, db: Session, *, mascota_id: int, limit: int = 50) -> List[HistorialClinico]:
        """Obtener historial clínico de una mascota"""
        return db.query(HistorialClinico) \
            .filter(HistorialClinico.id_mascota == mascota_id) \
            .order_by(desc(HistorialClinico.fecha_evento)) \
            .limit(limit).all()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int) -> List[HistorialClinico]:
        """Obtener eventos del historial por veterinario"""
        return db.query(HistorialClinico).filter(HistorialClinico.id_veterinario == veterinario_id) \
            .order_by(desc(HistorialClinico.fecha_evento)).all()

    def get_by_tipo_evento(self, db: Session, *, tipo_evento: str) -> List[HistorialClinico]:
        """Obtener eventos por tipo"""
        return db.query(HistorialClinico).filter(HistorialClinico.tipo_evento.ilike(f"%{tipo_evento}%")) \
            .order_by(desc(HistorialClinico.fecha_evento)).all()

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[HistorialClinico]:
        """Obtener eventos relacionados a una consulta"""
        return db.query(HistorialClinico).filter(HistorialClinico.id_consulta == consulta_id) \
            .order_by(HistorialClinico.fecha_evento).all()

    def get_by_diagnostico(self, db: Session, *, diagnostico_id: int) -> List[HistorialClinico]:
        """Obtener eventos relacionados a un diagnóstico"""
        return db.query(HistorialClinico).filter(HistorialClinico.id_diagnostico == diagnostico_id) \
            .order_by(HistorialClinico.fecha_evento).all()

    def get_by_tratamiento(self, db: Session, *, tratamiento_id: int) -> List[HistorialClinico]:
        """Obtener eventos relacionados a un tratamiento"""
        return db.query(HistorialClinico).filter(HistorialClinico.id_tratamiento == tratamiento_id) \
            .order_by(HistorialClinico.fecha_evento).all()

    def search_historial(self, db: Session, *, search_params: HistorialSearch) -> Tuple[List[HistorialClinico], int]:
        """Buscar en historial clínico"""
        query = db.query(HistorialClinico).filter(HistorialClinico.id_mascota == search_params.id_mascota)

        if search_params.tipo_evento:
            query = query.filter(HistorialClinico.tipo_evento.ilike(f"%{search_params.tipo_evento}%"))

        if search_params.fecha_desde:
            query = query.filter(HistorialClinico.fecha_evento >= search_params.fecha_desde)

        if search_params.fecha_hasta:
            fecha_hasta_complete = datetime.combine(search_params.fecha_hasta, datetime.max.time())
            query = query.filter(HistorialClinico.fecha_evento <= fecha_hasta_complete)

        total = query.count()

        historial = query.order_by(desc(HistorialClinico.fecha_evento)) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return historial, total

    def add_evento(self, db: Session, *, evento_data: HistorialClinicoCreate) -> HistorialClinico:
        """Agregar evento al historial"""
        evento_dict = evento_data.dict()
        evento_dict['fecha_evento'] = evento_dict.get('fecha_evento', datetime.now())
        return self.create(db, obj_in=evento_dict)

    def add_evento_consulta(self, db: Session, *, mascota_id: int, consulta_id: int, veterinario_id: int,
                            descripcion: str, peso_actual: float = None) -> HistorialClinico:
        """Agregar evento específico de consulta"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_consulta=consulta_id,
            id_veterinario=veterinario_id,
            tipo_evento="Consulta médica",
            descripcion_evento=descripcion,
            peso_momento=peso_actual,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def add_evento_diagnostico(self, db: Session, *, mascota_id: int, diagnostico_id: int,
                               veterinario_id: int, descripcion: str) -> HistorialClinico:
        """Agregar evento específico de diagnóstico"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_diagnostico=diagnostico_id,
            id_veterinario=veterinario_id,
            tipo_evento="Diagnóstico",
            descripcion_evento=descripcion,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def add_evento_tratamiento(self, db: Session, *, mascota_id: int, tratamiento_id: int,
                               veterinario_id: int, descripcion: str) -> HistorialClinico:
        """Agregar evento específico de tratamiento"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_tratamiento=tratamiento_id,
            id_veterinario=veterinario_id,
            tipo_evento="Tratamiento",
            descripcion_evento=descripcion,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def get_resumen_mascota(self, db: Session, *, mascota_id: int) -> Dict[str, Any]:
        """Obtener resumen del historial de una mascota"""
        # Último evento
        ultimo_evento = db.query(HistorialClinico) \
            .filter(HistorialClinico.id_mascota == mascota_id) \
            .order_by(desc(HistorialClinico.fecha_evento)).first()

        # Último peso registrado
        ultimo_peso = db.query(HistorialClinico) \
            .filter(
            and_(
                HistorialClinico.id_mascota == mascota_id,
                HistorialClinico.peso_momento.isnot(None)
            )
        ) \
            .order_by(desc(HistorialClinico.fecha_evento)).first()

        # Conteos por tipo de evento
        tipos_eventos = db.query(
            HistorialClinico.tipo_evento,
            func.count(HistorialClinico.id_historial).label('total')
        ).filter(HistorialClinico.id_mascota == mascota_id) \
            .group_by(HistorialClinico.tipo_evento).all()

        total_eventos = db.query(HistorialClinico).filter(HistorialClinico.id_mascota == mascota_id).count()

        return {
            "total_eventos": total_eventos,
            "ultimo_evento": {
                "fecha": ultimo_evento.fecha_evento if ultimo_evento else None,
                "tipo": ultimo_evento.tipo_evento if ultimo_evento else None,
                "descripcion": ultimo_evento.descripcion_evento if ultimo_evento else None
            },
            "ultimo_peso": float(ultimo_peso.peso_momento) if ultimo_peso and ultimo_peso.peso_momento else None,
            "tipos_eventos": [
                {"tipo": t.tipo_evento, "total": t.total} for t in tipos_eventos
            ]
        }

    def get_cronologia_completa(self, db: Session, *, mascota_id: int) -> List[Dict[str, Any]]:
        """Obtener cronología completa con información relacionada"""
        from app.models.consulta import Consulta
        from app.models.diagnostico import Diagnostico
        from app.models.tratamiento import Tratamiento
        from app.models.veterinario import Veterinario

        # Query complejo con JOINs opcionales
        resultado = db.query(
            HistorialClinico,
            Veterinario.nombre.label('vet_nombre'),
            Veterinario.apellido_paterno.label('vet_apellido'),
            Consulta.tipo_consulta,
            Diagnostico.diagnostico,
            Tratamiento.tipo_tratamiento
        ).outerjoin(Veterinario, HistorialClinico.id_veterinario == Veterinario.id_veterinario) \
            .outerjoin(Consulta, HistorialClinico.id_consulta == Consulta.id_consulta) \
            .outerjoin(Diagnostico, HistorialClinico.id_diagnostico == Diagnostico.id_diagnostico) \
            .outerjoin(Tratamiento, HistorialClinico.id_tratamiento == Tratamiento.id_tratamiento) \
            .filter(HistorialClinico.id_mascota == mascota_id) \
            .order_by(desc(HistorialClinico.fecha_evento)).all()

        cronologia = []
        for r in resultado:
            evento = {
                "id_historial": r.HistorialClinico.id_historial,
                "fecha_evento": r.HistorialClinico.fecha_evento,
                "tipo_evento": r.HistorialClinico.tipo_evento,
                "descripcion_evento": r.HistorialClinico.descripcion_evento,
                "edad_meses": r.HistorialClinico.edad_meses,
                "peso_momento": float(r.HistorialClinico.peso_momento) if r.HistorialClinico.peso_momento else None,
                "observaciones": r.HistorialClinico.observaciones,
                "veterinario": f"{r.vet_nombre} {r.vet_apellido}" if r.vet_nombre else None,
                "tipo_consulta": r.tipo_consulta,
                "diagnostico": r.diagnostico,
                "tipo_tratamiento": r.tipo_tratamiento
            }
            cronologia.append(evento)

        return cronologia

    def get_pesos_historicos(self, db: Session, *, mascota_id: int) -> List[Dict[str, Any]]:
        """Obtener histórico de pesos de una mascota"""
        pesos = db.query(HistorialClinico) \
            .filter(
            and_(
                HistorialClinico.id_mascota == mascota_id,
                HistorialClinico.peso_momento.isnot(None)
            )
        ) \
            .order_by(HistorialClinico.fecha_evento).all()

        return [
            {
                "fecha": evento.fecha_evento,
                "peso": float(evento.peso_momento),
                "edad_meses": evento.edad_meses,
                "tipo_evento": evento.tipo_evento
            }
            for evento in pesos
        ]


# Instancias únicas - TODAS LAS CLASES
solicitud_atencion = CRUDSolicitudAtencion(SolicitudAtencion)
triaje = CRUDTriaje(Triaje)
consulta = CRUDConsulta(Consulta)
diagnostico = CRUDDiagnostico(Diagnostico)
tratamiento = CRUDTratamiento(Tratamiento)
cita = CRUDCita(Cita)
servicio_solicitado = CRUDServicioSolicitado(ServicioSolicitado)
resultado_servicio = CRUDResultadoServicio(ResultadoServicio)
historial_clinico = CRUDHistorialClinico(HistorialClinico)