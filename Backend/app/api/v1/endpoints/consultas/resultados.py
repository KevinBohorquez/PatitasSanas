# app/api/v1/endpoints/consultas/resultados.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.crud.consulta import resultado_servicio, cita as cita_crud, servicio_solicitado
from app.schemas.consulta_schema import ResultadoServicioResponse, ResultadoServicioCreate

router = APIRouter()

@router.get("/resultado_servicio/{cita_id}", response_model=ResultadoServicioResponse)
async def get_resultado_servicio(cita_id: int, db: Session = Depends(get_db)):
    # Buscar el resultado del servicio para la cita específica
    resultado = resultado_servicio.get_by_cita(db, cita_id=cita_id)

    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado del servicio no encontrado para esta cita")

    return ResultadoServicioResponse(
        id_resultado=resultado.id_resultado,
        id_cita=resultado.id_cita,
        id_veterinario=resultado.id_veterinario,
        resultado=resultado.resultado,
        interpretacion=resultado.interpretacion,
        archivo_adjunto=resultado.archivo_adjunto,
        fecha_realizacion=resultado.fecha_realizacion
    )


@router.put("/resultado_servicio/{cita_id}", response_model=ResultadoServicioResponse)
async def update_resultado_servicio(cita_id: int, resultado_servicio_update: ResultadoServicioCreate, db: Session = Depends(get_db)):
    # Buscar el resultado del servicio para la cita específica
    resultado = resultado_servicio.get_by_cita(db, cita_id=cita_id)

    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado del servicio no encontrado para esta cita")

    # Actualizar los campos del resultado de servicio
    resultado.resultado = resultado_servicio_update.resultado
    resultado.interpretacion = resultado_servicio_update.interpretacion
    resultado.archivo_adjunto = resultado_servicio_update.archivo_adjunto
    resultado.fecha_realizacion = resultado_servicio_update.fecha_realizacion

    # Marcar cita como atendida y registrar ingreso automaticamente (HU-13)
    cita_crud.marcar_atendida(db, cita_id=cita_id)

    # SC-042 / F24: al registrar el resultado, el examen avanza a 'Completado'.
    cita_obj = cita_crud.get(db, cita_id)
    if cita_obj and cita_obj.id_servicio_solicitado:
        ss = servicio_solicitado.get(db, cita_obj.id_servicio_solicitado)
        if ss:
            ss.estado_examen = 'Completado'

    db.commit()
    db.refresh(resultado)

    return ResultadoServicioResponse(
        id_resultado=resultado.id_resultado,
        id_cita=resultado.id_cita,
        id_veterinario=resultado.id_veterinario,
        resultado=resultado.resultado,
        interpretacion=resultado.interpretacion,
        archivo_adjunto=resultado.archivo_adjunto,
        fecha_realizacion=resultado.fecha_realizacion
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
    resultado = resultado_servicio.get_by_cita(db, cita_id=cita_id)
    if not resultado:
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

    resultado.archivo_adjunto = enlace
    db.commit()
    db.refresh(resultado)

    return {"archivo_adjunto": enlace}
