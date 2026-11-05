"""Fixtures compartidas de pytest con aislamiento riguroso en bases de datos temporales."""
from collections.abc import Generator
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.infrastructure.config import Settings
from app.main import create_app


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Ruta a un archivo SQLite efímero y aislado por cada prueba."""
    return tmp_path / "test_aislado.db"


@pytest.fixture
def settings(db_path: Path) -> Settings:
    """Configuración de prueba que nunca toca la base de datos de desarrollo."""
    return Settings(
        _env_file=None,
        database_url=f"sqlite:///{db_path.as_posix()}",
        jwt_secret="secreto_seguro_para_pruebas_unitarias_de_64_caracteres_minimo_abc123",
        token_minutes=5,
        cors_origins=["http://localhost:5173"],
    )


@pytest.fixture
def client(settings: Settings) -> Generator[TestClient, None, None]:
    """TestClient ejecutado como context manager para activar el lifespan (create_all y dispose)."""
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client
