import uvicorn
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))  # Railway inyecta PORT en producción

    uvicorn.run(
        "main:app",  # Ajusta si tu archivo y estructura es distinta
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )
