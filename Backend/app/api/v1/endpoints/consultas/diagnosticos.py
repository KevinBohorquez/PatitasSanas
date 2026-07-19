# app/api/v1/endpoints/consultas/diagnosticos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.config.database import get_db
from app.crud.consulta import consulta, diagnostico, historial_clinico, triaje, solicitud_atencion, tratamiento
from app.crud.catalogo import patologia
from app.queries import diagnostico_queries
from app.models import Tratamiento, Patologia
from app.schemas.consulta_schema import DiagnosticoCreate, DiagnosticoResponse, DiagnosticoCompletoUpdate

router = APIRouter()

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
        from app.crud.catalogo import patologia
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


@router.get("/diagnosticos/{id_consulta}", response_model=List[DiagnosticoResponse])
async def get_diagnosticos_by_consulta(
        id_consulta: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todos los diagnósticos relacionados con una consulta específica.
    """
    try:
        # Todos los diagnósticos relacionados con la consulta (vacía si no hay ninguno)
        diagnosticos = diagnostico.get_all_by_consulta(db, consulta_id=id_consulta)

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
        diagnostico_obj = diagnostico.get(db, id_diagnostico)

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
        tratamiento_patologia_diagnostico = diagnostico_queries.get_tratamiento_patologia_diagnostico(
            db, id_diagnostico=id_diagnostico
        )

        # Si hay patología pero aún no hay tratamiento, devolver diagnóstico + patología
        # para que el formulario se abra con esos datos (sin romper con 404).
        if not tratamiento_patologia_diagnostico:
            diagnostico_patologia = diagnostico_queries.get_diagnostico_patologia(
                db, id_diagnostico=id_diagnostico
            )

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
        diagnostico_obj = diagnostico.get(db, id_diagnostico)

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
        patologia_obj = patologia.get(db, diagnostico_obj.id_patologia)

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
            patologia_obj = patologia.get_by_nombre(db, nombre_patologia=nombre_pat)
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
        tratamiento_obj = tratamiento.get_by_consulta_patologia(
            db, consulta_id=diagnostico_obj.id_consulta, patologia_id=diagnostico_obj.id_patologia
        )

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
        tratamiento_patologia_diagnostico = diagnostico_queries.get_tratamiento_patologia_diagnostico(
            db, id_diagnostico=id_diagnostico
        )

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
            diagnostico_patologia = diagnostico_queries.get_diagnostico_patologia(
                db, id_diagnostico=id_diagnostico
            )

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
async def create_diagnostico_directo(
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
