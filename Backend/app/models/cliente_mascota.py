# app/models/cliente_mascota.py
from sqlalchemy import Column, Integer, ForeignKey
from app.models.base import Base

class ClienteMascota(Base):
    __tablename__ = "Cliente_Mascota"

    id_cliente_mascota = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey('Cliente.id_cliente'))
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))