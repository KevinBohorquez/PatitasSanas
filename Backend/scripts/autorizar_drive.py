"""Autorización única de Google Drive (OAuth) para subir imágenes a TU Drive personal.

Requisitos previos:
  1. En Google Cloud Console (mismo proyecto), crea una credencial:
     Credenciales -> Crear credenciales -> ID de cliente de OAuth -> Aplicación de escritorio.
     Descarga el JSON y guárdalo como:  Backend/credentials/oauth_client.json
  2. En "Pantalla de consentimiento de OAuth", agrégate como usuario de prueba (tu correo).

Uso (desde Backend/, con el venv activo):
    python scripts/autorizar_drive.py

Abre el navegador, inicia sesión con TU cuenta y autoriza. Al terminar guarda el
token en Backend/credentials/drive_oauth_token.json (gitignored), que el backend usa
para subir imágenes a tu Drive.
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_FILE = os.path.join(BACKEND_DIR, 'credentials', 'oauth_client.json')
TOKEN_FILE = os.path.join(BACKEND_DIR, 'credentials', 'drive_oauth_token.json')


def main():
    if not os.path.exists(CLIENT_FILE):
        raise SystemExit(
            f"Falta el archivo del cliente OAuth: {CLIENT_FILE}\n"
            "Descárgalo de Google Cloud Console (ID de cliente de OAuth -> Aplicación de escritorio)."
        )
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        f.write(creds.to_json())
    print("Autorización completada. Token guardado en:", TOKEN_FILE)


if __name__ == '__main__':
    main()
