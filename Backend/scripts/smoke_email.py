"""
Script de prueba para verificar el envío de correos (SMTP).

Uso:
    python scripts/smoke_email.py destino@ejemplo.com

Requisitos:
    - Backend/.env con SMTP_USER, SMTP_PASSWORD y SMTP_FROM configurados
      (SMTP_PASSWORD debe ser una "contraseña de aplicación" de Gmail).
"""
import sys
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Carga variables desde Backend/.env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    print("⚠️  python-dotenv no instalado. Instálalo con: pip install python-dotenv")
    print("    (o exporta las variables SMTP_* manualmente antes de correr esto)")

from app.services.notifications.email_service import send_reminder_email


def main():
    destino = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SMTP_USER")
    if not destino:
        print("❌ Indica un correo destino: python scripts/smoke_email.py tucorreo@gmail.com")
        sys.exit(1)

    sender = (os.getenv('BREVO_SENDER_EMAIL') or os.getenv('SMTP_FROM')
              or os.getenv('SMTP_USER') or '(vacío)')
    print(f"→ Enviando correo de prueba a: {destino}")
    print(f"  Proveedor=Brevo  API_KEY={'configurada' if os.getenv('BREVO_API_KEY') else '(vacía)'}  "
          f"Remitente={sender}")

    ok = send_reminder_email(
        to_email=destino,
        cliente_nombre="Cliente de Prueba",
        mascota_nombre="Firulais",
        fecha_hora=datetime.now() + timedelta(hours=24),
        horas_antes=24,
        veterinario_nombre="Dra. Prueba",
        servicio_nombre="Consulta general",
    )

    if ok:
        print("✅ Correo enviado correctamente. Revisa la bandeja (y spam) de", destino)
    else:
        print("❌ No se pudo enviar. Revisa los logs de arriba (credenciales / conexión).")
        sys.exit(1)


if __name__ == "__main__":
    main()
