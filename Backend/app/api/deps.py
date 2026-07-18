# app/api/deps.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.crud import cliente, mascota
from app.models.clientes import Cliente
from app.models.mascota import Mascota

# ===== DEPENDENCIAS DE VALIDACIÓN =====
def get_cliente_or_404(
    cliente_id: int,
    db: Session = Depends(get_db)
) -> Cliente:
    """Obtener cliente o retornar 404"""
    cli = cliente.get(db, cliente_id)
    if not cli:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cli

def get_mascota_or_404(
    mascota_id: int,
    db: Session = Depends(get_db)
) -> Mascota:
    """Obtener mascota o retornar 404"""
    masc = mascota.get(db, mascota_id)
    if not masc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )
    return masc
