# app/api/v1/endpoints/consultas.py - VERSIÓN CORREGIDA
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, date

from app.config.database import get_db
from app.crud.consulta_crud import (
    consulta, diagnostico, tratamiento, historial_clinico,
    triaje, solicitud_atencion, cita
)
from app.crud.veterinario_crud import veterinario
from app.models import Cita, ResultadoServicio, ServicioSolicitado, Servicio, Veterinario, Mascota, HistorialClinico, \
    Diagnostico, Tratamiento, Patologia
from app.models.consulta import Consulta
from app.models.triaje import Triaje
from app.models.solicitud_atencion import SolicitudAtencion
from app.schemas.consulta_schema import (
    ConsultaCreate, ConsultaResponse, ConsultaSearch,
    DiagnosticoCreate, DiagnosticoResponse,
    TratamientoCreate, TratamientoResponse,
    CitaResponse,
    CitaCreate, ConsultaUpdate, ResultadoServicioResponse, ResultadoServicioCreate, DiagnosticoCompletoUpdate,
)
from app.schemas.base_schema import MessageResponse

router = APIRouter()


# ================================================================
# 1. Crear cita
# ================================================================
@router.post("/cita", response_model=CitaResponse, status_code=status.HTTP_201_CREATED)
async def create_cita(
    cita_data: CitaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva cita programada
    """
    try:
        # Verificar que la mascota existe
        from app.crud.mascota_crud import mascota
        mascota_obj = mascota.get(db, cita_data.id_mascota)
        if not mascota_obj:
            raise HTTPException(
                status_code=400,
                detail="Mascota no encontrada"
            )

        # Verificar que el servicio solicitado existe
        if cita_data.id_servicio_solicitado:
            from app.crud.consulta_crud import servicio_solicitado
            servicio_obj = servicio_solicitado.get(db, cita_data.id_servicio_solicitado)
            if not servicio_obj:
                raise HTTPException(
                    status_code=400,
                    detail="Servicio solicitado no encontrado"
                )

        # Verificar que el veterinario asignado existe (SC-016 / F4).
        # El campo es opcional: si no se envía, la cita queda sin asignar.
        if cita_data.id_veterinario:
            vet_obj = veterinario.get(db, cita_data.id_veterinario)
            if not vet_obj:
                raise HTTPException(
                    status_code=400,
                    detail="Veterinario no encontrado"
                )

        # Crear la cita
        cita_dict = cita_data.dict()
        cita_dict["estado_cita"] = "Programada"
        nueva_cita = cita.create(db, obj_in=cita_dict)

        return nueva_cita

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear cita: {str(e)}"
        )

# ================================================================
# 2. Obtener lista de citas
# ================================================================
@router.get("/cita", response_model=List[CitaResponse])
async def get_citas(
    db: Session = Depends(get_db),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    mascota_id: Optional[int] = Query(None, description="Filtrar por mascota"),
    servicio_solicitado_id: Optional[int] = Query(None, description="Filtrar por servicio solicitado"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener lista de citas
    """
    try:
        if estado:
            citas = cita.get_by_estado(db, estado_cita=estado)
        elif mascota_id:
            citas = cita.get_by_mascota(db, mascota_id=mascota_id)
        elif servicio_solicitado_id:
            citas = db.query(cita.model).filter(
                cita.model.id_servicio_solicitado == servicio_solicitado_id
            ).order_by(cita.model.fecha_hora_programada).limit(limit).all()
        else:
            citas = cita.get_multi(db, limit=limit)

        return citas[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener citas: {str(e)}"
        )

# ================================================================
# 3. Obtener cita por ID
# ================================================================
@router.get("/cita/{cita_id}", response_model=CitaResponse)
async def get_cita(
    cita_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener una cita específica por ID
    """
    try:
        cita_obj = cita.get(db, cita_id)
        if not cita_obj:
            raise HTTPException(
                status_code=404,
                detail="Cita no encontrada"
            )
        return cita_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener cita: {str(e)}"
        )

@router.get("/citas/enriquecidas")
async def get_citas_enriquecidas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Buscar por nombre de mascota"),
    estado: Optional[str] = Query(None, description="Filtrar por estado de la cita"),
):
    """
    Lista de citas ya enriquecida (mascota, servicio y veterinario) resuelta en UNA sola
    consulta con JOINs, paginada y filtrada en el servidor.

    Reemplaza el patrón N+1 del frontend (1 + N*3 peticiones HTTP: mascota, servicio y
    veterinario por cada fila) por una única respuesta. Todos los JOIN son a filas únicas
    (claves), así que no hay riesgo de multiplicar filas.
    """
    try:
        nombre_vet = func.concat_ws(" ", Veterinario.nombre, Veterinario.apellido_paterno)

        query = (
            db.query(
                Cita,
                Mascota.nombre.label("nombre_mascota"),
                Servicio.nombre_servicio.label("nombre_servicio"),
                nombre_vet.label("nombre_veterinario"),
            )
            .join(Mascota, Mascota.id_mascota == Cita.id_mascota)
            .outerjoin(
                ServicioSolicitado,
                ServicioSolicitado.id_servicio_solicitado == Cita.id_servicio_solicitado,
            )
            .outerjoin(Servicio, Servicio.id_servicio == ServicioSolicitado.id_servicio)
            .outerjoin(Veterinario, Veterinario.id_veterinario == Cita.id_veterinario)
        )

        if estado:
            query = query.filter(Cita.estado_cita == estado)
        if search and search.strip():
            query = query.filter(Mascota.nombre.ilike(f"%{search.strip()}%"))

        total = query.count()

        # Orden: la cita más reciente (recién creada) primero. Cita no tiene timestamp de
        # creación, así que se usa id_cita desc como proxy — igual criterio "lo último
        # primero" que el listado de solicitudes.
        rows = (
            query.order_by(Cita.id_cita.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        citas = [
            {
                "id_cita": c.id_cita,
                "id_mascota": c.id_mascota,
                "id_servicio_solicitado": c.id_servicio_solicitado,
                "id_veterinario": c.id_veterinario,
                "fecha_hora_programada": c.fecha_hora_programada,
                "estado_cita": c.estado_cita,
                "requiere_ayuno": c.requiere_ayuno,
                "observaciones": c.observaciones,
                "nombre_mascota": nombre_mascota or "Desconocida",
                "nombre_servicio": nombre_servicio or "Sin servicio",
                "nombre_veterinario": (nombre_veterinario or "").strip() or "Sin asignar",
            }
            for c, nombre_mascota, nombre_servicio, nombre_veterinario in rows
        ]

        return {
            "citas": citas,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener citas enriquecidas: {str(e)}"
        )


@router.patch("/cita/{cita_id}/atender", response_model=CitaResponse)
async def atender_cita(
    cita_id: int,
    db: Session = Depends(get_db)
):
    """
    Marcar cita como atendida y registrar ingreso automaticamente (HU-13)
    """
    try:
        cita_obj = cita.get(db, cita_id)
        if not cita_obj:
            raise HTTPException(
                status_code=404,
                detail="Cita no encontrada"
            )
        if cita_obj.estado_cita != "Programada":
            raise HTTPException(
                status_code=400,
                detail=f"La cita esta en estado '{cita_obj.estado_cita}', solo se puede atender citas programadas"
            )

        cita_atendida = cita.marcar_atendida(db, cita_id=cita_id)
        return cita_atendida

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al atender cita: {str(e)}"
        )


@router.delete("/cita/{cita_id}")
async def delete_cita(
        cita_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar una cita
    """
    cita_obj = cita.get(db, cita_id)
    if not cita_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    # SC-039 / SC-044 (F20 / F28): no borrar una cita con dependientes. La cascada del
    # ORM eliminaba el Resultado_servicio en silencio (pérdida del registro clínico), y
    # el Movimiento_Financiero (FK NO ACTION) hacía fallar el borrado con 500.
    from app.models.movimiento_financiero import MovimientoFinanciero
    dependientes = []
    if db.query(ResultadoServicio).filter(ResultadoServicio.id_cita == cita_id).first():
        dependientes.append("un resultado de servicio")
    if db.query(MovimientoFinanciero).filter(MovimientoFinanciero.id_cita == cita_id).first():
        dependientes.append("un movimiento financiero")
    if dependientes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar la cita: tiene {' y '.join(dependientes)} asociado(s).",
        )

    cita.remove(db, id=cita_id)
    return {"message": "Cita eliminada correctamente", "success": True}


@router.get("/search")
async def search_consultas_endpoint(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        id_veterinario: Optional[int] = Query(None, description="Filtrar por veterinario"),
        fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
        fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
        condicion_general: Optional[str] = Query(None, description="Filtrar por condición"),
        es_seguimiento: Optional[bool] = Query(None, description="Filtrar seguimientos")
):
    """
    Buscar consultas con filtros avanzados
    """
    try:
        search_params = ConsultaSearch(
            id_veterinario=id_veterinario,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            condicion_general=condicion_general,
            es_seguimiento=es_seguimiento,
            page=page,
            per_page=per_page
        )

        consultas_result, total = consulta.search_consultas(db, search_params=search_params)

        return {
            "consultas": consultas_result,
            "total": total,
            "page": search_params.page,
            "per_page": search_params.per_page,
            "total_pages": (total + search_params.per_page - 1) // search_params.per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de consultas: {str(e)}"
        )


@router.get("/estadisticas/resumen")
async def get_estadisticas_consultas(
        db: Session = Depends(get_db),
        fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
        fecha_hasta: Optional[date] = Query(None, description="Fecha hasta")
):
    """
    Obtener estadísticas de consultas
    """
    try:
        # Estadísticas por condición general
        stats_condicion = consulta.get_estadisticas_por_condicion(db)

        # Consultas de seguimiento
        seguimientos = consulta.get_seguimientos(db)

        # Si hay rango de fechas, filtrar consultas por fecha
        if fecha_desde and fecha_hasta:
            search_params = ConsultaSearch(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                page=1,
                per_page=1000  # Para obtener todas y contar
            )
            consultas_periodo, total_periodo = consulta.search_consultas(db, search_params=search_params)
        else:
            total_periodo = db.query(Consulta).count()

        # Diagnósticos más frecuentes
        diagnosticos_frecuentes = diagnostico.get_mas_frecuentes(db, limit=5)

        return {
            "periodo": {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "total_consultas": total_periodo
            },
            "estadisticas_condicion": stats_condicion,
            "total_seguimientos": len(seguimientos),
            "diagnosticos_frecuentes": diagnosticos_frecuentes
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/hoy/agenda")
async def get_consultas_hoy(
        db: Session = Depends(get_db)
):
    """
    Obtener consultas del día actual
    """
    try:
        hoy = date.today()
        consultas_hoy = consulta.get_por_fecha(db, fecha=hoy)

        # Organizar por veterinario
        consultas_por_veterinario = {}
        for c in consultas_hoy:
            vet_id = c.id_veterinario
            if vet_id not in consultas_por_veterinario:
                vet_obj = veterinario.get(db, vet_id)
                consultas_por_veterinario[vet_id] = {
                    "veterinario": f"{vet_obj.nombre} {vet_obj.apellido_paterno}" if vet_obj else "Desconocido",
                    "consultas": []
                }
            consultas_por_veterinario[vet_id]["consultas"].append(c)

        return {
            "fecha": hoy,
            "total_consultas": len(consultas_hoy),
            "consultas_por_veterinario": list(consultas_por_veterinario.values()),
            "consultas_detalle": consultas_hoy
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consultas de hoy: {str(e)}"
        )


@router.get("/veterinario/{veterinario_id}")
async def get_consultas_by_veterinario(
        veterinario_id: int,
        db: Session = Depends(get_db),
        fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
        fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener consultas realizadas por un veterinario
    """
    try:
        # Verificar que el veterinario existe
        veterinario_obj = veterinario.get(db, veterinario_id)
        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        consultas_list = consulta.get_by_veterinario(
            db,
            veterinario_id=veterinario_id,
            fecha_inicio=fecha_desde,
            fecha_fin=fecha_hasta
        )

        # Limitar resultados
        consultas_list = consultas_list[:limit]

        return {
            "veterinario": {
                "id_veterinario": veterinario_obj.id_veterinario,
                "nombre": f"{veterinario_obj.nombre} {veterinario_obj.apellido_paterno}"
            },
            "consultas": consultas_list,
            "total": len(consultas_list),
            "filtros": {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consultas del veterinario: {str(e)}"
        )


# ===== RUTAS GENERALES (DESPUÉS DE LAS ESPECÍFICAS) =====

@router.post("/", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
async def create_consulta(
        consulta_data: ConsultaCreate,
        db: Session = Depends(get_db)
):
    """
    Crear una nueva consulta médica
    """
    try:
        # Verificar que el triaje existe
        triaje_obj = triaje.get(db, consulta_data.id_triaje)
        if not triaje_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Triaje no encontrado"
            )

        # Verificar que el veterinario existe y está disponible
        veterinario_obj = veterinario.get(db, consulta_data.id_veterinario)
        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Veterinario no encontrado"
            )

        # Verificar que no existe ya una consulta para este triaje
        consulta_existente = consulta.get_by_triaje(db, triaje_id=consulta_data.id_triaje)
        if consulta_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una consulta para este triaje"
            )

        # Agregar timestamp actual si no se proporciona
        consulta_dict = consulta_data.dict()
        consulta_dict['fecha_consulta'] = consulta_dict.get('fecha_consulta', datetime.now())

        # Crear la consulta
        nueva_consulta = consulta.create(db, obj_in=consulta_dict)

        # Cambiar disposición del veterinario a ocupado
        veterinario.cambiar_disposicion(
            db,
            veterinario_id=consulta_data.id_veterinario,
            nueva_disposicion="Ocupado"
        )

        # Cambiar estado de la solicitud de atención a "En atencion"
        solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud)
        if solicitud_obj:
            solicitud_atencion.cambiar_estado(
                db,
                solicitud_id=triaje_obj.id_solicitud,
                nuevo_estado="En atencion"
            )

        # Agregar evento al historial clínico
        if solicitud_obj:
            historial_clinico.add_evento_consulta(
                db,
                mascota_id=solicitud_obj.id_mascota,
                consulta_id=nueva_consulta.id_consulta,
                veterinario_id=consulta_data.id_veterinario,
                descripcion=f"Consulta: {consulta_data.tipo_consulta}. Motivo: {consulta_data.motivo_consulta or 'No especificado'}",
                peso_actual=float(triaje_obj.peso_mascota) if triaje_obj.peso_mascota else None
            )

        return nueva_consulta

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear consulta: {str(e)}"
        )


@router.get("/")
async def get_consultas(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        id_veterinario: Optional[int] = Query(None, description="Filtrar por veterinario"),
        fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
        fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
        condicion_general: Optional[str] = Query(None, description="Filtrar por condición"),
        es_seguimiento: Optional[bool] = Query(None, description="Filtrar seguimientos")
):
    """
    Obtener lista de consultas con paginación y filtros
    """
    try:
        search_params = ConsultaSearch(
            id_veterinario=id_veterinario,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            condicion_general=condicion_general,
            es_seguimiento=es_seguimiento,
            page=page,
            per_page=per_page
        )

        consultas_result, total = consulta.search_consultas(db, search_params=search_params)

        return {
            "consultas": consultas_result,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consultas: {str(e)}"
        )


@router.get("/triaje/{id_triaje}")
async def get_consulta_by_triaje(id_triaje: int, db: Session = Depends(get_db)):
    """
    Obtener la consulta asociada a un triaje (SC-040 / F21).

    Reemplaza el patrón del frontend de traer la primera página de /consultas/ y
    filtrar en memoria (se rompía al superar 20 consultas y no encontrar la del
    triaje en esa página). Retorna la consulta del triaje, o null (200) si el
    triaje aún no tiene consulta.
    """
    try:
        return consulta.get_by_triaje(db, triaje_id=id_triaje)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la consulta del triaje: {str(e)}"
        )


@router.put("/{consulta_id}", response_model=ConsultaResponse)
async def update_consulta(
        consulta_id: int,
        consulta_data: ConsultaUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar una recepcionista existente
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=404,
                detail="Consulta no encontrada"
            )


        # Actualizar la recepcionista
        consulta_actualizada = consulta.update(db, db_obj=consulta_obj, obj_in=consulta_data)

        # SC-043 / F26: registrar el evento de consulta en el historial clínico. El PUT
        # se llama en cada guardado, así que se agrega una sola vez por consulta. El
        # historial es complementario: si falla, no debe romper el guardado.
        try:
            if not historial_clinico.get_by_consulta(db, consulta_id=consulta_id):
                triaje_obj = triaje.get(db, consulta_obj.id_triaje)
                solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud) if triaje_obj else None
                if solicitud_obj:
                    historial_clinico.add_evento_consulta(
                        db,
                        mascota_id=solicitud_obj.id_mascota,
                        consulta_id=consulta_id,
                        veterinario_id=consulta_obj.id_veterinario,
                        descripcion=consulta_actualizada.motivo_consulta
                        or consulta_actualizada.tipo_consulta
                        or "Consulta médica",
                    )
        except Exception:
            pass

        # SC-018 / F23: al guardar la consulta, la solicitud avanza a "En atencion"
        # (solo desde "Pendiente"/"En triaje"). Con esto el trigger de liberación del
        # veterinario (En atencion -> Completada) ya se dispara al finalizar.
        try:
            triaje_obj = triaje.get(db, consulta_obj.id_triaje)
            if triaje_obj:
                solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud)
                if solicitud_obj and solicitud_obj.estado in ("Pendiente", "En triaje"):
                    solicitud_atencion.cambiar_estado(
                        db, solicitud_id=triaje_obj.id_solicitud, nuevo_estado="En atencion"
                    )
        except Exception:
            pass

        return consulta_actualizada

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar consulta: {str(e)}"
        )

# ===== RUTAS CON PARÁMETROS AL FINAL =====

@router.get("/{consulta_id}", response_model=ConsultaResponse)
async def get_consulta(
        consulta_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener una consulta específica por ID
    """
    try:
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )
        return consulta_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consulta: {str(e)}"
        )


@router.get("/{consulta_id}/completa")
async def get_consulta_completa(
        consulta_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener consulta con toda la información relacionada (triaje, diagnósticos, tratamientos)
    """
    try:
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        # Obtener triaje relacionado
        triaje_obj = triaje.get(db, consulta_obj.id_triaje)

        # Obtener solicitud de atención
        solicitud_obj = None
        if triaje_obj:
            solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud)

        # Obtener diagnósticos de la consulta
        diagnosticos_list = diagnostico.get_by_consulta(db, consulta_id=consulta_id)

        # Obtener tratamientos de la consulta
        tratamientos_list = tratamiento.get_by_consulta(db, consulta_id=consulta_id)

        # Obtener veterinario
        veterinario_obj = veterinario.get(db, consulta_obj.id_veterinario)

        # Obtener historial relacionado
        historial_list = historial_clinico.get_by_consulta(db, consulta_id=consulta_id)

        return {
            "consulta": consulta_obj,
            "triaje": {
                "id_triaje": triaje_obj.id_triaje if triaje_obj else None,
                "clasificacion_urgencia": triaje_obj.clasificacion_urgencia if triaje_obj else None,
                "peso_mascota": float(triaje_obj.peso_mascota) if triaje_obj and triaje_obj.peso_mascota else None,
                "temperatura": float(triaje_obj.temperatura) if triaje_obj and triaje_obj.temperatura else None,
                "condicion_corporal": triaje_obj.condicion_corporal if triaje_obj else None
            },
            "solicitud": {
                "id_solicitud": solicitud_obj.id_solicitud if solicitud_obj else None,
                "id_mascota": solicitud_obj.id_mascota if solicitud_obj else None,
                "tipo_solicitud": solicitud_obj.tipo_solicitud if solicitud_obj else None,
                "estado": solicitud_obj.estado if solicitud_obj else None
            },
            "veterinario": {
                "id_veterinario": veterinario_obj.id_veterinario if veterinario_obj else None,
                "nombre_completo": f"{veterinario_obj.nombre} {veterinario_obj.apellido_paterno}" if veterinario_obj else None,
                "especialidad_id": veterinario_obj.id_especialidad if veterinario_obj else None
            },
            "diagnosticos": diagnosticos_list,
            "tratamientos": tratamientos_list,
            "eventos_historial": historial_list
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consulta completa: {str(e)}"
        )


@router.post("/{consulta_id}/diagnosticos", response_model=DiagnosticoResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnostico(
        consulta_id: int,
        diagnostico_data: DiagnosticoCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un diagnóstico para una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        # Verificar que la patología existe
        from app.crud.catalogo_crud import patologia
        patologia_obj = patologia.get(db, diagnostico_data.id_patologia)
        if not patologia_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patología no encontrada"
            )

        # Actualizar el id_consulta con el de la URL
        diagnostico_data.id_consulta = consulta_id

        # Agregar timestamp actual
        diagnostico_dict = diagnostico_data.dict()
        diagnostico_dict['fecha_diagnostico'] = diagnostico_dict.get('fecha_diagnostico', datetime.now())

        # Crear el diagnóstico
        nuevo_diagnostico = diagnostico.create(db, obj_in=diagnostico_dict)

        # Agregar evento al historial clínico
        # Obtener ID de mascota
        triaje_obj = triaje.get(db, consulta_obj.id_triaje)
        if triaje_obj:
            solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud)
            if solicitud_obj:
                historial_clinico.add_evento_diagnostico(
                    db,
                    mascota_id=solicitud_obj.id_mascota,
                    diagnostico_id=nuevo_diagnostico.id_diagnostico,
                    veterinario_id=consulta_obj.id_veterinario,
                    descripcion=f"Diagnóstico {diagnostico_data.tipo_diagnostico}: {diagnostico_data.diagnostico}"
                )

        return nuevo_diagnostico

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear diagnóstico: {str(e)}"
        )


@router.post("/{consulta_id}/tratamientos", response_model=TratamientoResponse, status_code=status.HTTP_201_CREATED)
async def create_tratamiento(
        consulta_id: int,
        tratamiento_data: TratamientoCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un tratamiento para una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        # Actualizar el id_consulta con el de la URL
        tratamiento_data.id_consulta = consulta_id

        # Crear el tratamiento
        nuevo_tratamiento = tratamiento.create(db, obj_in=tratamiento_data)

        # Agregar evento al historial clínico
        triaje_obj = triaje.get(db, consulta_obj.id_triaje)
        if triaje_obj:
            solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud)
            if solicitud_obj:
                historial_clinico.add_evento_tratamiento(
                    db,
                    mascota_id=solicitud_obj.id_mascota,
                    tratamiento_id=nuevo_tratamiento.id_tratamiento,
                    veterinario_id=consulta_obj.id_veterinario,
                    descripcion=f"Tratamiento {tratamiento_data.tipo_tratamiento} iniciado para patología"
                )

        return nuevo_tratamiento

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tratamiento: {str(e)}"
        )


@router.get("/{consulta_id}/diagnosticos")
async def get_diagnosticos_consulta(
        consulta_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todos los diagnósticos de una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        diagnosticos_list = diagnostico.get_by_consulta(db, consulta_id=consulta_id)

        return {
            "consulta_id": consulta_id,
            "diagnosticos": diagnosticos_list,
            "total": len(diagnosticos_list)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener diagnósticos: {str(e)}"
        )


@router.get("/{consulta_id}/tratamientos")
async def get_tratamientos_consulta(
        consulta_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todos los tratamientos de una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        tratamientos_list = tratamiento.get_by_consulta(db, consulta_id=consulta_id)

        return {
            "consulta_id": consulta_id,
            "tratamientos": tratamientos_list,
            "total": len(tratamientos_list)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tratamientos: {str(e)}"
        )


@router.patch("/{consulta_id}/finalizar", response_model=MessageResponse)
async def finalizar_consulta(
        consulta_id: int,
        db: Session = Depends(get_db)
):
    """
    Finalizar una consulta médica
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        # Liberar al veterinario
        veterinario.cambiar_disposicion(
            db,
            veterinario_id=consulta_obj.id_veterinario,
            nueva_disposicion="Libre"
        )

        # Cambiar estado de la solicitud a "Completada"
        triaje_obj = triaje.get(db, consulta_obj.id_triaje)
        if triaje_obj:
            solicitud_atencion.cambiar_estado(
                db,
                solicitud_id=triaje_obj.id_solicitud,
                nuevo_estado="Completada"
            )

        return {
            "message": "Consulta finalizada exitosamente",
            "success": True,
            "consulta_id": consulta_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al finalizar consulta: {str(e)}"
        )

@router.get("/historial/{mascota_id}")
async def get_historial_clinico_mascota(
    mascota_id: int,
    db: Session = Depends(get_db),
    fecha_desde: Optional[date] = Query(None, description="Filtrar eventos desde esta fecha (inclusive)"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar eventos hasta esta fecha (inclusive)"),
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de eventos")
):
    """
    Obtener historial clínico de una mascota, ordenado por fecha de evento descendente,
    incluyendo el veterinario responsable de cada evento.
    Permite filtrar opcionalmente por rango de fechas (fecha_hasta es inclusiva).
    Si la mascota no tiene eventos, retorna una lista vacía (HTTP 200).
    """
    try:
        query = db.query(HistorialClinico, Veterinario) \
            .outerjoin(Veterinario, HistorialClinico.id_veterinario == Veterinario.id_veterinario) \
            .filter(HistorialClinico.id_mascota == mascota_id)

        if fecha_desde:
            query = query.filter(HistorialClinico.fecha_evento >= fecha_desde)
        if fecha_hasta:
            # Incluir todos los eventos del día 'fecha_hasta' (hasta las 23:59:59)
            fecha_hasta_completa = datetime.combine(fecha_hasta, datetime.max.time())
            query = query.filter(HistorialClinico.fecha_evento <= fecha_hasta_completa)

        resultados = query.order_by(desc(HistorialClinico.fecha_evento)).limit(limit).all()

        return [
            {
                "id_historial": e.id_historial,
                "fecha_evento": e.fecha_evento,
                "tipo_evento": e.tipo_evento,
                "edad_meses": e.edad_meses,
                "descripcion_evento": e.descripcion_evento,
                "peso_momento": float(e.peso_momento) if e.peso_momento else None,
                "observaciones": e.observaciones,
                "veterinario": f"{v.nombre} {v.apellido_paterno}" if v else None
            }
            for e, v in resultados
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial clínico: {str(e)}"
        )


@router.get("/historialConsultas/{mascota_id}", response_model=List[dict])
async def get_historial_clinico_mascota(
    mascota_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de eventos")
):
    """
    Obtener historial clínico de una mascota y sus consultas
    """
    try:
        # Consultar las consultas relacionadas con la mascota, pasando por la cadena
        # correcta: Consulta -> Triaje -> Solicitud_atencion -> Mascota.
        # (Antes se cruzaba SolicitudAtencion.id_solicitud == Consulta.id_triaje, lo que
        # comparaba un id de solicitud con un id de triaje y solo coincidía por casualidad
        # en los registros donde ambos ids eran iguales.)
        eventos = db.query(Consulta) \
            .join(Triaje, Triaje.id_triaje == Consulta.id_triaje) \
            .join(SolicitudAtencion, SolicitudAtencion.id_solicitud == Triaje.id_solicitud) \
            .filter(SolicitudAtencion.id_mascota == mascota_id) \
            .order_by(Consulta.fecha_consulta.desc()) \
            .limit(limit).all()

        # Si la mascota no tiene consultas, devolver lista vacía (HTTP 200) en lugar
        # de 404, para que el front muestre un historial vacío y no un error.
        # Mapear los eventos para devolverlos en el formato adecuado
        return [
            {
                "id_consulta": e.id_consulta,
                "fecha_consulta": e.fecha_consulta,
                "tipo_consulta": e.tipo_consulta,
                "motivo_consulta": e.motivo_consulta,
                "diagnostico_preliminar": e.diagnostico_preliminar,
                "observaciones": e.observaciones
            }
            for e in eventos
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consultas: {str(e)}"
        )


@router.get("/historialDetallado/{mascota_id}", response_model=List[dict])
async def get_historial_detallado_mascota(
    mascota_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de consultas")
):
    """
    Historial clínico detallado por consulta de una mascota. Por cada consulta devuelve sus
    datos clínicos + el evento de historial asociado (edad, peso, observaciones) + los
    diagnósticos con su patología (nombre, tipo, estado, gravedad, contagiosa/crónica).
    Alimenta el panel interactivo y el detalle de diagnóstico del modal de Historial Clínico.
    """
    try:
        # Consultas de la mascota, por la cadena Consulta -> Triaje -> Solicitud_atencion -> Mascota.
        consultas = db.query(Consulta, Veterinario) \
            .join(Triaje, Triaje.id_triaje == Consulta.id_triaje) \
            .join(SolicitudAtencion, SolicitudAtencion.id_solicitud == Triaje.id_solicitud) \
            .outerjoin(Veterinario, Veterinario.id_veterinario == Consulta.id_veterinario) \
            .filter(SolicitudAtencion.id_mascota == mascota_id) \
            .order_by(Consulta.fecha_consulta.desc()) \
            .limit(limit).all()

        resultado = []
        for cons, vet in consultas:
            # Evento de historial de esta consulta (peso/edad/observaciones registrados al atender).
            evento = db.query(HistorialClinico) \
                .filter(HistorialClinico.id_consulta == cons.id_consulta) \
                .order_by(HistorialClinico.fecha_evento) \
                .first()

            # Diagnósticos de la consulta, con la patología asociada.
            diags = db.query(Diagnostico, Patologia) \
                .outerjoin(Patologia, Patologia.id_patologia == Diagnostico.id_patologia) \
                .filter(Diagnostico.id_consulta == cons.id_consulta) \
                .order_by(Diagnostico.fecha_diagnostico) \
                .all()

            diagnosticos = [
                {
                    "id_diagnostico": d.id_diagnostico,
                    "diagnostico": d.diagnostico,
                    "tipo_diagnostico": d.tipo_diagnostico,
                    "estado_patologia": d.estado_patologia,
                    "fecha_diagnostico": d.fecha_diagnostico,
                    "patologia": {
                        "nombre": p.nombre_patologia,
                        "gravedad": p.gravedad,
                        "especie_afecta": p.especie_afecta,
                        "es_contagiosa": p.es_contagiosa,
                        "es_cronica": p.es_crónica,
                    } if p else None,
                }
                for d, p in diags
            ]

            resultado.append({
                "id_consulta": cons.id_consulta,
                "fecha_consulta": cons.fecha_consulta,
                "tipo_consulta": cons.tipo_consulta,
                "motivo_consulta": cons.motivo_consulta,
                "sintomas_observados": cons.sintomas_observados,
                "diagnostico_preliminar": cons.diagnostico_preliminar,
                "observaciones": cons.observaciones,
                "condicion_general": cons.condicion_general,
                "es_seguimiento": cons.es_seguimiento,
                "veterinario": f"{vet.nombre} {vet.apellido_paterno}" if vet else None,
                "edad_meses": evento.edad_meses if evento else None,
                "peso_momento": float(evento.peso_momento) if evento and evento.peso_momento else None,
                "observaciones_historial": evento.observaciones if evento else None,
                "diagnosticos": diagnosticos,
            })

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial detallado: {str(e)}"
        )


@router.get("/citaServicio/{cita_id}")
async def get_cita_by_id(cita_id: int, db: Session = Depends(get_db)):
    try:
        # Importar los modelos necesarios
        from app.models.cita import Cita
        from app.models.servicio import Servicio
        from app.models.servicio_solicitado import ServicioSolicitado  # Asegúrate de importar este modelo

        # Realizar la consulta para obtener la cita con el nombre del servicio
        cita_obj = db.query(Cita, Servicio.nombre_servicio) \
            .join(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio) \
            .filter(Cita.id_cita == cita_id).first()

        if not cita_obj:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        # Devolver la respuesta con los detalles de la cita y el nombre del servicio
        return {
            "id_cita": cita_obj.Cita.id_cita,
            "fecha_hora_programada": cita_obj.Cita.fecha_hora_programada,
            "estado_cita": cita_obj.Cita.estado_cita,
            "nombre_servicio": cita_obj.nombre_servicio  # Nombre del servicio asociado
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cita: {str(e)}")

@router.get("/citaVeterinario/{cita_id}")
async def get_cita_by_id(cita_id: int, db: Session = Depends(get_db)):
    try:
        # Obtener la cita con el servicio asociado y veterinario
        cita = db.query(
                Cita.id_cita,
                Cita.fecha_hora_programada,
                Cita.estado_cita,
                Servicio.nombre_servicio,
                Veterinario.nombre.label("veterinario_nombre"),
                Veterinario.apellido_paterno.label("veterinario_apellido")
            ) \
            .join(ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio) \
            .join(ResultadoServicio, ResultadoServicio.id_cita == Cita.id_cita) \
            .join(Veterinario, ResultadoServicio.id_veterinario == Veterinario.id_veterinario) \
            .filter(Cita.id_cita == cita_id) \
            .first()

        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        return {
            "id_cita": cita.id_cita,
            "fecha_hora_programada": cita.fecha_hora_programada,
            "estado_cita": cita.estado_cita,
            "nombre_servicio": cita.nombre_servicio,
            "veterinario": f"{cita.veterinario_nombre} {cita.veterinario_apellido}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cita: {str(e)}")

@router.get("/citaMascota/{cita_id}")
async def get_mascota_from_cita(cita_id: int, db: Session = Depends(get_db)):
    try:
        # Realizar el JOIN entre la tabla Cita y Mascota
        result = db.query(Cita.id_cita, Mascota.nombre).join(Mascota, Cita.id_mascota == Mascota.id_mascota) \
            .filter(Cita.id_cita == cita_id).first()

        if not result:
            raise HTTPException(status_code=404, detail="Cita o mascota no encontrada")

        return {
            "id_cita": result.id_cita,
            "nombre_mascota": result.nombre
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cita: {str(e)}")


@router.get("/resultado_servicio/{cita_id}", response_model=ResultadoServicioResponse)
async def get_resultado_servicio(cita_id: int, db: Session = Depends(get_db)):
    # Buscar el resultado del servicio para la cita específica
    resultado_servicio = db.query(ResultadoServicio).filter(ResultadoServicio.id_cita == cita_id).first()

    if not resultado_servicio:
        raise HTTPException(status_code=404, detail="Resultado del servicio no encontrado para esta cita")

    return ResultadoServicioResponse(
        id_resultado=resultado_servicio.id_resultado,
        id_cita=resultado_servicio.id_cita,
        id_veterinario=resultado_servicio.id_veterinario,
        resultado=resultado_servicio.resultado,
        interpretacion=resultado_servicio.interpretacion,
        archivo_adjunto=resultado_servicio.archivo_adjunto,
        fecha_realizacion=resultado_servicio.fecha_realizacion
    )

@router.put("/resultado_servicio/{cita_id}", response_model=ResultadoServicioResponse)
async def update_resultado_servicio(cita_id: int, resultado_servicio_update: ResultadoServicioCreate, db: Session = Depends(get_db)):
    # Buscar el resultado del servicio para la cita específica
    resultado_servicio = db.query(ResultadoServicio).filter(ResultadoServicio.id_cita == cita_id).first()

    if not resultado_servicio:
        raise HTTPException(status_code=404, detail="Resultado del servicio no encontrado para esta cita")

    # Actualizar los campos del resultado de servicio
    resultado_servicio.resultado = resultado_servicio_update.resultado
    resultado_servicio.interpretacion = resultado_servicio_update.interpretacion
    resultado_servicio.archivo_adjunto = resultado_servicio_update.archivo_adjunto
    resultado_servicio.fecha_realizacion = resultado_servicio_update.fecha_realizacion

    # Marcar cita como atendida y registrar ingreso automaticamente (HU-13)
    from app.crud.consulta_crud import cita as cita_crud
    cita_crud.marcar_atendida(db, cita_id=cita_id)

    # SC-042 / F24: al registrar el resultado, el examen avanza a 'Completado'.
    cita_obj = db.query(Cita).filter(Cita.id_cita == cita_id).first()
    if cita_obj and cita_obj.id_servicio_solicitado:
        ss = db.query(ServicioSolicitado).filter(
            ServicioSolicitado.id_servicio_solicitado == cita_obj.id_servicio_solicitado
        ).first()
        if ss:
            ss.estado_examen = 'Completado'

    db.commit()
    db.refresh(resultado_servicio)

    return ResultadoServicioResponse(
        id_resultado=resultado_servicio.id_resultado,
        id_cita=resultado_servicio.id_cita,
        id_veterinario=resultado_servicio.id_veterinario,
        resultado=resultado_servicio.resultado,
        interpretacion=resultado_servicio.interpretacion,
        archivo_adjunto=resultado_servicio.archivo_adjunto,
        fecha_realizacion=resultado_servicio.fecha_realizacion
    )


@router.post("/resultado_servicio/{cita_id}/adjunto")
async def subir_adjunto_resultado(
    cita_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Subir el archivo adjunto de un resultado de servicio a Google Drive (SC-020 / F27)
    y guardar el enlace resultante en archivo_adjunto.

    Requiere configurar GOOGLE_SERVICE_ACCOUNT_JSON (y opcionalmente GDRIVE_FOLDER_ID);
    si Drive no está configurado, responde 503 con un mensaje claro.
    """
    resultado_servicio = db.query(ResultadoServicio).filter(
        ResultadoServicio.id_cita == cita_id
    ).first()
    if not resultado_servicio:
        raise HTTPException(
            status_code=404,
            detail="Resultado del servicio no encontrado para esta cita",
        )

    from app.services.storage import drive_service

    try:
        contenido = await archivo.read()
        enlace = drive_service.subir_archivo(contenido, archivo.filename, archivo.content_type)
    except RuntimeError as e:
        # Drive no configurado o falta la librería.
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el adjunto: {str(e)}")

    resultado_servicio.archivo_adjunto = enlace
    db.commit()
    db.refresh(resultado_servicio)

    return {"archivo_adjunto": enlace}


@router.get("/diagnosticos/{id_consulta}", response_model=List[DiagnosticoResponse])
async def get_diagnosticos_by_consulta(
        id_consulta: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todos los diagnósticos relacionados con una consulta específica.
    """
    try:
        # Realizar la consulta para obtener todos los diagnósticos relacionados con la consulta
        diagnosticos = db.query(Diagnostico).filter(Diagnostico.id_consulta == id_consulta).all()

        # Retornar la lista de diagnósticos (vacía si no hay ninguno)
        return diagnosticos

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener diagnósticos: {str(e)}"
        )


@router.get("/diagnostico/{id_diagnostico}/info", response_model=List[dict])
async def get_tratamiento_patologia_by_diagnostico(
        id_diagnostico: int,
        db: Session = Depends(get_db)
):
    """
    Obtener tratamiento y patología relacionados a un diagnóstico dado su id_diagnostico
    """
    try:
        # Obtener primero el diagnóstico directamente. El diagnóstico puede haberse
        # creado sin patología (id_patologia = NULL); en ese caso el INNER JOIN de abajo
        # no devuelve nada y el formulario de "Modificar Diagnóstico" mostraba un 404.
        diagnostico_obj = db.query(Diagnostico).filter(
            Diagnostico.id_diagnostico == id_diagnostico
        ).first()

        if not diagnostico_obj:
            raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")

        # Si el diagnóstico aún no tiene patología, devolver sus datos base con valores
        # por defecto para que el formulario se abra vacío pero funcional (editable).
        if diagnostico_obj.id_patologia is None:
            return [{
                "id_tratamiento": None,
                "id_consulta": diagnostico_obj.id_consulta,
                "id_patologia": None,
                "nombre_patologia": "",
                "especie_afecta": "",
                "gravedad": "",
                "es_crónica": None,
                "es_contagiosa": None,
                "fecha_inicio_tratamiento": None,
                "eficacia_tratamiento": None,
                "tipo_tratamiento": None,
                "tipo_diagnostico": diagnostico_obj.tipo_diagnostico,
                "fecha_diagnostico": diagnostico_obj.fecha_diagnostico,
                "estado_patologia": diagnostico_obj.estado_patologia,
                "diagnostico": diagnostico_obj.diagnostico
            }]

        # Realizamos la consulta para obtener los tratamientos, patologías y diagnósticos relacionados
        tratamiento_patologia_diagnostico = db.query(Tratamiento, Patologia, Diagnostico) \
            .join(Patologia, Patologia.id_patologia == Tratamiento.id_patologia) \
            .join(Diagnostico, Diagnostico.id_patologia == Patologia.id_patologia) \
            .filter(Diagnostico.id_diagnostico == id_diagnostico) \
            .all()

        # Si hay patología pero aún no hay tratamiento, devolver diagnóstico + patología
        # para que el formulario se abra con esos datos (sin romper con 404).
        if not tratamiento_patologia_diagnostico:
            diagnostico_patologia = db.query(Diagnostico, Patologia) \
                .join(Patologia, Patologia.id_patologia == Diagnostico.id_patologia) \
                .filter(Diagnostico.id_diagnostico == id_diagnostico) \
                .first()

            if diagnostico_patologia:
                d, p = diagnostico_patologia
                return [{
                    "id_tratamiento": None,
                    "id_consulta": d.id_consulta,
                    "id_patologia": p.id_patologia,
                    "nombre_patologia": p.nombre_patologia,
                    "especie_afecta": p.especie_afecta,
                    "gravedad": p.gravedad,
                    "es_crónica": p.es_crónica,
                    "es_contagiosa": p.es_contagiosa,
                    "fecha_inicio_tratamiento": None,
                    "eficacia_tratamiento": None,
                    "tipo_tratamiento": None,
                    "tipo_diagnostico": d.tipo_diagnostico,
                    "fecha_diagnostico": d.fecha_diagnostico,
                    "estado_patologia": d.estado_patologia,
                    "diagnostico": d.diagnostico
                }]

            raise HTTPException(
                status_code=404,
                detail="No se encontraron tratamientos, patologías o diagnósticos para este diagnóstico"
            )

        # Devolver la respuesta mapeando los resultados
        return [
            {
                "id_tratamiento": t.id_tratamiento,
                "id_consulta": t.id_consulta,
                "id_patologia": p.id_patologia,
                "nombre_patologia": p.nombre_patologia,
                "especie_afecta": p.especie_afecta,
                "gravedad": p.gravedad,
                "es_crónica": p.es_crónica,
                "es_contagiosa": p.es_contagiosa,
                "fecha_inicio_tratamiento": t.fecha_inicio,
                "eficacia_tratamiento": t.eficacia_tratamiento,
                "tipo_tratamiento": t.tipo_tratamiento,

                # Información adicional del diagnóstico
                "tipo_diagnostico": d.tipo_diagnostico,
                "fecha_diagnostico": d.fecha_diagnostico,
                "estado_patologia": d.estado_patologia,
                "diagnostico": d.diagnostico
            }
            for t, p, d in tratamiento_patologia_diagnostico
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tratamiento, patología y diagnóstico: {str(e)}"
        )


@router.put("/diagnostico/{id_diagnostico}/completo", response_model=List[dict])
async def update_diagnostico_completo(
        id_diagnostico: int,
        data: DiagnosticoCompletoUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar todos los campos del formulario: diagnóstico, patología y tratamiento
    """
    try:
        # 1. Obtener el diagnóstico principal
        diagnostico_obj = db.query(Diagnostico).filter(
            Diagnostico.id_diagnostico == id_diagnostico
        ).first()

        if not diagnostico_obj:
            raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")

        # 2. Actualizar campos de DIAGNOSTICO
        if data.tipo_diagnostico is not None:
            diagnostico_obj.tipo_diagnostico = data.tipo_diagnostico
        if data.diagnostico is not None:
            diagnostico_obj.diagnostico = data.diagnostico
        if data.estado_patologia is not None:
            diagnostico_obj.estado_patologia = data.estado_patologia

        # 3. Obtener y actualizar PATOLOGIA
        patologia_obj = db.query(Patologia).filter(
            Patologia.id_patologia == diagnostico_obj.id_patologia
        ).first()

        if patologia_obj:
            if data.nombre_patologia is not None:
                patologia_obj.nombre_patologia = data.nombre_patologia
            if data.especie_afecta is not None:
                patologia_obj.especie_afecta = data.especie_afecta
            if data.es_contagioso is not None:
                patologia_obj.es_contagiosa = data.es_contagioso
            if data.es_cronico is not None:
                patologia_obj.es_crónica = data.es_cronico
            if data.gravedad_patologia is not None:
                patologia_obj.gravedad = data.gravedad_patologia
        else:
            # El diagnóstico fue creado sin patología (id_patologia = NULL). Si ya existe una
            # patología con ese nombre, reutilizarla (nombre_patologia es UNIQUE en la BD, así
            # que crear una duplicada rompía con 500); si no, crearla con los datos del
            # formulario, usando defaults para los campos NOT NULL que el formulario no envíe.
            nombre_pat = data.nombre_patologia or "Sin especificar"
            patologia_obj = db.query(Patologia).filter(
                Patologia.nombre_patologia == nombre_pat
            ).first()
            if not patologia_obj:
                patologia_obj = Patologia(
                    nombre_patologia=nombre_pat,
                    especie_afecta=data.especie_afecta or "Ambas",
                    gravedad=data.gravedad_patologia or "Moderada",
                    es_contagiosa=data.es_contagioso,
                    es_crónica=data.es_cronico,
                )
                db.add(patologia_obj)
                db.flush()  # obtener id_patologia antes de crear el tratamiento
            diagnostico_obj.id_patologia = patologia_obj.id_patologia

        # 4. Obtener y actualizar TRATAMIENTO
        tratamiento_obj = db.query(Tratamiento).filter(
            Tratamiento.id_consulta == diagnostico_obj.id_consulta,
            Tratamiento.id_patologia == diagnostico_obj.id_patologia
        ).first()

        if tratamiento_obj:
            if data.fecha_inicio is not None:
                tratamiento_obj.fecha_inicio = data.fecha_inicio
            if data.tipo_tratamiento is not None:
                tratamiento_obj.tipo_tratamiento = data.tipo_tratamiento
            if data.eficacia_tratamiento is not None:
                tratamiento_obj.eficacia_tratamiento = data.eficacia_tratamiento
        else:
            # No existía tratamiento (diagnóstico creado sin patología/tratamiento).
            # Crear uno nuevo vinculado a la patología y consulta del diagnóstico.
            tratamiento_obj = Tratamiento(
                id_consulta=diagnostico_obj.id_consulta,
                id_patologia=patologia_obj.id_patologia,
                fecha_inicio=data.fecha_inicio or date.today(),
                tipo_tratamiento=data.tipo_tratamiento or "Medicamentoso",
                eficacia_tratamiento=data.eficacia_tratamiento,
            )
            db.add(tratamiento_obj)

        # 5. Guardar cambios
        db.commit()
        db.refresh(diagnostico_obj)
        if patologia_obj:
            db.refresh(patologia_obj)
        if tratamiento_obj:
            db.refresh(tratamiento_obj)

        # 6. Devolver datos actualizados (misma estructura que el GET)
        tratamiento_patologia_diagnostico = db.query(Tratamiento, Patologia, Diagnostico) \
            .join(Patologia, Patologia.id_patologia == Tratamiento.id_patologia) \
            .join(Diagnostico, Diagnostico.id_patologia == Patologia.id_patologia) \
            .filter(Diagnostico.id_diagnostico == id_diagnostico) \
            .all()

        if tratamiento_patologia_diagnostico:
            return [
                {
                    "id_tratamiento": t.id_tratamiento,
                    "id_consulta": t.id_consulta,
                    "id_patologia": p.id_patologia,
                    "nombre_patologia": p.nombre_patologia,
                    "especie_afecta": p.especie_afecta,
                    "gravedad": p.gravedad,
                    "es_crónica": p.es_crónica,
                    "es_contagiosa": p.es_contagiosa,
                    "fecha_inicio_tratamiento": t.fecha_inicio,
                    "eficacia_tratamiento": t.eficacia_tratamiento,
                    "tipo_tratamiento": t.tipo_tratamiento,
                    "tipo_diagnostico": d.tipo_diagnostico,
                    "fecha_diagnostico": d.fecha_diagnostico,
                    "estado_patologia": d.estado_patologia,
                    "diagnostico": d.diagnostico
                }
                for t, p, d in tratamiento_patologia_diagnostico
            ]
        else:
            # Si no hay tratamiento, devolver solo diagnóstico y patología
            diagnostico_patologia = db.query(Diagnostico, Patologia) \
                .join(Patologia, Patologia.id_patologia == Diagnostico.id_patologia) \
                .filter(Diagnostico.id_diagnostico == id_diagnostico) \
                .first()

            if diagnostico_patologia:
                d, p = diagnostico_patologia
                return [{
                    "id_tratamiento": None,
                    "id_consulta": d.id_consulta,
                    "id_patologia": p.id_patologia,
                    "nombre_patologia": p.nombre_patologia,
                    "especie_afecta": p.especie_afecta,
                    "gravedad": p.gravedad,
                    "es_crónica": p.es_crónica,
                    "es_contagiosa": p.es_contagiosa,
                    "fecha_inicio_tratamiento": None,
                    "eficacia_tratamiento": None,
                    "tipo_tratamiento": None,
                    "tipo_diagnostico": d.tipo_diagnostico,
                    "fecha_diagnostico": d.fecha_diagnostico,
                    "estado_patologia": d.estado_patologia,
                    "diagnostico": d.diagnostico
                }]

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")


@router.post("/diagnostico/{consulta_id}", status_code=status.HTTP_201_CREATED)
async def create_diagnostico(
        consulta_id: int,
        db: Session = Depends(get_db)
):
    """
    Crear un diagnóstico con valores predeterminados para una consulta
    """
    try:
        # Verificar que la consulta existe
        consulta_obj = consulta.get(db, consulta_id)
        if not consulta_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )

        # Crear el diccionario con valores predeterminados
        diagnostico_dict = {
            'id_consulta': consulta_id,
            'tipo_diagnostico': 'Presuntivo',
            'fecha_diagnostico': datetime.now(),
            'estado_patologia': 'Activa',
            'diagnostico': 'Diagnóstico inicial'
        }

        # Crear el diagnóstico usando el método CRUD
        nuevo_diagnostico = diagnostico.create(db, obj_in=diagnostico_dict)

        # SC-043 / F26: registrar el diagnóstico en el historial clínico (este es el
        # endpoint que usa la UI del veterinario). Complementario: si falla, no rompe
        # la creación del diagnóstico.
        try:
            triaje_obj = triaje.get(db, consulta_obj.id_triaje)
            solicitud_obj = solicitud_atencion.get(db, triaje_obj.id_solicitud) if triaje_obj else None
            if solicitud_obj:
                historial_clinico.add_evento_diagnostico(
                    db,
                    mascota_id=solicitud_obj.id_mascota,
                    diagnostico_id=nuevo_diagnostico.id_diagnostico,
                    veterinario_id=consulta_obj.id_veterinario,
                    descripcion=nuevo_diagnostico.diagnostico or "Diagnóstico",
                )
        except Exception:
            pass

        return {"detail": "Diagnóstico insertado correctamente", "id": nuevo_diagnostico.id_diagnostico}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear diagnóstico: {str(e)}"
        )

