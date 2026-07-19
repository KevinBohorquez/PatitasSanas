# app/crud/horario_crud.py
"""
CRUD de los horarios (recurrentes y excepciones) de veterinarios y recepcionistas.

Acceso a una sola entidad (filtros por veterinario/recepcionista, día o fecha).
Los ensamblados con nombre/especialidad/estado viven en app.queries.horario_queries.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base_crud import CRUDBase
from app.models.horario_veterinario import HorarioVeterinario
from app.models.horario_excepcion import HorarioExcepcion
from app.models.horario_recepcionista import HorarioRecepcionista
from app.models.horario_excepcion_recep import HorarioExcepcionRecep


class CRUDHorarioVeterinario(CRUDBase[HorarioVeterinario, None, None]):

    def get_by_vet_dia_turno(self, db: Session, *, id_veterinario: int, dia_semana: str,
                             turno: str) -> Optional[HorarioVeterinario]:
        return db.query(HorarioVeterinario).filter_by(
            id_veterinario=id_veterinario, dia_semana=dia_semana, turno=turno).first()

    def list(self, db: Session, *, id_veterinario: Optional[int] = None) -> List[HorarioVeterinario]:
        q = db.query(HorarioVeterinario)
        if id_veterinario:
            q = q.filter_by(id_veterinario=id_veterinario)
        return q.all()

    def list_by_dia(self, db: Session, *, dia_semana: str) -> List[HorarioVeterinario]:
        return db.query(HorarioVeterinario).filter_by(dia_semana=dia_semana).all()


class CRUDHorarioExcepcion(CRUDBase[HorarioExcepcion, None, None]):

    def get_by_vet_fecha(self, db: Session, *, id_veterinario: int, fecha) -> Optional[HorarioExcepcion]:
        return db.query(HorarioExcepcion).filter_by(
            id_veterinario=id_veterinario, fecha=fecha).first()

    def list(self, db: Session, *, fecha=None, id_veterinario: Optional[int] = None) -> List[HorarioExcepcion]:
        q = db.query(HorarioExcepcion)
        if fecha:
            q = q.filter_by(fecha=fecha)
        if id_veterinario:
            q = q.filter_by(id_veterinario=id_veterinario)
        return q.all()

    def list_by_fecha(self, db: Session, *, fecha) -> List[HorarioExcepcion]:
        return db.query(HorarioExcepcion).filter_by(fecha=fecha).all()


class CRUDHorarioRecepcionista(CRUDBase[HorarioRecepcionista, None, None]):

    def get_by_recep_dia_turno(self, db: Session, *, id_recepcionista: int, dia_semana: str,
                               turno: str) -> Optional[HorarioRecepcionista]:
        return db.query(HorarioRecepcionista).filter_by(
            id_recepcionista=id_recepcionista, dia_semana=dia_semana, turno=turno).first()

    def list(self, db: Session, *, id_recepcionista: Optional[int] = None) -> List[HorarioRecepcionista]:
        q = db.query(HorarioRecepcionista)
        if id_recepcionista:
            q = q.filter_by(id_recepcionista=id_recepcionista)
        return q.all()

    def list_by_dia(self, db: Session, *, dia_semana: str) -> List[HorarioRecepcionista]:
        return db.query(HorarioRecepcionista).filter_by(dia_semana=dia_semana).all()


class CRUDHorarioExcepcionRecep(CRUDBase[HorarioExcepcionRecep, None, None]):

    def get_by_recep_fecha(self, db: Session, *, id_recepcionista: int, fecha) -> Optional[HorarioExcepcionRecep]:
        return db.query(HorarioExcepcionRecep).filter_by(
            id_recepcionista=id_recepcionista, fecha=fecha).first()

    def list(self, db: Session, *, fecha=None, id_recepcionista: Optional[int] = None) -> List[HorarioExcepcionRecep]:
        q = db.query(HorarioExcepcionRecep)
        if fecha:
            q = q.filter_by(fecha=fecha)
        if id_recepcionista:
            q = q.filter_by(id_recepcionista=id_recepcionista)
        return q.all()

    def list_by_fecha(self, db: Session, *, fecha) -> List[HorarioExcepcionRecep]:
        return db.query(HorarioExcepcionRecep).filter_by(fecha=fecha).all()


horario_veterinario = CRUDHorarioVeterinario(HorarioVeterinario)
horario_excepcion = CRUDHorarioExcepcion(HorarioExcepcion)
horario_recepcionista = CRUDHorarioRecepcionista(HorarioRecepcionista)
horario_excepcion_recep = CRUDHorarioExcepcionRecep(HorarioExcepcionRecep)
