import logging
import os
from datetime import datetime

import httpx

from app.services.notifications.email_template import build_reminder_html

logger = logging.getLogger(__name__)

# API transaccional de Brevo (envío por HTTPS, funciona en Railway que bloquea SMTP)
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_reminder_email(
    to_email: str,
    cliente_nombre: str,
    mascota_nombre: str,
    fecha_hora: datetime,
    horas_antes: int,
    veterinario_nombre: str | None = None,
    servicio_nombre: str | None = None,
) -> bool:
    api_key = os.getenv("BREVO_API_KEY")
    # Remitente: debe ser un correo verificado en Brevo. Reutiliza SMTP_FROM/SMTP_USER si existen.
    sender_email = (
        os.getenv("BREVO_SENDER_EMAIL")
        or os.getenv("SMTP_FROM")
        or os.getenv("SMTP_USER")
    )
    sender_name = os.getenv("BREVO_SENDER_NAME", "Patitas Sanas")

    if not api_key:
        logger.error("BREVO_API_KEY no configurada — no se envían recordatorios")
        return False
    if not sender_email:
        logger.error("Remitente no configurado (BREVO_SENDER_EMAIL / SMTP_FROM / SMTP_USER)")
        return False

    asunto = f"Recordatorio: cita de {mascota_nombre} en {horas_antes} horas"

    fecha_formateada = fecha_hora.strftime("%d/%m/%Y")
    hora_formateada = fecha_hora.strftime("%H:%M")

    html = build_reminder_html(
        cliente_nombre=cliente_nombre,
        mascota_nombre=mascota_nombre,
        fecha_formateada=fecha_formateada,
        hora_formateada=hora_formateada,
        horas_antes=horas_antes,
        veterinario_nombre=veterinario_nombre,
        servicio_nombre=servicio_nombre,
    )

    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": to_email, "name": cliente_nombre}],
        "subject": asunto,
        "htmlContent": html,
    }
    headers = {
        "api-key": api_key,
        "content-type": "application/json",
        "accept": "application/json",
    }

    try:
        response = httpx.post(BREVO_API_URL, json=payload, headers=headers, timeout=20)

        if response.status_code in (200, 201):
            logger.info(
                "Recordatorio %dh enviado a %s para mascota '%s'",
                horas_antes, to_email, mascota_nombre,
            )
            return True

        logger.error(
            "Brevo rechazó el envío a %s (HTTP %s): %s",
            to_email, response.status_code, response.text,
        )

    except httpx.TimeoutException:
        logger.error("Timeout al conectar con Brevo para enviar a %s", to_email)
    except httpx.RequestError as exc:
        logger.error("Error de red al enviar recordatorio a %s vía Brevo: %s", to_email, exc)
    except Exception as exc:
        logger.error("Error inesperado al enviar correo a %s: %s", to_email, exc)

    return False
