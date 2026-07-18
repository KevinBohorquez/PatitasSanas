# app/api/v1/endpoints/consultas/resultados.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models import Cita, ResultadoServicio, ServicioSolicitado
from app.schemas.consulta_schema import ResultadoServicioResponse, ResultadoServicioCreate

router = APIRouter()

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
    from app.crud.consulta import cita as cita_crud
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
