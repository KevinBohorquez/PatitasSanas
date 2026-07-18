"""Subida de imágenes a Google Drive con OAuth (Drive personal del usuario).

Los archivos quedan a nombre del usuario que autorizó (su cuota de 15 GB). El token
se genera una vez con scripts/autorizar_drive.py.

Credenciales del token: se leen de GOOGLE_DRIVE_OAUTH_TOKEN (contenido JSON, ideal para
producción/Railway) o del archivo credentials/drive_oauth_token.json (para local).
La carpeta destino se toma de GOOGLE_DRIVE_FOLDER_ID.
"""
import os
import io
import json
from functools import lru_cache

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
# .../Backend  (cuatro niveles arriba de este archivo)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_TOKEN_FILE = os.path.join(_BACKEND_DIR, 'credentials', 'drive_oauth_token.json')


def _credentials():
    raw = os.getenv('GOOGLE_DRIVE_OAUTH_TOKEN')
    if raw:
        creds = Credentials.from_authorized_user_info(json.loads(raw), SCOPES)
    else:
        if not os.path.exists(_TOKEN_FILE):
            raise RuntimeError(
                "No hay token de Drive. Ejecuta 'python scripts/autorizar_drive.py' para autorizar."
            )
        creds = Credentials.from_authorized_user_file(_TOKEN_FILE, SCOPES)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
    return creds


@lru_cache(maxsize=1)
def _service():
    return build('drive', 'v3', credentials=_credentials(), cache_discovery=False)


def subir_imagen(contenido: bytes, nombre: str, mimetype: str) -> str:
    """Sube el archivo a la carpeta configurada, lo hace visible por enlace y devuelve
    una URL de visualización directa de la imagen."""
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    if not folder_id:
        raise RuntimeError('GOOGLE_DRIVE_FOLDER_ID no está configurado')

    service = _service()
    media = MediaIoBaseUpload(io.BytesIO(contenido), mimetype=mimetype, resumable=False)
    archivo = service.files().create(
        body={'name': nombre, 'parents': [folder_id]},
        media_body=media,
        fields='id',
    ).execute()
    file_id = archivo['id']

    # Visible para cualquiera con el enlace (solo lectura).
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'},
    ).execute()

    return f'https://drive.google.com/uc?id={file_id}'
