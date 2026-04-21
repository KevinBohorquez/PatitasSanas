# app/api/v1/endpoints/catalogos.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud.catalogo_crud import (
    raza, tipo_animal, especialidad, tipo_servicio,
    servicio, patologia, cliente_mascota
)
from app.models.raza import Raza
from app.models.tipo_animal import TipoAnimal
from app.models.especialidad import Especialidad
from app.models.tipo_servicio import TipoServicio
from app.models.servicio import Servicio
from app.models.patologia import Patologia
from app.models.cliente_mascota import ClienteMascota
from app.schemas.catalogo_schemas import (
    RazaCreate, RazaResponse,
    TipoAnimalCreate, TipoAnimalResponse,
    EspecialidadCreate, EspecialidadResponse,
    TipoServicioCreate, TipoServicioResponse,
    ServicioCreate, ServicioUpdate, ServicioResponse, ServicioWithTipoResponse,
    PatologiaCreate, PatologiaResponse,
    ClienteMascotaCreate, ClienteMascotaResponse
)
from app.schemas.base_schema import MessageResponse

router = APIRouter()


# ===== ENDPOINTS PARA RAZA =====

@router.post("/razas/", response_model=RazaResponse, status_code=status.HTTP_201_CREATED)
async def create_raza(
        raza_data: RazaCreate,
        db: Session = Depends(get_db)
):
    """Crear una nueva raza"""
    try:
        # Validar duplicados
        if raza.exists_by_nombre(db, nombre_raza=raza_data.nombre_raza):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una raza con ese nombre"
            )

        return raza.create(db, obj_in=raza_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear raza: {str(e)}"
        )


@router.get("/razas/", response_model=List[RazaResponse])
async def get_razas(
        db: Session = Depends(get_db),
        ordenadas: bool = Query(True, description="Ordenar alfabéticamente")
):
    """Obtener lista de razas"""
    try:
        if ordenadas:
            return raza.get_all_ordenadas(db)
        else:
            return raza.get_multi(db, limit=1000)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener razas: {str(e)}"
        )


@router.get("/razas/{raza_id}", response_model=RazaResponse)
async def get_raza(
        raza_id: int,
        db: Session = Depends(get_db)
):
    """Obtener una raza específica por ID"""
    try:
        raza_obj = raza.get(db, raza_id)
        if not raza_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raza no encontrada"
            )
        return raza_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener raza: {str(e)}"
        )


@router.get("/razas/nombre/{nombre}")
async def get_raza_by_nombre(
        nombre: str,
        db: Session = Depends(get_db)
):
    """Obtener raza por nombre"""
    try:
        raza_obj = raza.get_by_nombre(db, nombre_raza=nombre)
        if not raza_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raza no encontrada"
            )
        return raza_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar raza: {str(e)}"
        )


@router.get("/razas/search/{termino}")
async def search_razas(
        termino: str,
        db: Session = Depends(get_db)
):
    """Buscar razas por nombre (parcial)"""
    try:
        razas_encontradas = raza.search_razas(db, nombre=termino)
        return {
            "termino_busqueda": termino,
            "razas": razas_encontradas,
            "total": len(razas_encontradas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de razas: {str(e)}"
        )


@router.get("/razas/estadisticas/mascotas")
async def get_razas_con_mascotas_count(db: Session = Depends(get_db)):
    """Obtener razas con conteo de mascotas"""
    try:
        return raza.get_razas_con_mascotas_count(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas de razas: {str(e)}"
        )


@router.get("/razas/populares/top")
async def get_razas_populares(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """Obtener razas más populares"""
    try:
        return raza.get_razas_populares(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener razas populares: {str(e)}"
        )


# ===== ENDPOINTS PARA TIPO ANIMAL =====

@router.post("/tipos-animal/", response_model=TipoAnimalResponse, status_code=status.HTTP_201_CREATED)
async def create_tipo_animal(
        tipo_data: TipoAnimalCreate,
        db: Session = Depends(get_db)
):
    """Crear un nuevo tipo de animal"""
    try:
        # Validar que no existe la combinación
        if tipo_animal.exists_combination(db, raza_id=tipo_data.id_raza, descripcion=tipo_data.descripcion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe esa combinación de raza y tipo de animal"
            )

        return tipo_animal.create(db, obj_in=tipo_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tipo de animal: {str(e)}"
        )


@router.get("/tipos-animal/", response_model=List[TipoAnimalResponse])
async def get_tipos_animal(db: Session = Depends(get_db)):
    """Obtener lista de tipos de animal"""
    try:
        return tipo_animal.get_multi(db, limit=1000)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos de animal: {str(e)}"
        )


@router.get("/tipos-animal/raza/{raza_id}")
async def get_tipos_animal_by_raza(
        raza_id: int,
        db: Session = Depends(get_db)
):
    """Obtener tipos de animal por raza"""
    try:
        tipos = tipo_animal.get_by_raza(db, raza_id=raza_id)
        return {
            "id_raza": raza_id,
            "tipos_animal": tipos,
            "total": len(tipos)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos por raza: {str(e)}"
        )


@router.get("/tipos-animal/descripcion/{descripcion}")
async def get_tipos_animal_by_descripcion(
        descripcion: str,
        db: Session = Depends(get_db)
):
    """Obtener tipos de animal por descripción (Perro/Gato)"""
    try:
        if descripcion not in ['Perro', 'Gato']:
            raise HTTPException(
                status_code=400,
                detail="Descripción debe ser 'Perro' o 'Gato'"
            )

        tipos = tipo_animal.get_by_descripcion(db, descripcion=descripcion)
        return {
            "descripcion": descripcion,
            "tipos_animal": tipos,
            "total": len(tipos)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos por descripción: {str(e)}"
        )


@router.get("/tipos-animal/with-raza-info/list")
async def get_tipos_animal_with_raza_info(db: Session = Depends(get_db)):
    """Obtener tipos de animal con información de raza"""
    try:
        return tipo_animal.get_with_raza_info(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos con info de raza: {str(e)}"
        )


@router.get("/tipos-animal/estadisticas/general")
async def get_tipos_animal_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas de tipos de animal"""
    try:
        return tipo_animal.get_estadisticas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ===== ENDPOINTS PARA ESPECIALIDAD =====

@router.post("/especialidades/", response_model=EspecialidadResponse, status_code=status.HTTP_201_CREATED)
async def create_especialidad(
        especialidad_data: EspecialidadCreate,
        db: Session = Depends(get_db)
):
    """Crear una nueva especialidad"""
    try:
        # Validar duplicados
        if especialidad.exists_by_descripcion(db, descripcion=especialidad_data.descripcion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una especialidad con esa descripción"
            )

        return especialidad.create(db, obj_in=especialidad_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear especialidad: {str(e)}"
        )


@router.get("/especialidades/", response_model=List[EspecialidadResponse])
async def get_especialidades(db: Session = Depends(get_db)):
    """Obtener lista de especialidades"""
    try:
        return especialidad.get_all_ordenadas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener especialidades: {str(e)}"
        )


@router.get("/especialidades/{especialidad_id}", response_model=EspecialidadResponse)
async def get_especialidad(
        especialidad_id: int,
        db: Session = Depends(get_db)
):
    """Obtener una especialidad específica por ID"""
    try:
        especialidad_obj = especialidad.get(db, especialidad_id)
        if not especialidad_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Especialidad no encontrada"
            )
        return especialidad_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener especialidad: {str(e)}"
        )


@router.get("/especialidades/search/{termino}")
async def search_especialidades(
        termino: str,
        db: Session = Depends(get_db)
):
    """Buscar especialidades por descripción"""
    try:
        especialidades_encontradas = especialidad.search_especialidades(db, descripcion=termino)
        return {
            "termino_busqueda": termino,
            "especialidades": especialidades_encontradas,
            "total": len(especialidades_encontradas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de especialidades: {str(e)}"
        )


@router.get("/especialidades/estadisticas/veterinarios")
async def get_especialidades_con_veterinarios_count(db: Session = Depends(get_db)):
    """Obtener especialidades con conteo de veterinarios"""
    try:
        return especialidad.get_especialidades_con_veterinarios_count(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/especialidades/demandadas/top")
async def get_especialidades_mas_demandadas(
        db: Session = Depends(get_db),
        limit: int = Query(5, ge=1, le=20, description="Límite de resultados")
):
    """Obtener especialidades más demandadas"""
    try:
        return especialidad.get_mas_demandadas(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener especialidades demandadas: {str(e)}"
        )


# ===== ENDPOINTS PARA TIPO SERVICIO =====

@router.post("/tipos-servicio/", response_model=TipoServicioResponse, status_code=status.HTTP_201_CREATED)
async def create_tipo_servicio(
        tipo_servicio_data: TipoServicioCreate,
        db: Session = Depends(get_db)
):
    """Crear un nuevo tipo de servicio"""
    try:
        # Validar duplicados
        if tipo_servicio.exists_by_descripcion(db, descripcion=tipo_servicio_data.descripcion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un tipo de servicio con esa descripción"
            )

        return tipo_servicio.create(db, obj_in=tipo_servicio_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tipo de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/", response_model=List[TipoServicioResponse])
async def get_tipos_servicio(db: Session = Depends(get_db)):
    """Obtener lista de tipos de servicio"""
    try:
        return tipo_servicio.get_all_ordenados(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/{tipo_servicio_id}", response_model=TipoServicioResponse)
async def get_tipo_servicio(
        tipo_servicio_id: int,
        db: Session = Depends(get_db)
):
    """Obtener un tipo de servicio específico por ID"""
    try:
        tipo_servicio_obj = tipo_servicio.get(db, tipo_servicio_id)
        if not tipo_servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de servicio no encontrado"
            )
        return tipo_servicio_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipo de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/search/{termino}")
async def search_tipos_servicio(
        termino: str,
        db: Session = Depends(get_db)
):
    """Buscar tipos de servicio por descripción"""
    try:
        tipos_encontrados = tipo_servicio.search_tipos(db, descripcion=termino)
        return {
            "termino_busqueda": termino,
            "tipos_servicio": tipos_encontrados,
            "total": len(tipos_encontrados)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de tipos de servicio: {str(e)}"
        )


@router.get("/tipos-servicio/estadisticas/servicios")
async def get_tipos_servicio_con_servicios_count(db: Session = Depends(get_db)):
    """Obtener tipos de servicio con conteo de servicios"""
    try:
        return tipo_servicio.get_tipos_con_servicios_count(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ===== ENDPOINTS PARA SERVICIO =====

@router.post("/servicios/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
async def create_servicio(
        servicio_data: ServicioCreate,
        db: Session = Depends(get_db)
):
    """Crear un nuevo servicio"""
    try:
        # Validar duplicados
        if servicio.exists_by_nombre(db, nombre_servicio=servicio_data.nombre_servicio):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un servicio con ese nombre"
            )

        return servicio.create(db, obj_in=servicio_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear servicio: {str(e)}"
        )


@router.get("/servicios/", response_model=List[ServicioResponse])
async def get_servicios(
        db: Session = Depends(get_db),
        activos_solo: bool = Query(True, description="Solo servicios activos"),
        tipo_servicio_id: Optional[int] = Query(None, description="Filtrar por tipo")
):
    """Obtener lista de servicios"""
    try:
        if tipo_servicio_id:
            return servicio.get_by_tipo(db, tipo_servicio_id=tipo_servicio_id, solo_activos=activos_solo)
        elif activos_solo:
            return servicio.get_activos(db)
        else:
            return servicio.get_multi(db, limit=1000)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicios: {str(e)}"
        )


@router.get("/servicios/{servicio_id}", response_model=ServicioResponse)
async def get_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Obtener un servicio específico por ID"""
    try:
        servicio_obj = servicio.get(db, servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
        return servicio_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicio: {str(e)}"
        )


@router.get("/servicios/{servicio_id}/with-tipo", response_model=ServicioWithTipoResponse)
async def get_servicio_with_tipo_info(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Obtener servicio con información del tipo"""
    try:
        servicio_info = servicio.get_with_tipo_info(db, servicio_id=servicio_id)
        if not servicio_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
        return servicio_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicio con tipo: {str(e)}"
        )


@router.put("/servicios/{servicio_id}", response_model=ServicioResponse)
async def update_servicio(
        servicio_id: int,
        servicio_data: ServicioUpdate,
        db: Session = Depends(get_db)
):
    """Actualizar un servicio"""
    try:
        servicio_obj = servicio.get(db, servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        # Validar nombre único si se está actualizando
        update_data = servicio_data.dict(exclude_unset=True)
        if "nombre_servicio" in update_data:
            if servicio.exists_by_nombre(db, nombre_servicio=update_data["nombre_servicio"], exclude_id=servicio_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un servicio con ese nombre"
                )

        return servicio.update(db, db_obj=servicio_obj, obj_in=servicio_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar servicio: {str(e)}"
        )


@router.patch("/servicios/{servicio_id}/activate", response_model=MessageResponse)
async def activate_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Activar un servicio"""
    try:
        servicio_obj = servicio.activate_service(db, servicio_id=servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        return {"message": "Servicio activado exitosamente", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al activar servicio: {str(e)}"
        )


@router.patch("/servicios/{servicio_id}/deactivate", response_model=MessageResponse)
async def deactivate_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Desactivar un servicio"""
    try:
        servicio_obj = servicio.deactivate_service(db, servicio_id=servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        return {"message": "Servicio desactivado exitosamente", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar servicio: {str(e)}"
        )


@router.get("/servicios/search/nombre/{termino}")
async def search_servicios(
        termino: str,
        db: Session = Depends(get_db),
        activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
        tipo_servicio_id: Optional[int] = Query(None, description="Filtrar por tipo")
):
    """Buscar servicios por nombre"""
    try:
        servicios_encontrados = servicio.search_servicios(
            db,
            nombre=termino,
            activo=activo,
            tipo_servicio_id=tipo_servicio_id
        )
        return {
            "termino_busqueda": termino,
            "servicios": servicios_encontrados,
            "total": len(servicios_encontrados)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de servicios: {str(e)}"
        )


@router.get("/servicios/precio-range/list")
async def get_servicios_by_precio_range(
        db: Session = Depends(get_db),
        precio_min: Optional[float] = Query(None, description="Precio mínimo"),
        precio_max: Optional[float] = Query(None, description="Precio máximo")
):
    """Obtener servicios por rango de precio"""
    try:
        servicios_encontrados = servicio.get_by_precio_range(
            db,
            precio_min=precio_min,
            precio_max=precio_max
        )
        return {
            "precio_min": precio_min,
            "precio_max": precio_max,
            "servicios": servicios_encontrados,
            "total": len(servicios_encontrados)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicios por precio: {str(e)}"
        )


@router.get("/servicios/populares/top")
async def get_servicios_mas_solicitados(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """Obtener servicios más solicitados"""
    try:
        return servicio.get_mas_solicitados(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener servicios populares: {str(e)}"
        )


@router.get("/servicios/estadisticas/precios")
async def get_servicios_estadisticas_precios(db: Session = Depends(get_db)):
    """Obtener estadísticas de precios de servicios"""
    try:
        return servicio.get_estadisticas_precios(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas de precios: {str(e)}"
        )


@router.delete("/servicios/{servicio_id}", response_model=MessageResponse)
async def delete_servicio(
        servicio_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar un servicio permanentemente"""
    try:
        servicio_obj = servicio.get(db, servicio_id)
        if not servicio_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )

        # Verificar si el servicio está siendo usado
        try:
            from app.models.servicio_solicitado import ServicioSolicitado
            servicios_solicitados = db.query(ServicioSolicitado).filter(
                ServicioSolicitado.id_servicio == servicio_id
            ).count()

            if servicios_solicitados > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede eliminar el servicio. Está siendo usado en {servicios_solicitados} solicitud(es). Considere desactivarlo en su lugar."
                )
        except ImportError:
            # Si no existe el modelo ServicioSolicitado, continuar con la eliminación
            pass

        # Eliminar el servicio
        success = servicio.remove(db, id=servicio_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el servicio"
            )

        return {
            "message": f"Servicio '{servicio_obj.nombre_servicio}' eliminado exitosamente",
            "success": True
        }

    except HTTPException as http_ex:
        # Re-raise HTTP exceptions para que FastAPI las maneje correctamente
        raise http_ex
    except Exception as e:
        # Para otros errores, crear una HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar servicio: {str(e)}"
        )

# ===== ENDPOINTS PARA PATOLOGÍA =====

@router.post("/patologias/", response_model=PatologiaResponse, status_code=status.HTTP_201_CREATED)
async def create_patologia(
        patologia_data: PatologiaCreate,
        db: Session = Depends(get_db)
):
    """Crear una nueva patología"""
    try:
        # Validar duplicados
        if patologia.exists_by_nombre(db, nombre_patologia=patologia_data.nombre_patologia):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una patología con ese nombre"
            )

        return patologia.create(db, obj_in=patologia_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear patología: {str(e)}"
        )


@router.get("/patologias/", response_model=List[PatologiaResponse])
async def get_patologias(db: Session = Depends(get_db)):
    """Obtener lista de patologías"""
    try:
        return patologia.get_all_ordenadas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías: {str(e)}"
        )


@router.get("/patologias/{patologia_id}", response_model=PatologiaResponse)
async def get_patologia(
        patologia_id: int,
        db: Session = Depends(get_db)
):
    """Obtener una patología específica por ID"""
    try:
        patologia_obj = patologia.get(db, patologia_id)
        if not patologia_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patología no encontrada"
            )
        return patologia_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patología: {str(e)}"
        )


@router.get("/patologias/especie/{especie}")
async def get_patologias_by_especie(
        especie: str,
        db: Session = Depends(get_db)
):
    """Obtener patologías por especie"""
    try:
        if especie not in ['Perro', 'Gato', 'Ambas']:
            raise HTTPException(
                status_code=400,
                detail="Especie debe ser 'Perro', 'Gato' o 'Ambas'"
            )

        patologias_encontradas = patologia.get_by_especie(db, especie=especie)
        return {
            "especie": especie,
            "patologias": patologias_encontradas,
            "total": len(patologias_encontradas)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías por especie: {str(e)}"
        )


@router.get("/patologias/gravedad/{gravedad}")
async def get_patologias_by_gravedad(
        gravedad: str,
        db: Session = Depends(get_db)
):
    """Obtener patologías por gravedad"""
    try:
        if gravedad not in ['Leve', 'Moderada', 'Grave', 'Critica']:
            raise HTTPException(
                status_code=400,
                detail="Gravedad debe ser 'Leve', 'Moderada', 'Grave' o 'Critica'"
            )

        patologias_encontradas = patologia.get_by_gravedad(db, gravedad=gravedad)
        return {
            "gravedad": gravedad,
            "patologias": patologias_encontradas,
            "total": len(patologias_encontradas)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías por gravedad: {str(e)}"
        )


@router.get("/patologias/cronicas/list")
async def get_patologias_cronicas(db: Session = Depends(get_db)):
    """Obtener patologías crónicas"""
    try:
        patologias_cronicas = patologia.get_cronicas(db)
        return {
            "patologias_cronicas": patologias_cronicas,
            "total": len(patologias_cronicas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías crónicas: {str(e)}"
        )


@router.get("/patologias/contagiosas/list")
async def get_patologias_contagiosas(db: Session = Depends(get_db)):
    """Obtener patologías contagiosas"""
    try:
        patologias_contagiosas = patologia.get_contagiosas(db)
        return {
            "patologias_contagiosas": patologias_contagiosas,
            "total": len(patologias_contagiosas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías contagiosas: {str(e)}"
        )


@router.get("/patologias/search/avanzada")
async def search_patologias_avanzada(
        db: Session = Depends(get_db),
        nombre: Optional[str] = Query(None, description="Buscar por nombre"),
        especie: Optional[str] = Query(None, description="Filtrar por especie"),
        gravedad: Optional[str] = Query(None, description="Filtrar por gravedad")
):
    """Buscar patologías con filtros múltiples"""
    try:
        patologias_encontradas = patologia.search_patologias(
            db,
            nombre=nombre,
            especie=especie,
            gravedad=gravedad
        )
        return {
            "filtros": {
                "nombre": nombre,
                "especie": especie,
                "gravedad": gravedad
            },
            "patologias": patologias_encontradas,
            "total": len(patologias_encontradas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda avanzada de patologías: {str(e)}"
        )


@router.get("/patologias/estadisticas/general")
async def get_patologias_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas generales de patologías"""
    try:
        return patologia.get_estadisticas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas de patologías: {str(e)}"
        )


@router.get("/patologias/diagnosticadas/top")
async def get_patologias_mas_diagnosticadas(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=50, description="Límite de resultados")
):
    """Obtener patologías más diagnosticadas"""
    try:
        return patologia.get_mas_diagnosticadas(db, limit=limit)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener patologías más diagnosticadas: {str(e)}"
        )


# ===== ENDPOINTS PARA CLIENTE_MASCOTA =====

@router.post("/cliente-mascota/", response_model=ClienteMascotaResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente_mascota_relation(
        relacion_data: ClienteMascotaCreate,
        db: Session = Depends(get_db)
):
    """Crear relación cliente-mascota"""
    try:
        # Verificar que no existe ya la relación
        if cliente_mascota.exists_relationship(
                db,
                cliente_id=relacion_data.id_cliente,
                mascota_id=relacion_data.id_mascota
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe la relación entre este cliente y mascota"
            )

        nueva_relacion = cliente_mascota.create_relationship(
            db,
            cliente_id=relacion_data.id_cliente,
            mascota_id=relacion_data.id_mascota
        )

        if not nueva_relacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear la relación"
            )

        return nueva_relacion

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear relación cliente-mascota: {str(e)}"
        )


@router.get("/cliente-mascota/cliente/{cliente_id}")
async def get_mascotas_by_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """Obtener mascotas de un cliente con información detallada"""
    try:
        mascotas_info = cliente_mascota.get_mascotas_info_by_cliente(db, cliente_id=cliente_id)
        return {
            "id_cliente": cliente_id,
            "mascotas": mascotas_info,
            "total_mascotas": len(mascotas_info)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mascotas del cliente: {str(e)}"
        )


@router.get("/cliente-mascota/mascota/{mascota_id}")
async def get_clientes_by_mascota(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """Obtener clientes de una mascota con información detallada"""
    try:
        clientes_info = cliente_mascota.get_clientes_info_by_mascota(db, mascota_id=mascota_id)
        return {
            "id_mascota": mascota_id,
            "clientes": clientes_info,
            "total_clientes": len(clientes_info)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener clientes de la mascota: {str(e)}"
        )


@router.delete("/cliente-mascota/{cliente_id}/{mascota_id}", response_model=MessageResponse)
async def delete_cliente_mascota_relation(
        cliente_id: int,
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar relación cliente-mascota"""
    try:
        success = cliente_mascota.remove_relationship(
            db,
            cliente_id=cliente_id,
            mascota_id=mascota_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relación cliente-mascota no encontrada"
            )

        return {"message": "Relación eliminada exitosamente", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar relación: {str(e)}"
        )


@router.put("/cliente-mascota/transfer/{mascota_id}")
async def transfer_mascota(
        mascota_id: int,
        cliente_anterior_id: int = Query(..., description="ID del cliente actual"),
        cliente_nuevo_id: int = Query(..., description="ID del nuevo cliente"),
        db: Session = Depends(get_db)
):
    """Transferir mascota entre clientes"""
    try:
        success = cliente_mascota.transfer_mascota(
            db,
            mascota_id=mascota_id,
            cliente_anterior_id=cliente_anterior_id,
            cliente_nuevo_id=cliente_nuevo_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo realizar la transferencia. Verifique que existe la relación actual y que no existe con el nuevo cliente."
            )

        return {
            "message": "Mascota transferida exitosamente",
            "success": True,
            "mascota_id": mascota_id,
            "cliente_anterior": cliente_anterior_id,
            "cliente_nuevo": cliente_nuevo_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al transferir mascota: {str(e)}"
        )


@router.get("/cliente-mascota/all/with-details")
async def get_all_relations_with_details(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """Obtener todas las relaciones con información detallada"""
    try:
        skip = (page - 1) * per_page

        relaciones_info = cliente_mascota.get_all_relationships_with_details(
            db, skip=skip, limit=per_page
        )

        total = db.query(ClienteMascota).count()

        return {
            "relaciones": relaciones_info,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener relaciones: {str(e)}"
        )


@router.get("/cliente-mascota/clientes-sin-mascotas/list")
async def get_clientes_sin_mascotas(db: Session = Depends(get_db)):
    """Obtener clientes que no tienen mascotas"""
    try:
        clientes_sin_mascotas = cliente_mascota.get_clientes_sin_mascotas(db)
        return {
            "clientes_sin_mascotas": clientes_sin_mascotas,
            "total": len(clientes_sin_mascotas)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener clientes sin mascotas: {str(e)}"
        )


@router.get("/cliente-mascota/mascotas-sin-cliente/list")
async def get_mascotas_sin_cliente(db: Session = Depends(get_db)):
    """Obtener mascotas que no tienen cliente asignado"""
    try:
        mascotas_sin_cliente = cliente_mascota.get_mascotas_sin_cliente(db)
        return {
            "mascotas_sin_cliente": mascotas_sin_cliente,
            "total": len(mascotas_sin_cliente)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mascotas sin cliente: {str(e)}"
        )


@router.get("/cliente-mascota/estadisticas/general")
async def get_cliente_mascota_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas de relaciones cliente-mascota"""
    try:
        return cliente_mascota.get_estadisticas(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.post("/cliente-mascota/bulk-assign/{cliente_id}")
async def bulk_assign_mascotas_to_cliente(
        cliente_id: int,
        mascota_ids: List[int],
        db: Session = Depends(get_db)
):
    """Asignar múltiples mascotas a un cliente"""
    try:
        asignadas, errores = cliente_mascota.bulk_assign_mascotas(
            db,
            cliente_id=cliente_id,
            mascota_ids=mascota_ids
        )

        return {
            "message": f"Proceso completado: {asignadas} mascotas asignadas",
            "success": True,
            "cliente_id": cliente_id,
            "mascotas_asignadas": asignadas,
            "total_intentos": len(mascota_ids),
            "errores": errores
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en asignación masiva: {str(e)}"
        )


@router.delete("/cliente-mascota/cliente/{cliente_id}/all", response_model=MessageResponse)
async def delete_all_relations_by_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar todas las relaciones de un cliente"""
    try:
        count = cliente_mascota.remove_all_relationships_by_cliente(db, cliente_id=cliente_id)

        return {
            "message": f"Se eliminaron {count} relaciones del cliente",
            "success": True,
            "cliente_id": cliente_id,
            "relaciones_eliminadas": count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar relaciones del cliente: {str(e)}"
        )


@router.delete("/cliente-mascota/mascota/{mascota_id}/all", response_model=MessageResponse)
async def delete_all_relations_by_mascota(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """Eliminar todas las relaciones de una mascota"""
    try:
        count = cliente_mascota.remove_all_relationships_by_mascota(db, mascota_id=mascota_id)

        return {
            "message": f"Se eliminaron {count} relaciones de la mascota",
            "success": True,
            "mascota_id": mascota_id,
            "relaciones_eliminadas": count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar relaciones de la mascota: {str(e)}"
        )


# ===== ENDPOINTS GENERALES =====

@router.get("/debug/info")
async def debug_catalogos_info(db: Session = Depends(get_db)):
    """Endpoint para depurar información de las tablas de catálogo"""
    try:
        info = {}

        tablas = [
            ("Raza", Raza),
            ("Tipo_animal", TipoAnimal),
            ("Especialidad", Especialidad),
            ("Tipo_servicio", TipoServicio),
            ("Servicio", Servicio),
            ("Patologia", Patologia),
            ("Cliente_Mascota", ClienteMascota)
        ]

        for tabla_nombre, tabla_modelo in tablas:
            try:
                count = db.query(tabla_modelo).count()
                info[tabla_nombre] = {
                    "total_records": count,
                    "status": "OK"
                }
            except Exception as e:
                info[tabla_nombre] = {
                    "total_records": 0,
                    "status": f"Error: {str(e)}"
                }

        return {
            "debug_info": info,
            "timestamp": "2024-06-09"
        }

    except Exception as e:
        return {
            "error": f"Error al obtener información de debug: {str(e)}"
        }