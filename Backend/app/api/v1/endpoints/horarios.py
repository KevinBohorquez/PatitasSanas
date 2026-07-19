# app/api/v1/endpoints/horarios.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
import calendar as _calendar

from app.config.database import get_db
from app.crud.horario_crud import horario_veterinario, horario_excepcion
from app.queries import horario_queries
from app.models.horario_veterinario import HorarioVeterinario
from app.models.horario_excepcion import HorarioExcepcion
from app.models.veterinario import Veterinario

router = APIRouter()

# weekday() -> 0=Lunes ... 6=Domingo
DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
TURNOS = ['Mañana', 'Tarde', 'Noche', 'Madrugada']


class HorarioRecurrenteCreate(BaseModel):
    id_veterinario: int
    dia_semana: str
    turno: str


class ExcepcionCreate(BaseModel):
    id_veterinario: int
    fecha: date
    turno: Optional[str] = None
    trabaja: bool = True


# ================= HORARIO RECURRENTE (gestiona el admin) =================
@router.post("/recurrente")
def crear_horario_recurrente(data: HorarioRecurrenteCreate, db: Session = Depends(get_db)):
    if data.dia_semana not in DIAS:
        raise HTTPException(status_code=400, detail=f"dia_semana debe ser uno de: {', '.join(DIAS)}")
    if data.turno not in TURNOS:
        raise HTTPException(status_code=400, detail=f"turno debe ser uno de: {', '.join(TURNOS)}")
    if not db.get(Veterinario, data.id_veterinario):
        raise HTTPException(status_code=404, detail="Veterinario no encontrado")
    existe = horario_veterinario.get_by_vet_dia_turno(
        db, id_veterinario=data.id_veterinario, dia_semana=data.dia_semana, turno=data.turno)
    if existe:
        raise HTTPException(status_code=400, detail="Ese veterinario ya tiene ese turno ese día")
    h = HorarioVeterinario(id_veterinario=data.id_veterinario, dia_semana=data.dia_semana, turno=data.turno)
    db.add(h); db.commit(); db.refresh(h)
    return {"id_horario": h.id_horario, "id_veterinario": h.id_veterinario,
            "dia_semana": h.dia_semana, "turno": h.turno}


@router.get("/recurrente")
def listar_horario_recurrente(db: Session = Depends(get_db),
                              id_veterinario: Optional[int] = Query(None)):
    horarios = horario_veterinario.list(db, id_veterinario=id_veterinario)
    info = horario_queries.info_veterinarios(db, {h.id_veterinario for h in horarios})
    return [
        {"id_horario": h.id_horario, "id_veterinario": h.id_veterinario,
         "veterinario": info.get(h.id_veterinario, {}).get("nombre"),
         "dia_semana": h.dia_semana, "turno": h.turno}
        for h in horarios
    ]


@router.delete("/recurrente/{id_horario}")
def eliminar_horario_recurrente(id_horario: int, db: Session = Depends(get_db)):
    h = db.get(HorarioVeterinario, id_horario)
    if not h:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    db.delete(h); db.commit()
    return {"message": "Horario eliminado", "success": True}


# ================= EXCEPCIONES POR FECHA (gestiona el admin) =================
@router.post("/excepcion")
def crear_excepcion(data: ExcepcionCreate, db: Session = Depends(get_db)):
    if data.trabaja and data.turno not in TURNOS:
        raise HTTPException(status_code=400, detail="Si trabaja, el turno es obligatorio y válido")
    if not db.get(Veterinario, data.id_veterinario):
        raise HTTPException(status_code=404, detail="Veterinario no encontrado")
    existe = horario_excepcion.get_by_vet_fecha(
        db, id_veterinario=data.id_veterinario, fecha=data.fecha)
    if existe:
        # una excepción por vet y fecha: se actualiza
        existe.turno = data.turno if data.trabaja else None
        existe.trabaja = data.trabaja
        db.commit(); db.refresh(existe)
        obj = existe
    else:
        obj = HorarioExcepcion(id_veterinario=data.id_veterinario, fecha=data.fecha,
                               turno=data.turno if data.trabaja else None, trabaja=data.trabaja)
        db.add(obj); db.commit(); db.refresh(obj)
    return {"id_excepcion": obj.id_excepcion, "id_veterinario": obj.id_veterinario,
            "fecha": obj.fecha, "turno": obj.turno, "trabaja": obj.trabaja}


@router.get("/excepcion")
def listar_excepciones(db: Session = Depends(get_db),
                       fecha: Optional[date] = Query(None),
                       id_veterinario: Optional[int] = Query(None)):
    exc = horario_excepcion.list(db, fecha=fecha, id_veterinario=id_veterinario)
    info = horario_queries.info_veterinarios(db, {e.id_veterinario for e in exc})
    return [
        {"id_excepcion": e.id_excepcion, "id_veterinario": e.id_veterinario,
         "veterinario": info.get(e.id_veterinario, {}).get("nombre"),
         "fecha": e.fecha, "turno": e.turno, "trabaja": e.trabaja}
        for e in exc
    ]


@router.delete("/excepcion/{id_excepcion}")
def eliminar_excepcion(id_excepcion: int, db: Session = Depends(get_db)):
    e = db.get(HorarioExcepcion, id_excepcion)
    if not e:
        raise HTTPException(status_code=404, detail="Excepción no encontrada")
    db.delete(e); db.commit()
    return {"message": "Excepción eliminada", "success": True}


# ================= ROSTER EFECTIVO (recepcionista + admin) =================
def _roster_fecha(db: Session, fecha: date):
    """Combina el horario recurrente del día de la semana con las excepciones de esa
    fecha (que sustituyen al recurrente por veterinario). Devuelve (dia_semana, lista)."""
    dia = DIAS[fecha.weekday()]
    base = horario_veterinario.list_by_dia(db, dia_semana=dia)
    excepciones = horario_excepcion.list_by_fecha(db, fecha=fecha)
    exc_por_vet = {e.id_veterinario: e for e in excepciones}

    roster = {}
    for h in base:
        if h.id_veterinario in exc_por_vet:
            continue
        roster[(h.id_veterinario, h.turno)] = "recurrente"
    for vid, e in exc_por_vet.items():
        if e.trabaja and e.turno:
            roster[(vid, e.turno)] = "excepcion"

    info = horario_queries.info_veterinarios(db, {vid for vid, _ in roster.keys()})
    return dia, [
        {"id_veterinario": vid, "veterinario": info.get(vid, {}).get("nombre"),
         "especialidad": info.get(vid, {}).get("especialidad"),
         "estado": info.get(vid, {}).get("estado"),
         "turno": turno, "origen": origen}
        for (vid, turno), origen in sorted(roster.items())
    ]


@router.get("/dia/{fecha}")
def veterinarios_del_dia(fecha: date, db: Session = Depends(get_db)):
    """Quiénes trabajan una fecha concreta, con su turno."""
    dia, vets = _roster_fecha(db, fecha)
    return {"fecha": fecha, "dia_semana": dia, "total": len(vets), "veterinarios": vets}


@router.get("/semana/{fecha}")
def semana(fecha: date, db: Session = Depends(get_db)):
    """Roster de la semana (Lunes a Domingo) que contiene la fecha dada."""
    lunes = fecha - timedelta(days=fecha.weekday())
    dias = []
    for i in range(7):
        f = lunes + timedelta(days=i)
        dia, vets = _roster_fecha(db, f)
        dias.append({"fecha": f, "dia_semana": dia, "veterinarios": vets})
    return {"inicio": lunes, "fin": lunes + timedelta(days=6), "dias": dias}


@router.get("/mes/{anio}/{mes}")
def mes(anio: int, mes: int, db: Session = Depends(get_db)):
    """Resumen por día de un mes (total de veterinarios en turno y conteo por turno)."""
    if not (1 <= mes <= 12):
        raise HTTPException(status_code=400, detail="mes debe estar entre 1 y 12")
    ndias = _calendar.monthrange(anio, mes)[1]
    dias = []
    for d in range(1, ndias + 1):
        f = date(anio, mes, d)
        dia, vets = _roster_fecha(db, f)
        turnos = {}
        for v in vets:
            turnos[v["turno"]] = turnos.get(v["turno"], 0) + 1
        dias.append({
            "fecha": f, "dia_semana": dia, "total": len(vets), "turnos": turnos,
            "veterinarios": [
                {"veterinario": v["veterinario"], "turno": v["turno"], "estado": v["estado"]}
                for v in vets
            ],
        })
    return {"anio": anio, "mes": mes, "dias": dias}
