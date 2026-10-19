import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as task_app


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.tasks_file = Path(self.temp_directory.name) / "tasks.json"
        self.tasks_file_patch = patch.object(task_app, "TASKS_FILE", self.tasks_file)
        self.tasks_file_patch.start()
        task_app.app.config.update(TESTING=True)
        self.client = task_app.app.test_client()

    def tearDown(self):
        self.tasks_file_patch.stop()
        self.temp_directory.cleanup()

    @staticmethod
    def task_data(title="Estudiar Flask"):
        return {
            "title": title,
            "description": "Practicar las rutas de la API",
            "due_date": "2026-10-15",
        }

    def test_get_starts_with_empty_list(self):
        response = self.client.get("/tasks")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_post_creates_and_persists_task(self):
        response = self.client.post("/tasks", json=self.task_data())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 1)
        persisted_tasks = json.loads(self.tasks_file.read_text(encoding="utf-8"))
        self.assertEqual(persisted_tasks[0]["title"], "Estudiar Flask")

    def test_put_updates_existing_task(self):
        self.client.post("/tasks", json=self.task_data())
        updated_data = self.task_data("Dominar Flask")

        response = self.client.put("/tasks/1", json=updated_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["title"], "Dominar Flask")

    def test_delete_removes_existing_task(self):
        self.client.post("/tasks", json=self.task_data())

        response = self.client.delete("/tasks/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get("/tasks").get_json(), [])

    def test_delete_returns_404_for_unknown_task(self):
        response = self.client.delete("/tasks/99")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Tarea no encontrada."})

    def test_title_cannot_exceed_100_characters(self):
        response = self.client.post("/tasks", json=self.task_data("A" * 101))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "El título no puede superar 100 caracteres."},
        )


if __name__ == "__main__":
    unittest.main()
