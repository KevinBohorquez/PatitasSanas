import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.config.database import SessionLocal
from app.models.cita import Cita
from app.models.clientes import Cliente
from app.models.cliente_mascota import ClienteMascota
from app.models.mascota import Mascota
from app.models.servicio_solicitado import ServicioSolicitado
from app.models.servicio import Servicio
from app.models.resultado_servicio import ResultadoServicio
from app.models.veterinario import Veterinario
from app.services.notifications.email_service import send_reminder_email

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="America/Lima")


def _enviar_recordatorios(horas_antes: int) -> None:
    """Busca citas en la ventana de ±1 h alrededor de `horas_antes` y envía el correo."""
    db = SessionLocal()
    flag = "recordatorio_24h_enviado" if horas_antes == 24 else "recordatorio_4h_enviado"
    try:
        now = datetime.now()
        ventana_inicio = now + timedelta(hours=horas_antes - 1)
        ventana_fin    = now + timedelta(hours=horas_antes + 1)

        citas = (
            db.query(Cita, Mascota, Cliente, Servicio, Veterinario)
            .join(Mascota, Cita.id_mascota == Mascota.id_mascota)
            .join(ClienteMascota, ClienteMascota.id_mascota == Mascota.id_mascota)
            .join(Cliente, Cliente.id_cliente == ClienteMascota.id_cliente)
            .outerjoin(ServicioSolicitado, ServicioSolicitado.id_servicio_solicitado == Cita.id_servicio_solicitado)
            .outerjoin(Servicio, Servicio.id_servicio == ServicioSolicitado.id_servicio)
            .outerjoin(ResultadoServicio, ResultadoServicio.id_cita == Cita.id_cita)
            .outerjoin(Veterinario, Veterinario.id_veterinario == ResultadoServicio.id_veterinario)
            .filter(
                Cita.estado_cita == "Programada",
                Cita.fecha_hora_programada >= ventana_inicio,
                Cita.fecha_hora_programada <= ventana_fin,
                getattr(Cita, flag) == False,
            )
            .all()
        )

        for cita, mascota, cliente, servicio, veterinario in citas:
            nombre_completo = f"{cliente.nombre} {cliente.apellido_paterno}"
            veterinario_nombre = (
                f"{veterinario.nombre} {veterinario.apellido_paterno}" if veterinario else None
            )
            servicio_nombre = servicio.nombre_servicio if servicio else None
            enviado = send_reminder_email(
                to_email=cliente.email,
                cliente_nombre=nombre_completo,
                mascota_nombre=mascota.nombre,
                fecha_hora=cita.fecha_hora_programada,
                horas_antes=horas_antes,
                veterinario_nombre=veterinario_nombre,
                servicio_nombre=servicio_nombre,
            )
            if enviado:
                setattr(cita, flag, True)
                db.commit()
                logger.info(
                    "Flag %s marcado para cita id=%s", flag, cita.id_cita
                )

    except Exception as exc:
        logger.error("Error en recordatorio %dh: %s", horas_antes, exc)
        db.rollback()
    finally:
        db.close()


def check_reminders() -> None:
    logger.info("Scheduler: revisando recordatorios [%s]", datetime.now().strftime("%H:%M:%S"))
    _enviar_recordatorios(24)
    _enviar_recordatorios(4)


def start_scheduler() -> None:
    scheduler.add_job(
        check_reminders,
        trigger="interval",
        minutes=30,
        id="reminder_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler de recordatorios iniciado (cada 30 min)")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler de recordatorios detenido")
