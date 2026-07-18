# app/crud/consulta_crud.py (VERSIÓN COMPLETA)
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
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
from app.models.servicio import Servicio
from app.models.resultado_servicio import ResultadoServicio
from app.models.movimiento_financiero import MovimientoFinanciero
from app.schemas.consulta_schema import (
    SolicitudAtencionCreate, TriajeCreate, ConsultaCreate,
    DiagnosticoCreate, TratamientoCreate, HistorialClinicoCreate,
    CitaCreate, CitaUpdate, ServicioSolicitadoCreate, ResultadoServicioCreate,
    ConsultaSearch
)


# ===== SOLICITUD ATENCIÓN COMPLETO =====
class CRUDSolicitudAtencion(CRUDBase[SolicitudAtencion, SolicitudAtencionCreate, None]):

    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[SolicitudAtencion]:
        """Obtener solicitudes por mascota"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.id_mascota == mascota_id) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_by_tipo(self, db: Session, *, tipo_solicitud: str) -> List[SolicitudAtencion]:
        """Obtener solicitudes por tipo"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_by_estado(self, db: Session, *, estado: str) -> List[SolicitudAtencion]:
        """Obtener solicitudes por estado"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == estado) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def cambiar_estado(self, db: Session, *, solicitud_id: int, nuevo_estado: str) -> Optional[SolicitudAtencion]:
        """Cambiar estado de la solicitud"""
        solicitud = self.get(db, solicitud_id)
        if solicitud:
            solicitud.estado = nuevo_estado
            db.commit()
            db.refresh(solicitud)
        return solicitud


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

    def get_by_fecha_rango(self, db: Session, *, fecha_inicio: datetime, fecha_fin: datetime) -> List[Triaje]:
        """Obtener triajes dentro de un rango de fechas (inclusivo en ambos extremos)"""
        return db.query(Triaje).filter(
            and_(
                Triaje.fecha_hora_triaje >= fecha_inicio,
                Triaje.fecha_hora_triaje <= fecha_fin
            )
        ).order_by(desc(Triaje.fecha_hora_triaje)).all()

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

    def get_by_tipo(self, db: Session, *, tipo_diagnostico: str) -> List[Diagnostico]:
        """Obtener diagnósticos por tipo"""
        return db.query(Diagnostico).filter(Diagnostico.tipo_diagnostico == tipo_diagnostico) \
            .order_by(desc(Diagnostico.fecha_diagnostico)).all()

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

    def get_by_tipo(self, db: Session, *, tipo_tratamiento: str) -> List[Tratamiento]:
        """Obtener tratamientos por tipo"""
        return db.query(Tratamiento).filter(Tratamiento.tipo_tratamiento == tipo_tratamiento) \
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


# ===== CITA COMPLETO =====
class CRUDCita(CRUDBase[Cita, CitaCreate, CitaUpdate]):

    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[Cita]:
        """Obtener citas de una mascota"""
        return db.query(Cita).filter(Cita.id_mascota == mascota_id) \
            .order_by(desc(Cita.fecha_hora_programada)).all()

    def get_by_estado(self, db: Session, *, estado_cita: str) -> List[Cita]:
        """Obtener citas por estado"""
        return db.query(Cita).filter(Cita.estado_cita == estado_cita) \
            .order_by(Cita.fecha_hora_programada).all()

    def get_por_fecha(self, db: Session, *, fecha: date) -> List[Cita]:
        """Obtener citas de una fecha específica"""
        return db.query(Cita).filter(func.date(Cita.fecha_hora_programada) == fecha) \
            .order_by(Cita.fecha_hora_programada).all()

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

    def marcar_atendida(self, db: Session, *, cita_id: int) -> Optional[Cita]:
        """Marcar cita como atendida y registrar ingreso automaticamente"""
        cita = self.get(db, cita_id)
        if cita and cita.estado_cita == "Programada":
            cita.estado_cita = "Atendida"

            # Obtener el precio del servicio asociado
            monto = 0
            concepto = f"Ingreso por cita #{cita_id}"
            if cita.id_servicio_solicitado:
                ss = db.query(ServicioSolicitado).filter(
                    ServicioSolicitado.id_servicio_solicitado == cita.id_servicio_solicitado
                ).first()
                if ss and ss.id_servicio:
                    servicio = db.query(Servicio).filter(Servicio.id_servicio == ss.id_servicio).first()
                    if servicio:
                        monto = float(servicio.precio)
                        concepto = f"Ingreso por {servicio.nombre_servicio} - Cita #{cita_id}"

            # Registrar movimiento financiero (ingreso automático) SOLO si hay monto.
            # Si la cita no tiene servicio con precio, el monto es 0 y registrarlo
            # ensuciaría el Flujo de Caja / Balance con ingresos vacíos (SC-032 / F13).
            if monto > 0:
                movimiento = MovimientoFinanciero(
                    tipo='Ingreso',
                    categoria='Servicio',
                    monto=monto,
                    concepto=concepto,
                    fecha_movimiento=datetime.now(),
                    id_cita=cita_id
                )
                db.add(movimiento)

            # El commit/refresh se hacen siempre, para persistir estado_cita='Atendida'.
            db.commit()
            db.refresh(cita)
        return cita


# ===== SERVICIO SOLICITADO COMPLETO =====
class CRUDServicioSolicitado(CRUDBase[ServicioSolicitado, ServicioSolicitadoCreate, None]):

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[ServicioSolicitado]:
        """Obtener servicios solicitados de una consulta"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_consulta == consulta_id) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

    def get_by_estado(self, db: Session, *, estado_examen: str) -> List[ServicioSolicitado]:
        """Obtener servicios por estado de examen"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.estado_examen == estado_examen) \
            .order_by(desc(ServicioSolicitado.fecha_solicitado)).all()

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

    def get_by_veterinario(self, db: Session, *, veterinario_id: int) -> List[ResultadoServicio]:
        """Obtener resultados realizados por un veterinario"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.id_veterinario == veterinario_id) \
            .order_by(desc(ResultadoServicio.fecha_realizacion)).all()

    def get_recientes(self, db: Session, *, dias: int = 7) -> List[ResultadoServicio]:
        """Obtener resultados recientes"""
        fecha_limite = date.today() - timedelta(days=dias)
        return db.query(ResultadoServicio).filter(
            func.date(ResultadoServicio.fecha_realizacion) >= fecha_limite
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

    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[HistorialClinico]:
        """Obtener eventos relacionados a una consulta"""
        return db.query(HistorialClinico).filter(HistorialClinico.id_consulta == consulta_id) \
            .order_by(HistorialClinico.fecha_evento).all()

    def add_evento(self, db: Session, *, evento_data: HistorialClinicoCreate) -> HistorialClinico:
        """Agregar evento al historial"""
        evento_dict = evento_data.dict()
        evento_dict['fecha_evento'] = evento_dict.get('fecha_evento', datetime.now())
        return self.create(db, obj_in=evento_dict)

    def add_evento_consulta(self, db: Session, *, mascota_id: int, consulta_id: int, veterinario_id: int,
                            descripcion: str, peso_actual: float = None) -> HistorialClinico:
        """Agregar evento específico de consulta"""
        # Registrar la edad (en meses) que la mascota tenía al momento de la consulta, para
        # que quede visible en el historial. Antes no se guardaba y quedaba siempre NULL.
        from app.models.mascota import Mascota
        mascota_obj = db.query(Mascota).filter(Mascota.id_mascota == mascota_id).first()
        edad_meses_actual = None
        if mascota_obj:
            edad_meses_actual = (mascota_obj.edad_anios or 0) * 12 + (mascota_obj.edad_meses or 0)

        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_consulta=consulta_id,
            id_veterinario=veterinario_id,
            tipo_evento="Consulta médica",
            descripcion_evento=descripcion,
            peso_momento=peso_actual,
            edad_meses=edad_meses_actual,
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