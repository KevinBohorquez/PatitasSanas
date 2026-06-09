import smtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

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

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <style>
        body      {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
        .container{{ max-width: 580px; margin: 32px auto; background: #ffffff;
                     border-radius: 8px; overflow: hidden;
                     box-shadow: 0 2px 8px rgba(0,0,0,.12); }}
        .header   {{ background: #2e7d32; padding: 24px 32px; }}
        .header h1{{ color: #ffffff; margin: 0; font-size: 20px; }}
        .body     {{ padding: 28px 32px; color: #333333; }}
        .body p   {{ line-height: 1.6; margin: 8px 0; }}
        .highlight{{ background: #e8f5e9; border-left: 4px solid #2e7d32;
                     border-radius: 4px; padding: 14px 18px; margin: 20px 0; }}
        .highlight p {{ margin: 4px 0; }}
        .badge    {{ display: inline-block; background: #2e7d32; color: #fff;
                     padding: 4px 12px; border-radius: 12px; font-size: 13px; }}
        .footer   {{ background: #f0f0f0; text-align: center; padding: 14px;
                     font-size: 12px; color: #888888; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🐾 Patitas Sanas — Recordatorio de cita</h1>
        </div>
        <div class="body">
          <p>Hola, <strong>{cliente_nombre}</strong>.</p>
          <p>Te recordamos que tu mascota tiene una cita programada
             <span class="badge">en {horas_antes} horas</span>.</p>

          <div class="highlight">
            <p><strong>Mascota:</strong> {mascota_nombre}</p>
            <p><strong>Fecha:</strong> {fecha_formateada}</p>
            <p><strong>Hora:</strong> {hora_formateada}</p>
          </div>

          <p>Por favor, llega con al menos 10 minutos de anticipación.</p>
          <p>Si necesitas cancelar o reprogramar, contáctanos a la brevedad.</p>
          <p>¡Hasta pronto! 🐶🐱</p>
        </div>
        <div class="footer">
          Veterinaria Patitas Sanas — Este correo es generado automáticamente.
        </div>
      </div>
    </body>
    </html>
    """

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
