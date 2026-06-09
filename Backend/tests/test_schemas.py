"""
Tests unitarios para los schemas de validación Pydantic.
No requieren conexión a base de datos.
"""
import pytest
from pydantic import ValidationError

from app.schemas.mascota_schema import MascotaCreate, MascotaUpdate
from app.schemas.auth_schema import (
    LoginRequest,
    PasswordChangeRequest,
    PermissionCheckRequest,
    UserBlockRequest,
)


# ─── MascotaCreate ────────────────────────────────────────────────────────────

class TestMascotaCreate:

    def test_crea_mascota_valida(self):
        m = MascotaCreate(id_raza=1, nombre="Rocky", sexo="Macho")
        assert m.nombre == "Rocky"
        assert m.sexo == "Macho"
        assert m.esterilizado is False

    def test_sexo_invalido_lanza_error(self):
        with pytest.raises(ValidationError) as exc:
            MascotaCreate(id_raza=1, nombre="Luna", sexo="Otro")
        assert "Sexo debe ser Macho o Hembra" in str(exc.value)

    def test_edad_anios_fuera_de_rango(self):
        with pytest.raises(ValidationError):
            MascotaCreate(id_raza=1, nombre="Max", sexo="Macho", edad_anios=30)

    def test_edad_meses_fuera_de_rango(self):
        with pytest.raises(ValidationError):
            MascotaCreate(id_raza=1, nombre="Max", sexo="Macho", edad_meses=12)

    def test_color_muy_corto_lanza_error(self):
        with pytest.raises(ValidationError):
            MascotaCreate(id_raza=1, nombre="Max", sexo="Macho", color="A")

    def test_color_se_normaliza_a_title_case(self):
        m = MascotaCreate(id_raza=1, nombre="Max", sexo="Macho", color="  negro  ")
        assert m.color == "Negro"

    def test_campos_opcionales_son_none_por_defecto(self):
        m = MascotaCreate(id_raza=2, nombre="Michi", sexo="Hembra")
        assert m.color is None
        assert m.edad_anios is None
        assert m.imagen is None


class TestMascotaUpdate:

    def test_update_parcial_solo_nombre(self):
        m = MascotaUpdate(nombre="Toby")
        assert m.nombre == "Toby"
        assert m.sexo is None

    def test_update_sexo_invalido(self):
        with pytest.raises(ValidationError):
            MascotaUpdate(sexo="Indefinido")


# ─── LoginRequest ─────────────────────────────────────────────────────────────

class TestLoginRequest:

    def test_login_valido(self):
        req = LoginRequest(username="admin001", password="secret123")
        assert req.username == "admin001"

    def test_username_se_convierte_a_minusculas(self):
        req = LoginRequest(username="  ADMIN001  ", password="pass")
        assert req.username == "admin001"

    def test_username_muy_corto(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="ab", password="pass")

    def test_password_muy_corto(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="admin001", password="ab")


# ─── PasswordChangeRequest ────────────────────────────────────────────────────

class TestPasswordChangeRequest:

    def test_cambio_contrasena_valido(self):
        req = PasswordChangeRequest(
            user_id=1,
            current_password="old_pass",
            new_password="new_pass",
            confirm_password="new_pass",
        )
        assert req.user_id == 1

    def test_contrasenas_no_coinciden(self):
        with pytest.raises(ValidationError) as exc:
            PasswordChangeRequest(
                user_id=1,
                current_password="old",
                new_password="new_pass",
                confirm_password="otro_pass",
            )
        assert "no coinciden" in str(exc.value)


# ─── PermissionCheckRequest ───────────────────────────────────────────────────

class TestPermissionCheckRequest:

    @pytest.mark.parametrize("role", ["Administrador", "Veterinario", "Recepcionista"])
    def test_roles_validos(self, role):
        req = PermissionCheckRequest(user_type=role, permission="ver_dashboard")
        assert req.user_type == role

    def test_rol_invalido(self):
        with pytest.raises(ValidationError):
            PermissionCheckRequest(user_type="SuperAdmin", permission="todo")


# ─── UserBlockRequest ─────────────────────────────────────────────────────────

class TestUserBlockRequest:

    def test_bloqueo_valido(self):
        req = UserBlockRequest(user_id=5, minutes=60)
        assert req.minutes == 60

    def test_minutos_cero_invalido(self):
        with pytest.raises(ValidationError):
            UserBlockRequest(user_id=5, minutes=0)

    def test_mas_de_24_horas_invalido(self):
        with pytest.raises(ValidationError):
            UserBlockRequest(user_id=5, minutes=1500)

    def test_valor_por_defecto_30_minutos(self):
        req = UserBlockRequest(user_id=5)
        assert req.minutes == 30
