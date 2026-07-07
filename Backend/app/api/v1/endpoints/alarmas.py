from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from app.services.notifications.reminder_scheduler import scheduler
from app.services.notifications.email_service import send_reminder_email

router = APIRouter()


@router.get("/status")
def get_scheduler_status():
    jobs = scheduler.get_jobs()
    job_info = []
    for job in jobs:
        job_info.append({
            "id": job.id,
            "proxima_ejecucion": job.next_run_time.isoformat() if job.next_run_time else None,
        })

    return {
        "scheduler_activo": scheduler.running,
        "timestamp": datetime.now().isoformat(),
        "jobs": job_info,
    }


class CorreoPruebaRequest(BaseModel):
    email: EmailStr


@router.post("/enviar-prueba")
def enviar_correo_prueba(datos: CorreoPruebaRequest):
    """Envia un recordatorio de ejemplo al correo indicado.

    Pensado para demostraciones: dispara un correo al instante con datos de
    ejemplo, sin depender del scheduler ni de una cita real.
    """
    enviado = send_reminder_email(
        to_email=datos.email,
        cliente_nombre="Juan Perez",
        mascota_nombre="Firulais",
        fecha_hora=datetime.now() + timedelta(hours=24),
        horas_antes=24,
        veterinario_nombre="Dra. Ana Torres",
        servicio_nombre="Consulta general",
    )

    if not enviado:
        raise HTTPException(
            status_code=502,
            detail="No se pudo enviar el correo. Revisa la configuracion de Brevo.",
        )

    return {
        "enviado": True,
        "destinatario": datos.email,
        "mensaje": "Recordatorio de ejemplo enviado correctamente",
    }
