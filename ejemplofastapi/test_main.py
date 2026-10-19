"""Pruebas de la aplicación FastAPI."""

import unittest

from fastapi.testclient import TestClient

from main import app


class MainApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_listar_actividades_favoritas(self):
        response = self.client.get("/lovers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"id": 1, "titulo": "Escuchar audiolibros"},
                {"id": 2, "titulo": "Aprender programación en Python"},
                {
                    "id": 3,
                    "titulo": "Salir a caminar y conocer lugares nuevos",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
