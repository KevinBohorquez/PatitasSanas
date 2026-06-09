from fastapi import APIRouter
from datetime import datetime
from app.services.notifications.reminder_scheduler import scheduler

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
