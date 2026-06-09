import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
import smtplib

from app.services.notifications.email_template import build_reminder_html
from app.services.notifications.email_service import send_reminder_email
from app.services.notifications.reminder_scheduler import _enviar_recordatorios


# ──────────────────────────────────────────────
# Tests: email_template
# ──────────────────────────────────────────────

def test_template_contiene_datos_cliente():
    html = build_reminder_html(
        cliente_nombre="Maria Lopez",
        mascota_nombre="Toby",
        fecha_formateada="15/06/2026",
        hora_formateada="10:00",
        horas_antes=24,
    )
    assert "Maria Lopez" in html
    assert "Toby" in html
    assert "15/06/2026" in html
    assert "10:00" in html
    assert "24" in html


def test_template_contiene_datos_4h():
    html = build_reminder_html(
        cliente_nombre="Carlos Ruiz",
        mascota_nombre="Luna",
        fecha_formateada="20/06/2026",
        hora_formateada="14:30",
        horas_antes=4,
    )
    assert "4" in html
    assert "Luna" in html


def test_template_es_html_valido():
    html = build_reminder_html("A", "B", "01/01/2026", "08:00", 24)
    assert html.strip().startswith("<!DOCTYPE html>") or "<html" in html
    assert "</html>" in html


# ──────────────────────────────────────────────
# Tests: email_service
# ──────────────────────────────────────────────

def test_send_reminder_sin_credenciales_retorna_false():
    with patch.dict("os.environ", {}, clear=True):
        resultado = send_reminder_email(
            to_email="cliente@ejemplo.com",
            cliente_nombre="Juan Perez",
            mascota_nombre="Rex",
            fecha_hora=datetime(2026, 6, 15, 10, 0),
            horas_antes=24,
        )
    assert resultado is False


def test_send_reminder_exitoso():
    mock_smtp = MagicMock()
    env_vars = {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "test@gmail.com",
        "SMTP_PASSWORD": "app_password",
        "SMTP_FROM": "test@gmail.com",
    }
    with patch.dict("os.environ", env_vars):
        with patch("smtplib.SMTP") as mock_smtp_class:
            mock_smtp_class.return_value.__enter__ = lambda s: mock_smtp
            mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

            resultado = send_reminder_email(
                to_email="cliente@ejemplo.com",
                cliente_nombre="Ana Torres",
                mascota_nombre="Michi",
                fecha_hora=datetime(2026, 6, 20, 14, 30),
                horas_antes=4,
            )
    assert resultado is True


def test_send_reminder_error_autenticacion_retorna_false():
    env_vars = {
        "SMTP_USER": "test@gmail.com",
        "SMTP_PASSWORD": "wrong_password",
    }
    with patch.dict("os.environ", env_vars):
        with patch("smtplib.SMTP") as mock_smtp_class:
            mock_smtp_instance = MagicMock()
            mock_smtp_class.return_value.__enter__ = lambda s: mock_smtp_instance
            mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)
            mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")

            resultado = send_reminder_email(
                to_email="cliente@ejemplo.com",
                cliente_nombre="Luis Gomez",
                mascota_nombre="Peludo",
                fecha_hora=datetime(2026, 6, 18, 9, 0),
                horas_antes=24,
            )
    assert resultado is False


def test_send_reminder_error_conexion_retorna_false():
    env_vars = {
        "SMTP_USER": "test@gmail.com",
        "SMTP_PASSWORD": "pass",
    }
    with patch.dict("os.environ", env_vars):
        with patch("smtplib.SMTP", side_effect=smtplib.SMTPConnectError(421, b"Connection refused")):
            resultado = send_reminder_email(
                to_email="cliente@ejemplo.com",
                cliente_nombre="Rosa Diaz",
                mascota_nombre="Nala",
                fecha_hora=datetime(2026, 6, 19, 11, 0),
                horas_antes=4,
            )
    assert resultado is False


# ──────────────────────────────────────────────
# Tests: reminder_scheduler
# ──────────────────────────────────────────────

def _make_cita(horas_offset: int, flag_24: bool = False, flag_4: bool = False):
    """Crea objetos mock de (Cita, Mascota, Cliente) para usar en tests."""
    cita = MagicMock()
    cita.id_cita = 1
    cita.estado_cita = "Programada"
    cita.fecha_hora_programada = datetime.now() + timedelta(hours=horas_offset)
    cita.recordatorio_24h_enviado = flag_24
    cita.recordatorio_4h_enviado = flag_4

    mascota = MagicMock()
    mascota.nombre = "Firulais"

    cliente = MagicMock()
    cliente.nombre = "Pedro"
    cliente.apellido_paterno = "Sanchez"
    cliente.email = "pedro@ejemplo.com"

    return cita, mascota, cliente


def test_recordatorio_24h_envia_correo_y_marca_flag():
    cita, mascota, cliente = _make_cita(horas_offset=24)

    mock_db = MagicMock()
    mock_db.query.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
        (cita, mascota, cliente)
    ]

    with patch("app.services.notifications.reminder_scheduler.SessionLocal", return_value=mock_db):
        with patch("app.services.notifications.reminder_scheduler.send_reminder_email", return_value=True) as mock_send:
            _enviar_recordatorios(24)

    mock_send.assert_called_once_with(
        to_email=cliente.email,
        cliente_nombre="Pedro Sanchez",
        mascota_nombre=mascota.nombre,
        fecha_hora=cita.fecha_hora_programada,
        horas_antes=24,
    )
    assert cita.recordatorio_24h_enviado is True
    mock_db.commit.assert_called_once()


def test_recordatorio_4h_envia_correo_y_marca_flag():
    cita, mascota, cliente = _make_cita(horas_offset=4)

    mock_db = MagicMock()
    mock_db.query.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
        (cita, mascota, cliente)
    ]

    with patch("app.services.notifications.reminder_scheduler.SessionLocal", return_value=mock_db):
        with patch("app.services.notifications.reminder_scheduler.send_reminder_email", return_value=True) as mock_send:
            _enviar_recordatorios(4)

    mock_send.assert_called_once()
    assert cita.recordatorio_4h_enviado is True


def test_recordatorio_no_envia_si_correo_falla():
    cita, mascota, cliente = _make_cita(horas_offset=24)

    mock_db = MagicMock()
    mock_db.query.return_value.join.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
        (cita, mascota, cliente)
    ]

    with patch("app.services.notifications.reminder_scheduler.SessionLocal", return_value=mock_db):
        with patch("app.services.notifications.reminder_scheduler.send_reminder_email", return_value=False):
            _enviar_recordatorios(24)

    # El flag NO debe marcarse si el envío falló
    assert cita.recordatorio_24h_enviado is not True
    mock_db.commit.assert_not_called()


def test_recordatorio_sin_citas_no_envia_nada():
    mock_db = MagicMock()
    mock_db.query.return_value.join.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = []

    with patch("app.services.notifications.reminder_scheduler.SessionLocal", return_value=mock_db):
        with patch("app.services.notifications.reminder_scheduler.send_reminder_email") as mock_send:
            _enviar_recordatorios(24)

    mock_send.assert_not_called()
    mock_db.commit.assert_not_called()


def test_recordatorio_maneja_excepcion_y_hace_rollback():
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("DB error")

    with patch("app.services.notifications.reminder_scheduler.SessionLocal", return_value=mock_db):
        # No debe lanzar excepción hacia afuera
        _enviar_recordatorios(24)

    mock_db.rollback.assert_called_once()
