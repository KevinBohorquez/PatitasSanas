# main.py - Sistema Veterinaria API COMPLETO
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  # <--- [IMPORTANTE] Agregar esto
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import os
from datetime import datetime

from app.config.database import get_db
from app.models.clientes import Cliente

# ✅ IMPORTAR TODOS LOS ROUTERS
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.clientes import router as clientes_router
from app.api.v1.endpoints.veterinarios import router as veterinarios_router
from app.api.v1.endpoints.recepcionistas import router as recepcionistas_router
from app.api.v1.endpoints.mascota import router as mascotas_router
from app.api.v1.endpoints.usuarios import router as usuarios_router
from app.api.v1.endpoints.administradores import router as administradores_router
from app.api.v1.endpoints.catalogos import router as catalogos_router
from app.api.v1.endpoints.consultas import router as consultas_router
from app.api.v1.endpoints.solicitudes import router as solicitudes_router
from app.api.v1.endpoints.triaje import router as triaje_router
from app.api.v1.endpoints.servicio_solicitado import router as servicio_solicitado_router

app = FastAPI(
    title="🏥 Sistema Veterinaria API Completo",
    description="API integral para gestión de veterinaria con autenticación y todos los módulos",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*", 
        "http://localhost:5173",
        "http://localhost:3000",
        "https://colitasfelices.netlify.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ INCLUIR ROUTERS
app.include_router(auth_router, prefix="/api/v1/auth", tags=["🔐 autenticación"])
app.include_router(clientes_router, prefix="/api/v1/clientes", tags=["👥 clientes"])
app.include_router(veterinarios_router, prefix="/api/v1/veterinarios", tags=["👨‍⚕️ veterinarios"])
app.include_router(recepcionistas_router, prefix="/api/v1/recepcionistas", tags=["👩‍💼 recepcionistas"])
app.include_router(usuarios_router, prefix="/api/v1/usuarios", tags=["👤 usuarios"])
app.include_router(administradores_router, prefix="/api/v1/administradores", tags=["👑 administradores"])
app.include_router(mascotas_router, prefix="/api/v1/mascotas", tags=["🐕 mascotas"])
app.include_router(catalogos_router, prefix="/api/v1/catalogos", tags=["📋 catálogos"])
app.include_router(consultas_router, prefix="/api/v1/consultas", tags=["🏥 consultas"])
app.include_router(triaje_router, prefix="/api/v1/triaje", tags=["🏥 Triaje"])
app.include_router(servicio_solicitado_router, prefix="/api/v1/servicio_solicitado", tags=["🏥 Servicio_solicitado"])
app.include_router(solicitudes_router, prefix="/api/v1/solicitudes", tags=["🏥 Solicitudes"])

# ===== ENDPOINTS PRINCIPALES =====

# --- AGREGA ESTO AQUÍ ---
@app.get("/api/v1/")
async def v1_root():
    return {"message": "Bienvenido a la API v1", "docs": "/docs"}
# ------------------------

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "🏥 Sistema Veterinaria API COMPLETO funcionando!",
        "version": "2.0.0",
        "status": "✅ Operativo",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Endpoint de salud del sistema"""
    try:
        # Verificar conexión a la base de datos
        db.execute("SELECT 1")
        db_status = "✅ Conectada"
    except Exception as e:
        db_status = f"❌ Error: {str(e)}"
        
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.0.0"
    }

@app.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Estadísticas generales del sistema"""
    try:
        stats = {}
        # ... (Tu lógica de stats sigue igual aquí) ...
        # (Omitido para brevedad, mantener tu código original aquí)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_info": {"environment": os.getenv("ENVIRONMENT", "development")}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


# ===== MANEJO DE ERRORES GLOBALES (CORREGIDO) =====

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    """Manejo global de errores de base de datos"""
    # [CORRECCIÓN] Devolver JSONResponse en lugar de dict
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error de base de datos",
            "detail": "Ocurrió un problema con la base de datos",
            "status_code": 500
        }
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Manejo de rutas no encontradas"""
    # [CORRECCIÓN] Devolver JSONResponse en lugar de dict
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint no encontrado",
            "detail": f"La ruta {request.url.path} no existe",
            "available_endpoints": "/docs",
            "status_code": 404
        }
    )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"🚀 Iniciando servidor en http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug, log_level="info")