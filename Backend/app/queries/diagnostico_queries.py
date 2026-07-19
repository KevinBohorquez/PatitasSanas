# app/queries/diagnostico_queries.py
"""
Consultas de lectura para el diagnóstico.

Ensamblados de diagnóstico + patología + tratamiento (JOINs de varias tablas)
para el formulario de "Modificar Diagnóstico". No son persistencia de una sola
entidad y por eso viven fuera del CRUD.
"""
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models import Diagnostico, Tratamiento, Patologia


def get_tratamiento_patologia_diagnostico(
    db: Session, *, id_diagnostico: int
) -> List[Tuple[Tratamiento, Patologia, Diagnostico]]:
    """Filas (Tratamiento, Patologia, Diagnostico) para un diagnóstico (INNER JOIN)."""
    return (
        db.query(Tratamiento, Patologia, Diagnostico)
        .join(Patologia, Patologia.id_patologia == Tratamiento.id_patologia)
        .join(Diagnostico, Diagnostico.id_patologia == Patologia.id_patologia)
        .filter(Diagnostico.id_diagnostico == id_diagnostico)
        .all()
    )


def get_diagnostico_patologia(db: Session, *, id_diagnostico: int):
    """Fila (Diagnostico, Patologia) de un diagnóstico, o None."""
    return (
        db.query(Diagnostico, Patologia)
        .join(Patologia, Patologia.id_patologia == Diagnostico.id_patologia)
        .filter(Diagnostico.id_diagnostico == id_diagnostico)
        .first()
    )
