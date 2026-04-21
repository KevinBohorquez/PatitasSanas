# app/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexión (usar sakila o railway según prefieras)
DATABASE_URL = os.getenv("DATABASE_URL")

# --- CORRECCIÓN CRÍTICA ---
# Verificamos si la URL empieza con mysql:// y la cambiamos a mysql+pymysql://
# Esto evita el error de "No module named 'MySQLdb'" asegurando que se use el driver correcto.
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Ver queries SQL en logs
    pool_pre_ping=True,  # Verificar conexión
    pool_recycle=300  # Reciclar conexiones cada 5 min
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency para obtener sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()