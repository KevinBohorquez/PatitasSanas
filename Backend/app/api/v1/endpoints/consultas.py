# app/api/v1/endpoints/consultas.py - VERSIÓN CORREGIDA
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.config.database import get_db
from app.crud.catalogo_crud import servicio
from app.crud import servicio_solicitado
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
    limit: int = Query(50, ge=1, le=500, description="Cantidad máxima de eventos")
):
    """
    Obtener historial clínico de una mascota
    """
    try:
        eventos = historial_clinico.get_by_mascota(db, mascota_id=mascota_id, limit=limit)

        return [
            {
                "id_historial": e.id_historial,
                "fecha_evento": e.fecha_evento,
                "tipo_evento": e.tipo_evento,
                "edad_meses": e.edad_meses,
                "descripcion_evento": e.descripcion_evento,
                "peso_momento": float(e.peso_momento) if e.peso_momento else None,
                "observaciones": e.observaciones
            }
            for e in eventos
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
        # Consultar las consultas relacionadas con la mascota, pasando por Solicitud_atencion, Triaje y Consulta
        eventos = db.query(Consulta).join(SolicitudAtencion, SolicitudAtencion.id_solicitud == Consulta.id_triaje) \
            .join(Triaje, Triaje.id_triaje == Consulta.id_triaje) \
            .join(Mascota, Mascota.id_mascota == SolicitudAtencion.id_mascota) \
            .filter(Mascota.id_mascota == mascota_id) \
            .limit(limit).all()

        if not eventos:
            raise HTTPException(status_code=404, detail="No se encontraron consultas para esta mascota")

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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener consultas: {str(e)}"
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

        # Si no se encuentran diagnósticos
        if not diagnosticos:
            raise HTTPException(status_code=404, detail="No se encontraron diagnósticos para esta consulta")

        # Retornar la lista de diagnósticos
        return diagnosticos

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
        # Realizamos la consulta para obtener los tratamientos, patologías y diagnósticos relacionados
        tratamiento_patologia_diagnostico = db.query(Tratamiento, Patologia, Diagnostico) \
            .join(Patologia, Patologia.id_patologia == Tratamiento.id_patologia) \
            .join(Diagnostico, Diagnostico.id_patologia == Patologia.id_patologia) \
            .filter(Diagnostico.id_diagnostico == id_diagnostico) \
            .all()

        if not tratamiento_patologia_diagnostico:
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

        return {"detail": "Diagnóstico insertado correctamente", "id": nuevo_diagnostico.id_diagnostico}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear diagnóstico: {str(e)}"
        )

