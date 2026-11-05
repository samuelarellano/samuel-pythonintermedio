"""Pruebas de liveness, aislamiento de base de datos y trazabilidad HTTP."""
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.infrastructure.config import Settings
from app.main import create_app


def test_salud_responde_ok_y_trazabilidad(client: TestClient):
    """Verifica que /salud responde 200, json correcto y cabeceras de trazabilidad."""
    respuesta = client.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}

    # Verificación del middleware de observabilidad
    assert "X-Request-ID" in respuesta.headers
    assert len(respuesta.headers["X-Request-ID"]) > 0
    assert "X-Process-Time" in respuesta.headers
    # El tiempo de procesamiento debe ser un número positivo en segundos
    tiempo = float(respuesta.headers["X-Process-Time"])
    assert tiempo >= 0.0


def test_aislamiento_base_de_datos_temporal(settings: Settings, db_path: Path):
    """Comprueba que la base de datos de pruebas está en tmp_path y NO toca la_estrellita.db."""
    dev_db = Path("la_estrellita.db")
    dev_db_existe_antes = dev_db.exists()

    app = create_app(settings)
    with TestClient(app) as test_client:
        respuesta = test_client.get("/salud")
        assert respuesta.status_code == 200

        # La conexión debe operar sobre el archivo efímero de tmp_path
        engine = app.state.engine
        assert engine.url.database is not None
        assert Path(engine.url.database).resolve() == db_path.resolve()

        # Comprobar que foreign keys están activas (PRAGMA foreign_keys = 1)
        with Session(engine) as session:
            resultado = session.exec(text("PRAGMA foreign_keys")).first()
            # En SQLite devuelve (1,) si está activado
            assert resultado is not None
            assert resultado[0] == 1

    # Si la base de desarrollo no existía antes, no debe haber sido creada por la prueba
    if not dev_db_existe_antes:
        assert not dev_db.exists(), "La prueba creó o tocó la_estrellita.db en la raíz"


def test_settings_rechaza_marcador_inseguro():
    """Comprueba que Settings rechaza el marcador de ejemplo REEMPLAZAR..."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret="REEMPLAZAR_CON_TOKEN_INSEGURO_DE_EJEMPLO_123")
