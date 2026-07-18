# app/api/v1/endpoints/consultas/consultas.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from app.config.database import get_db
from app.crud.consulta import consulta, diagnostico, tratamiento, historial_clinico, triaje, solicitud_atencion
from app.crud.veterinario_crud import veterinario
from app.schemas.consulta_schema import ConsultaCreate, ConsultaResponse, ConsultaSearch, ConsultaUpdate
from app.schemas.base_schema import MessageResponse

router = APIRouter()

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
            total_periodo = consulta.count(db)

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
