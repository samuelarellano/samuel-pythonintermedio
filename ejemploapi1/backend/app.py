from datetime import date
import json
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
TASKS_FILE = Path(__file__).with_name("tasks.json")
REQUIRED_FIELDS = {"title", "description", "due_date"}
MAX_TITLE_LENGTH = 100


def read_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        return []

    with TASKS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_tasks(tasks: list[dict]) -> None:
    with TASKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)


def validate_task_data(data: object) -> tuple[dict | None, str | None]:
    if not isinstance(data, dict):
        return None, "El cuerpo debe ser un objeto JSON."

    missing_fields = REQUIRED_FIELDS - data.keys()
    if missing_fields:
        return None, f"Faltan campos: {', '.join(sorted(missing_fields))}."

    title = data["title"]
    description = data["description"]
    due_date = data["due_date"]

    if not isinstance(title, str) or not title.strip():
        return None, "El título es obligatorio."
    if len(title.strip()) > MAX_TITLE_LENGTH:
        return None, f"El título no puede superar {MAX_TITLE_LENGTH} caracteres."
    if not isinstance(description, str):
        return None, "La descripción debe ser texto."
    if due_date is not None:
        try:
            date.fromisoformat(due_date)
        except (TypeError, ValueError):
            return None, "La fecha debe usar el formato AAAA-MM-DD."

    return {
        "title": title.strip(),
        "description": description.strip(),
        "due_date": due_date,
    }, None


@app.get("/tasks")
def list_tasks():
    return jsonify(read_tasks())


@app.post("/tasks")
def create_task():
    task_data, error = validate_task_data(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    tasks = read_tasks()
    task = {"id": max((item["id"] for item in tasks), default=0) + 1, **task_data}
    tasks.append(task)
    write_tasks(tasks)
    return jsonify(task), 201


@app.put("/tasks/<int:task_id>")
def update_task(task_id: int):
    task_data, error = validate_task_data(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    tasks = read_tasks()
    for position, task in enumerate(tasks):
        if task["id"] == task_id:
            updated_task = {"id": task_id, **task_data}
            tasks[position] = updated_task
            write_tasks(tasks)
            return jsonify(updated_task)

    return jsonify({"error": "Tarea no encontrada."}), 404


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    tasks = read_tasks()
    remaining_tasks = [task for task in tasks if task["id"] != task_id]

    if len(remaining_tasks) == len(tasks):
        return jsonify({"error": "Tarea no encontrada."}), 404

    write_tasks(remaining_tasks)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
