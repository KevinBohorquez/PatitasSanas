# app/api/v1/endpoints/horarios_recep.py
# Cronograma de recepcionistas (espejo del de veterinarios).
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
import calendar as _calendar

from app.config.database import get_db
from app.crud.horario_crud import horario_recepcionista, horario_excepcion_recep
from app.queries import horario_queries
from app.models.horario_recepcionista import HorarioRecepcionista
from app.models.horario_excepcion_recep import HorarioExcepcionRecep
from app.models.recepcionista import Recepcionista

router = APIRouter()

DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
TURNOS = ['Mañana', 'Tarde', 'Noche', 'Madrugada']


class HorarioRecurrenteCreate(BaseModel):
    id_recepcionista: int
    dia_semana: str
    turno: str


class ExcepcionCreate(BaseModel):
    id_recepcionista: int
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
    if not db.get(Recepcionista, data.id_recepcionista):
        raise HTTPException(status_code=404, detail="Recepcionista no encontrada")
    existe = horario_recepcionista.get_by_recep_dia_turno(
        db, id_recepcionista=data.id_recepcionista, dia_semana=data.dia_semana, turno=data.turno)
    if existe:
        raise HTTPException(status_code=400, detail="Esa recepcionista ya tiene ese turno ese día")
    h = HorarioRecepcionista(id_recepcionista=data.id_recepcionista, dia_semana=data.dia_semana, turno=data.turno)
    db.add(h); db.commit(); db.refresh(h)
    return {"id_horario": h.id_horario, "id_recepcionista": h.id_recepcionista,
            "dia_semana": h.dia_semana, "turno": h.turno}


@router.get("/recurrente")
def listar_horario_recurrente(db: Session = Depends(get_db),
                              id_recepcionista: Optional[int] = Query(None)):
    horarios = horario_recepcionista.list(db, id_recepcionista=id_recepcionista)
    info = horario_queries.info_recepcionistas(db, {h.id_recepcionista for h in horarios})
    return [
        {"id_horario": h.id_horario, "id_recepcionista": h.id_recepcionista,
         "recepcionista": info.get(h.id_recepcionista, {}).get("nombre"),
         "dia_semana": h.dia_semana, "turno": h.turno}
        for h in horarios
    ]


@router.delete("/recurrente/{id_horario}")
def eliminar_horario_recurrente(id_horario: int, db: Session = Depends(get_db)):
    h = db.get(HorarioRecepcionista, id_horario)
    if not h:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    db.delete(h); db.commit()
    return {"message": "Horario eliminado", "success": True}


# ================= EXCEPCIONES POR FECHA =================
@router.post("/excepcion")
def crear_excepcion(data: ExcepcionCreate, db: Session = Depends(get_db)):
    if data.trabaja and data.turno not in TURNOS:
        raise HTTPException(status_code=400, detail="Si trabaja, el turno es obligatorio y válido")
    if not db.get(Recepcionista, data.id_recepcionista):
        raise HTTPException(status_code=404, detail="Recepcionista no encontrada")
    existe = horario_excepcion_recep.get_by_recep_fecha(
        db, id_recepcionista=data.id_recepcionista, fecha=data.fecha)
    if existe:
        existe.turno = data.turno if data.trabaja else None
        existe.trabaja = data.trabaja
        db.commit(); db.refresh(existe)
        obj = existe
    else:
        obj = HorarioExcepcionRecep(id_recepcionista=data.id_recepcionista, fecha=data.fecha,
                                    turno=data.turno if data.trabaja else None, trabaja=data.trabaja)
        db.add(obj); db.commit(); db.refresh(obj)
    return {"id_excepcion": obj.id_excepcion, "id_recepcionista": obj.id_recepcionista,
            "fecha": obj.fecha, "turno": obj.turno, "trabaja": obj.trabaja}


@router.get("/excepcion")
def listar_excepciones(db: Session = Depends(get_db),
                       fecha: Optional[date] = Query(None),
                       id_recepcionista: Optional[int] = Query(None)):
    exc = horario_excepcion_recep.list(db, fecha=fecha, id_recepcionista=id_recepcionista)
    info = horario_queries.info_recepcionistas(db, {e.id_recepcionista for e in exc})
    return [
        {"id_excepcion": e.id_excepcion, "id_recepcionista": e.id_recepcionista,
         "recepcionista": info.get(e.id_recepcionista, {}).get("nombre"),
         "fecha": e.fecha, "turno": e.turno, "trabaja": e.trabaja}
        for e in exc
    ]


@router.delete("/excepcion/{id_excepcion}")
def eliminar_excepcion(id_excepcion: int, db: Session = Depends(get_db)):
    e = db.get(HorarioExcepcionRecep, id_excepcion)
    if not e:
        raise HTTPException(status_code=404, detail="Excepción no encontrada")
    db.delete(e); db.commit()
    return {"message": "Excepción eliminada", "success": True}


# ================= ROSTER EFECTIVO =================
def _roster_fecha(db: Session, fecha: date):
    dia = DIAS[fecha.weekday()]
    base = horario_recepcionista.list_by_dia(db, dia_semana=dia)
    excepciones = horario_excepcion_recep.list_by_fecha(db, fecha=fecha)
    exc_por_recep = {e.id_recepcionista: e for e in excepciones}

    roster = {}
    for h in base:
        if h.id_recepcionista in exc_por_recep:
            continue
        roster[(h.id_recepcionista, h.turno)] = "recurrente"
    for rid, e in exc_por_recep.items():
        if e.trabaja and e.turno:
            roster[(rid, e.turno)] = "excepcion"

    info = horario_queries.info_recepcionistas(db, {rid for rid, _ in roster.keys()})
    return dia, [
        {"id_recepcionista": rid, "recepcionista": info.get(rid, {}).get("nombre"),
         "estado": info.get(rid, {}).get("estado"),
         "turno": turno, "origen": origen}
        for (rid, turno), origen in sorted(roster.items())
    ]


@router.get("/dia/{fecha}")
def recepcionistas_del_dia(fecha: date, db: Session = Depends(get_db)):
    dia, recs = _roster_fecha(db, fecha)
    return {"fecha": fecha, "dia_semana": dia, "total": len(recs), "recepcionistas": recs}


@router.get("/semana/{fecha}")
def semana(fecha: date, db: Session = Depends(get_db)):
    lunes = fecha - timedelta(days=fecha.weekday())
    dias = []
    for i in range(7):
        f = lunes + timedelta(days=i)
        dia, recs = _roster_fecha(db, f)
        dias.append({"fecha": f, "dia_semana": dia, "recepcionistas": recs})
    return {"inicio": lunes, "fin": lunes + timedelta(days=6), "dias": dias}


@router.get("/mes/{anio}/{mes}")
def mes(anio: int, mes: int, db: Session = Depends(get_db)):
    if not (1 <= mes <= 12):
        raise HTTPException(status_code=400, detail="mes debe estar entre 1 y 12")
    ndias = _calendar.monthrange(anio, mes)[1]
    dias = []
    for d in range(1, ndias + 1):
        f = date(anio, mes, d)
        dia, recs = _roster_fecha(db, f)
        turnos = {}
        for v in recs:
            turnos[v["turno"]] = turnos.get(v["turno"], 0) + 1
        dias.append({
            "fecha": f, "dia_semana": dia, "total": len(recs), "turnos": turnos,
            "recepcionistas": [
                {"recepcionista": v["recepcionista"], "turno": v["turno"], "estado": v["estado"]}
                for v in recs
            ],
        })
    return {"anio": anio, "mes": mes, "dias": dias}
