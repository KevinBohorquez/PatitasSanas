import pytest
from sqlalchemy.sql.elements import TextClause

from main import get_cors_origins
from app.api.v1.endpoints.system import health_check


def test_get_cors_origins_usa_variable_entorno(monkeypatch):
    monkeypatch.setenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:5173, https://frontend.vercel.app ,",
    )

    assert get_cors_origins() == [
        "http://localhost:5173",
        "https://frontend.vercel.app",
    ]


def test_get_cors_origins_tiene_valores_por_defecto(monkeypatch):
    monkeypatch.delenv("BACKEND_CORS_ORIGINS", raising=False)

    assert get_cors_origins() == [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://colitasfelices.netlify.app",
        "https://patitas-sanas-sigma.vercel.app",
    ]


class FakeDbSession:
    def __init__(self):
        self.statement = None

    def execute(self, statement):
        self.statement = statement


@pytest.mark.asyncio
async def test_health_check_usa_text_clause_para_sqlalchemy_2():
    db = FakeDbSession()

    response = await health_check(db=db)

    assert response["database"] == "✅ Conectada"
    assert isinstance(db.statement, TextClause)
