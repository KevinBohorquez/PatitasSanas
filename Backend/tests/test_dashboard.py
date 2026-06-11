"""
Tests unitarios para get_tasa_asistencia.
No requieren conexión a base de datos: la sesión SQLAlchemy se mockea.
"""
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace

from app.crud.dashboard_crud import CRUDDashboard


def make_db(rows):
    """Devuelve un mock de Session cuya cadena .query().group_by().all() retorna `rows`."""
    db = MagicMock()
    db.query.return_value.group_by.return_value.all.return_value = rows
    return db


def row(estado, total):
    return SimpleNamespace(estado_cita=estado, total=total)


crud = CRUDDashboard()


class TestGetTasaAsistencia:

    def test_caso_normal(self):
        """Con los tres estados presentes, calcula la tasa correctamente."""
        db = make_db([
            row('Atendida', 38),
            row('Cancelada', 5),
            row('Programada', 12),
        ])
        resultado = crud.get_tasa_asistencia(db)

        assert resultado['Atendida'] == 38
        assert resultado['Cancelada'] == 5
        assert resultado['Programada'] == 12
        assert resultado['tasa_asistencia'] == round(38 / 43 * 100, 2)

    def test_bd_vacia_no_falla(self):
        """Sin ninguna cita en la BD no debe lanzar excepción ni dividir entre cero."""
        db = make_db([])
        resultado = crud.get_tasa_asistencia(db)

        assert resultado['tasa_asistencia'] == 0.0
        assert resultado['Programada'] == 0
        assert resultado['Cancelada'] == 0
        assert resultado['Atendida'] == 0

    def test_solo_programadas_tasa_cero(self):
        """Citas solo Programadas no son 'resueltas', la tasa debe ser 0."""
        db = make_db([row('Programada', 10)])
        resultado = crud.get_tasa_asistencia(db)

        assert resultado['tasa_asistencia'] == 0.0
        assert resultado['Atendida'] == 0
        assert resultado['Cancelada'] == 0

    def test_todas_atendidas_tasa_100(self):
        """Sin canceladas la tasa de asistencia es 100%."""
        db = make_db([row('Atendida', 20)])
        resultado = crud.get_tasa_asistencia(db)

        assert resultado['tasa_asistencia'] == 100.0

    def test_ninguna_atendida_tasa_cero(self):
        """Si todas las resueltas son canceladas, la tasa es 0."""
        db = make_db([row('Cancelada', 15)])
        resultado = crud.get_tasa_asistencia(db)

        assert resultado['tasa_asistencia'] == 0.0

    def test_redondeo_dos_decimales(self):
        """1 atendida de 3 resueltas: 33.33%, no 33.333..."""
        db = make_db([
            row('Atendida', 1),
            row('Cancelada', 2),
        ])
        resultado = crud.get_tasa_asistencia(db)

        assert resultado['tasa_asistencia'] == 33.33

    def test_estructura_respuesta_siempre_tiene_cuatro_claves(self):
        """El frontend espera exactamente estas claves aunque no haya datos."""
        db = make_db([])
        resultado = crud.get_tasa_asistencia(db)

        assert set(resultado.keys()) == {'Programada', 'Cancelada', 'Atendida', 'tasa_asistencia'}

    def test_programadas_no_afectan_la_tasa(self):
        """Las citas Programadas se cuentan pero no entran en el cálculo de la tasa."""
        db = make_db([
            row('Atendida', 10),
            row('Cancelada', 10),
            row('Programada', 9999),
        ])
        resultado = crud.get_tasa_asistencia(db)

        assert resultado['tasa_asistencia'] == 50.0
