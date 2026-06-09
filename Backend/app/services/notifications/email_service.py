import smtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from app.services.notifications.email_template import build_reminder_html

logger = logging.getLogger(__name__)


def send_reminder_email(
    to_email: str,
    cliente_nombre: str,
    mascota_nombre: str,
    fecha_hora: datetime,
    horas_antes: int,
) -> bool:
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_user or not smtp_password:
        logger.error("Credenciales SMTP no configuradas (SMTP_USER / SMTP_PASSWORD)")
        return False

    asunto = (
        f"Recordatorio: cita de {mascota_nombre} en {horas_antes} horas"
    )

    fecha_formateada = fecha_hora.strftime("%d/%m/%Y")
    hora_formateada = fecha_hora.strftime("%H:%M")

    html = build_reminder_html(
        cliente_nombre=cliente_nombre,
        mascota_nombre=mascota_nombre,
        fecha_formateada=fecha_formateada,
        hora_formateada=hora_formateada,
        horas_antes=horas_antes,
    )

    try:
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"] = smtp_from
        mensaje["To"] = to_email
        mensaje.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from, to_email, mensaje.as_string())

        logger.info(
            "Recordatorio %dh enviado a %s para mascota '%s'",
            horas_antes, to_email, mascota_nombre,
        )
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Error de autenticación SMTP — revisa SMTP_USER y SMTP_PASSWORD")
    except smtplib.SMTPConnectError:
        logger.error("No se pudo conectar al servidor SMTP (%s:%s)", smtp_host, smtp_port)
    except smtplib.SMTPException as exc:
        logger.error("Error SMTP al enviar recordatorio a %s: %s", to_email, exc)
    except Exception as exc:
        logger.error("Error inesperado al enviar correo a %s: %s", to_email, exc)

    return False
