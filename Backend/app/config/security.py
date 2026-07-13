# app/config/security.py
"""Utilidades de hashing de contraseñas (SC-046 / F31).

Se usa pbkdf2_sha256 (passlib): seguro y sin la dependencia externa de bcrypt,
que con passlib 1.7.4 falla al leer su versión en este entorno.

La verificación es RETROCOMPATIBLE: si el valor almacenado no es un hash
(contraseña en texto plano legada), se compara en claro para no bloquear cuentas
creadas antes del hashing. La capa de autenticación re-hashea la contraseña al
primer login exitoso (migración perezosa), de modo que el texto plano desaparece
progresivamente sin intervención.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Devuelve el hash pbkdf2_sha256 de la contraseña."""
    return pwd_context.hash(password)


def is_hashed(stored: str) -> bool:
    """True si el valor almacenado ya es un hash pbkdf2_sha256."""
    return bool(stored) and stored.startswith("$pbkdf2-sha256$")


def verify_password(plain: str, stored: str) -> bool:
    """Verifica la contraseña contra el valor almacenado (hash o texto plano)."""
    if is_hashed(stored):
        try:
            return pwd_context.verify(plain, stored)
        except Exception:
            return False
    return plain == stored
