# SC-046 / F31: hashea (pbkdf2_sha256) las contraseñas que aún estén en texto
# plano en la tabla usuarios. Idempotente: salta las que ya son hash.
#
# Ejecutar UNA vez por entorno, desde Backend/ con el venv activo:
#   python migrations/008_hash_passwords.py
#
# Nota: aunque no se ejecute, la verificación de login es retrocompatible y
# re-hashea cada contraseña en su primer login exitoso (migración perezosa).
# Este script hace la migración completa de golpe.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal
from app.config.security import hash_password, is_hashed
from app.models.usuario import Usuario


def run():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        migrados = 0
        for u in usuarios:
            if not is_hashed(u.contraseña):
                u.contraseña = hash_password(u.contraseña)
                migrados += 1
        db.commit()
        print(f"Contraseñas hasheadas: {migrados} de {len(usuarios)} usuarios")
    finally:
        db.close()


if __name__ == "__main__":
    run()
