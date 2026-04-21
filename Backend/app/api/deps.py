# app/api/deps.py
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.crud import cliente, veterinario, mascota
from app.models.clientes import Cliente
from app.models.veterinario import Veterinario
from app.models.mascota import Mascota

# ===== DEPENDENCIAS DE BASE DE DATOS =====
def get_database() -> Session:
    """Dependencia para obtener sesión de DB"""
    return Depends(get_db)

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

def get_veterinario_or_404(
    veterinario_id: int,
    db: Session = Depends(get_db)
) -> Veterinario:
    """Obtener veterinario o retornar 404"""
    vet = veterinario.get(db, veterinario_id)
    if not vet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )
    return vet

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

# ===== DEPENDENCIAS DE PAGINACIÓN =====
def validate_pagination(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
) -> dict:
    """Validar parámetros de paginación"""
    return {"page": page, "per_page": per_page}

# ===== DEPENDENCIAS DE VALIDACIÓN DE DUPLICADOS =====
def validate_cliente_unique(
    cliente_data,
    db: Session = Depends(get_db),
    exclude_id: Optional[int] = None
):
    """Validar que DNI y email del cliente sean únicos"""
    if cliente.exists_by_dni(db, dni=cliente_data.dni, exclude_id=exclude_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un cliente con ese DNI"
        )
    
    if cliente.exists_by_email(db, email=cliente_data.email, exclude_id=exclude_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un cliente con ese email"
        )
    
    return cliente_data

def validate_veterinario_unique(
    veterinario_data,
    db: Session = Depends(get_db),
    exclude_id: Optional[int] = None
):
    """Validar que DNI, email y código CMVP del veterinario sean únicos"""
    if veterinario.exists_by_dni(db, dni=veterinario_data.dni, exclude_id=exclude_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un veterinario con ese DNI"
        )
    
    if veterinario.exists_by_email(db, email=veterinario_data.email, exclude_id=exclude_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un veterinario con ese email"
        )
    
    if veterinario.exists_by_codigo_cmvp(db, codigo_cmvp=veterinario_data.codigo_CMVP, exclude_id=exclude_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un veterinario con ese código CMVP"
        )
    
    return veterinario_data

# ===== DEPENDENCIAS DE AUTENTICACIÓN SIMPLE =====
def authenticate_veterinario(
    email: str,
    password: str,
    db: Session = Depends(get_db)
) -> Veterinario:
    """Autenticar veterinario"""
    vet = veterinario.authenticate(db, email=email, password=password)
    if not vet:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    return vet


def get_recepcionista_or_404():
    return None