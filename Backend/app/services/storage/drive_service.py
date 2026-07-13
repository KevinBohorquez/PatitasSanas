# app/services/storage/drive_service.py
"""
Subida de archivos adjuntos a Google Drive (SC-020 / F27).

Configuración por variables de entorno (NO se versiona ninguna credencial):
- GOOGLE_SERVICE_ACCOUNT_JSON: contenido JSON de la clave de una cuenta de
  servicio de Google Cloud con la Drive API habilitada.
- GDRIVE_FOLDER_ID (opcional): ID de la carpeta de Drive donde guardar los
  archivos (debe estar compartida con el email de la cuenta de servicio).

Los imports de Google son PEREZOSOS: este módulo carga aunque la librería no
esté instalada; sólo se requieren `google-api-python-client` y `google-auth`
en el momento de subir un archivo.
"""
import io
import json
import os

_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def esta_configurado() -> bool:
    """True si hay credenciales de cuenta de servicio configuradas."""
    return bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))


def _get_service():
    """Construye el cliente de Drive desde GOOGLE_SERVICE_ACCOUNT_JSON."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
    creds = service_account.Credentials.from_service_account_info(info, scopes=_SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def subir_archivo(contenido: bytes, nombre: str, mimetype: str = None) -> str:
    """
    Sube `contenido` a Google Drive con el nombre dado y devuelve un enlace
    visible (webViewLink).

    Lanza RuntimeError si Drive no está configurado o si falta la librería;
    propaga otras excepciones de la API de Drive.
    """
    if not esta_configurado():
        raise RuntimeError(
            "Google Drive no está configurado (falta la variable de entorno "
            "GOOGLE_SERVICE_ACCOUNT_JSON)."
        )
    try:
        service = _get_service()
    except ImportError as e:
        raise RuntimeError(
            "Faltan dependencias de Google Drive: instala "
            "'google-api-python-client' y 'google-auth'."
        ) from e

    from googleapiclient.http import MediaIoBaseUpload

    metadata = {"name": nombre or "adjunto"}
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaIoBaseUpload(
        io.BytesIO(contenido),
        mimetype=mimetype or "application/octet-stream",
        resumable=False,
    )
    archivo = (
        service.files()
        .create(body=metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )

    file_id = archivo["id"]
    # Permiso de lectura para cualquiera con el enlace (para verlo/descargarlo).
    try:
        service.permissions().create(
            fileId=file_id, body={"type": "anyone", "role": "reader"}
        ).execute()
    except Exception:
        pass  # si falla el permiso, el enlace igual queda; el dueño puede ajustarlo

    return archivo.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
