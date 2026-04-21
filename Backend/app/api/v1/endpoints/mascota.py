# app/api/v1/endpoints/mascotas.py (CORREGIDO)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional
from typing import List
from app.config.database import get_db
from app.crud import mascota, cliente
from app.models import SolicitudAtencion, Recepcionista, Cita, Servicio, ServicioSolicitado, TipoAnimal, Raza, Cliente
from app.models.mascota import Mascota
from app.models.cliente_mascota import ClienteMascota
from app.schemas import (
    MascotaCreate, MascotaUpdate, MascotaResponse, MascotaSearch
)
from app.api.deps import get_mascota_or_404
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
async def create_mascota(
        mascota_data: MascotaCreate,
        cliente_id: int = Query(..., description="ID del cliente propietario"),
        db: Session = Depends(get_db)
):
    """
    Crear una nueva mascota y asociarla a un cliente
    """
    # Verificar que el cliente existe
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente no existe"
        )

    # Verificar que la raza existe
    try:
        raza_exists = db.execute(
            "SELECT COUNT(*) as count FROM Raza WHERE id_raza = :id_raza",
            {"id_raza": mascota_data.id_raza}
        ).fetchone()

        if not raza_exists or raza_exists.count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Raza no existe"
            )
    except Exception:
        # Si no existe tabla Raza, continuar
        pass

    # Crear la mascota
    nueva_mascota = mascota.create(db, obj_in=mascota_data)

    # Crear la relación cliente-mascota
    relacion = ClienteMascota(
        id_cliente=cliente_id,
        id_mascota=nueva_mascota.id_mascota
    )
    db.add(relacion)
    db.commit()

    return nueva_mascota


@router.get("/")
async def get_mascotas(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        sexo: Optional[str] = Query(None, description="Filtrar por sexo"),
        id_raza: Optional[int] = Query(None, description="Filtrar por raza")
):
    """
    Obtener lista de mascotas con paginación
    """
    skip = (page - 1) * per_page

    query = db.query(Mascota)

    if sexo:
        query = query.filter(Mascota.sexo == sexo)

    if id_raza:
        query = query.filter(Mascota.id_raza == id_raza)

    total = query.count()
    mascotas = query.offset(skip).limit(per_page).all()

    # Convertir a diccionarios con información adicional
    result = []
    for mascota in mascotas:
        # Buscar cliente asociado
        cliente_info = None
        cliente_mascota = db.query(ClienteMascota).filter(
            ClienteMascota.id_mascota == mascota.id_mascota
        ).first()

        if cliente_mascota:
            from app.models.clientes import Cliente
            cliente = db.query(Cliente).filter(
                Cliente.id_cliente == cliente_mascota.id_cliente
            ).first()
            if cliente:
                cliente_info = {
                    "id_cliente": cliente.id_cliente,
                    "nombre": f"{cliente.nombre} {cliente.apellido_paterno}"
                }

        result.append({
            "id_mascota": mascota.id_mascota,
            "nombre": mascota.nombre,
            "sexo": mascota.sexo,
            "color": mascota.color,
            "edad_anios": mascota.edad_anios,
            "edad_meses": mascota.edad_meses,
            "esterilizado": mascota.esterilizado,
            "imagen": mascota.imagen,
            "id_raza": mascota.id_raza,
            "cliente": cliente_info
        })

    return {
        "mascotas": result,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/{mascota_id}", response_model=MascotaResponse)
async def get_mascota(
        mascota_obj: Mascota = Depends(get_mascota_or_404)
):
    """
    Obtener una mascota específica por ID
    """
    return mascota_obj


@router.get("/{mascota_id}/details")
async def get_mascota_with_details(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener mascota con detalles del cliente y raza
    """
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    # Buscar cliente asociado
    cliente_info = None
    cliente_mascota = db.query(ClienteMascota).filter(
        ClienteMascota.id_mascota == mascota_id
    ).first()

    if cliente_mascota:
        from app.models.clientes import Cliente
        cliente = db.query(Cliente).filter(
            Cliente.id_cliente == cliente_mascota.id_cliente
        ).first()
        if cliente:
            cliente_info = {
                "id_cliente": cliente.id_cliente,
                "nombre": cliente.nombre,
                "apellidos": f"{cliente.apellido_paterno} {cliente.apellido_materno}",
                "telefono": cliente.telefono,
                "email": cliente.email
            }

    # Buscar información de raza
    raza_info = None
    try:
        raza_result = db.execute(
            "SELECT nombre_raza, especie FROM Raza WHERE id_raza = :id_raza",
            {"id_raza": mascota_obj.id_raza}
        ).fetchone()
        if raza_result:
            raza_info = {
                "nombre_raza": raza_result.nombre_raza,
                "especie": raza_result.especie
            }
    except Exception:
        pass

    return {
        "id_mascota": mascota_obj.id_mascota,
        "nombre": mascota_obj.nombre,
        "sexo": mascota_obj.sexo,
        "color": mascota_obj.color,
        "edad_anios": mascota_obj.edad_anios,
        "edad_meses": mascota_obj.edad_meses,
        "esterilizado": mascota_obj.esterilizado,
        "imagen": mascota_obj.imagen,
        "id_raza": mascota_obj.id_raza,
        "cliente": cliente_info,
        "raza": raza_info
    }


@router.put("/{mascota_id}", response_model=MascotaResponse)
async def update_mascota(
        mascota_id: int,
        mascota_data: MascotaUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar una mascota
    """
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    # Validar raza si se está actualizando
    update_data = mascota_data.dict(exclude_unset=True)
    if "id_raza" in update_data:
        try:
            raza_exists = db.execute(
                "SELECT COUNT(*) as count FROM Raza WHERE id_raza = :id_raza",
                {"id_raza": update_data["id_raza"]}
            ).fetchone()

            if not raza_exists or raza_exists.count == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Raza no existe"
                )
        except Exception:
            pass

    return mascota.update(db, db_obj=mascota_obj, obj_in=mascota_data)


@router.get("/info/{mascota_id}")
async def get_mascota_by_id(mascota_id: int, db: Session = Depends(get_db)):
    """
    Obtener los detalles de una mascota específica: nombre, especie, raza, género, color, etc.
    """
    try:
        # Obtener la mascota por id
        mascota = db.query(
            Mascota.id_mascota,
            Mascota.nombre,
            Raza.nombre_raza.label('raza'),
            TipoAnimal.descripcion.label('especie'),
            Mascota.sexo.label('genero'),
            Mascota.color,
            Mascota.edad_anios,
            Mascota.edad_meses,
            Mascota.esterilizado,
            Mascota.imagen
        ).join(
            Raza, Mascota.id_raza == Raza.id_raza
        ).join(
            TipoAnimal, Raza.id_raza == TipoAnimal.id_raza
        ).filter(Mascota.id_mascota == mascota_id).first()

        if not mascota:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")

        # Formatear la respuesta
        result = {
            "id_mascota": mascota.id_mascota,
            "nombre": mascota.nombre,
            "especie": mascota.especie,
            "raza": mascota.raza,
            "genero": mascota.genero,
            "color": mascota.color,
            "edad_anios": mascota.edad_anios,
            "edad_meses": mascota.edad_meses,
            "esterilizado": mascota.esterilizado,
            "imagen": mascota.imagen
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la mascota: {str(e)}")



@router.delete("/{mascota_id}")
async def delete_mascota(
        mascota_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar una mascota
    """
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )

    mascota.remove(db, id=mascota_id)
    return {"message": "Mascota eliminada correctamente", "success": True}


@router.post("/search")
async def search_mascotas(
        search_params: MascotaSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar mascotas con filtros avanzados
    """
    mascotas_result, total = mascota.search_mascotas(db, search_params=search_params)

    return {
        "mascotas": mascotas_result,
        "total": total,
        "page": search_params.page,
        "per_page": search_params.per_page,
        "total_pages": (total + search_params.per_page - 1) // search_params.per_page
    }


@router.get("/cliente/{cliente_id}/list")
async def get_mascotas_by_cliente(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todas las mascotas de un cliente específico
    """
    # Verificar que el cliente existe
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    mascotas = mascota.get_mascotas_by_cliente(db, cliente_id=cliente_id)

    return {
        "cliente_id": cliente_id,
        "cliente_nombre": f"{cliente_obj.nombre} {cliente_obj.apellido_paterno}",
        "mascotas": mascotas,
        "total": len(mascotas)
    }


@router.get("/stats/por-sexo")
async def get_estadisticas_por_sexo(
        db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de mascotas por sexo
    """
    stats = mascota.count_mascotas_by_sexo(db)
    return {
        "estadisticas_por_sexo": stats,
        "total": stats["machos"] + stats["hembras"]
    }


@router.get("/no-esterilizadas/list")
async def get_mascotas_no_esterilizadas(
        db: Session = Depends(get_db)
):
    """
    Obtener mascotas no esterilizadas
    """
    mascotas = mascota.get_mascotas_no_esterilizadas(db)
    return {
        "mascotas_no_esterilizadas": mascotas,
        "total": len(mascotas)
    }

@router.get("/proxima-cita/{mascota_id}")
async def get_proxima_cita_mascota(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener la próxima cita programada de una mascota específica
    """
    try:
        # JOIN para obtener la próxima cita (fecha futura más cercana)
        proxima_cita = db.query(
            Cita.id_cita,
            Cita.fecha_hora_programada,
            Cita.estado_cita,
            Servicio.nombre_servicio
        ).join(
            ServicioSolicitado, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado
        ).join(
            Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio
        ).filter(
            Cita.id_mascota == mascota_id,
            Cita.estado_cita == 'Programada',
            Cita.fecha_hora_programada > datetime.now()  # Solo citas futuras
        ).order_by(
            Cita.fecha_hora_programada.asc()  # La más próxima primero
        ).first()

        if not proxima_cita:
            return {
                "mascota_id": mascota_id,
                "proxima_cita": None,
                "fecha_hora_programada": None,
                "servicio": "No hay citas programadas",
                "mensaje": "No hay citas programadas"
            }

        return {
            "mascota_id": mascota_id,
            "proxima_cita": proxima_cita.id_cita,
            "fecha_hora_programada": proxima_cita.fecha_hora_programada,
            "servicio": proxima_cita.nombre_servicio,
            "estado": proxima_cita.estado_cita
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener próxima cita: {str(e)}"
        )


@router.get("/ultima-atencion/{mascota_id}")
async def get_ultima_atencion_mascota(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener la última atención recibida por una mascota específica
    """
    try:
        # JOIN para obtener la última solicitud de atención
        ultima_atencion = db.query(
            SolicitudAtencion.id_solicitud,
            SolicitudAtencion.fecha_hora_solicitud,
            SolicitudAtencion.tipo_solicitud,
            SolicitudAtencion.estado,
            func.concat(
                Recepcionista.nombre, ' ',
                Recepcionista.apellido_paterno
            ).label('recepcionista')
        ).join(
            Recepcionista, SolicitudAtencion.id_recepcionista == Recepcionista.id_recepcionista
        ).filter(
            SolicitudAtencion.id_mascota == mascota_id,
            SolicitudAtencion.estado.in_(['Completada', 'En atencion'])  # Solo atenciones reales
        ).order_by(
            SolicitudAtencion.fecha_hora_solicitud.desc()  # La más reciente primero
        ).first()

        if not ultima_atencion:
            return {
                "mascota_id": mascota_id,
                "ultima_atencion": None,
                "fecha_hora_solicitud": None,
                "tipo_solicitud": "--",
                "recepcionista": "--",
                "mensaje": "No hay atenciones registradas"
            }

        return {
            "mascota_id": mascota_id,
            "ultima_atencion": ultima_atencion.id_solicitud,
            "fecha_hora_solicitud": ultima_atencion.fecha_hora_solicitud,
            "tipo_solicitud": ultima_atencion.tipo_solicitud,
            "estado": ultima_atencion.estado,
            "recepcionista": ultima_atencion.recepcionista
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener última atención: {str(e)}"
        )


@router.get("/mascota_cliente_servicio/{id_mascota}", response_model=List[dict])
async def get_mascota_cliente_servicio(id_mascota: int, db: Session = Depends(get_db)):
    try:
        # Realizamos la consulta con los JOIN correctos
        result = db.query(Mascota, Cliente, Servicio, ServicioSolicitado) \
            .join(ClienteMascota, Mascota.id_mascota == ClienteMascota.id_mascota) \
            .join(Cliente, ClienteMascota.id_cliente == Cliente.id_cliente) \
            .join(ServicioSolicitado, ServicioSolicitado.id_servicio_solicitado == Mascota.id_mascota) \
            .join(Servicio, ServicioSolicitado.id_servicio == Servicio.id_servicio) \
            .filter(Mascota.id_mascota == id_mascota) \
            .all()

        if not result:
            raise HTTPException(status_code=404, detail="Mascota no encontrada o no tiene servicios asociados")

        # Procesamos y devolvemos la respuesta mapeada en el formato deseado
        return [
            {
                "id_mascota": m.id_mascota,
                "nombre_mascota": m.nombre,
                "id_cliente": c.id_cliente,
                "nombre_cliente": f"{c.nombre} {c.apellido_paterno} {c.apellido_materno}",
                "id_servicio_solicitado": ss.id_servicio_solicitado if ss else None,  # Manejo de NULL
                "nombre_servicio": s.nombre_servicio if s else None,  # Nombre del servicio
                "id_servicio": s.id_servicio if s else None,  # ID del servicio
            }
            for m, c, s, ss in result
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")
