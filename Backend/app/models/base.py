# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base

# Base común para todos los modelos
Base = declarative_base()

# Aquí puedes agregar métodos comunes para todos los modelos si necesitas
class BaseModel:
    """Clase base con métodos comunes (opcional)"""
    pass