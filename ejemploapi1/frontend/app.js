const API_URL = "http://127.0.0.1:5000";
const form = document.querySelector("#task-form");
const tasksContainer = document.querySelector("#tasks");
const message = document.querySelector("#message");
const cancelButton = document.querySelector("#cancel-button");
let editingId = null;

function showMessage(text, isError = false) {
  message.textContent = text;
  message.className = isError ? "error" : "";
}

function renderTasks(tasks) {
  tasksContainer.innerHTML = "";
  if (tasks.length === 0) {
    tasksContainer.textContent = "Todavía no hay tareas.";
    return;
  }

  tasks.forEach((task) => {
    const article = document.createElement("article");
    article.className = "task";
    const title = document.createElement("h3");
    title.textContent = task.title;
    const description = document.createElement("p");
    description.textContent = task.description || "Sin descripción";
    const dueDate = document.createElement("p");
    dueDate.textContent = `Entrega: ${task.due_date || "Sin fecha"}`;
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "Editar tarea";
    editButton.addEventListener("click", () => startEditing(task));
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Eliminar tarea";
    deleteButton.addEventListener("click", () => deleteTask(task));
    article.append(title, description, dueDate, editButton, deleteButton);
    tasksContainer.appendChild(article);
  });
}

async function deleteTask(task) {
  const shouldDelete = window.confirm(`¿Eliminar la tarea "${task.title}"?`);
  if (!shouldDelete) {
    return;
  }

  const response = await fetch(`${API_URL}/tasks/${task.id}`, {method: "DELETE"});
  if (!response.ok) {
    const result = await response.json();
    showMessage(result.error || "No se pudo eliminar la tarea.", true);
    return;
  }

  if (editingId === task.id) {
    resetForm();
  }
  showMessage("Tarea eliminada.");
  await loadTasks();
}

async function loadTasks() {
  const response = await fetch(`${API_URL}/tasks`);
  if (!response.ok) {
    throw new Error("No se pudieron cargar las tareas.");
  }
  renderTasks(await response.json());
}

function startEditing(task) {
  editingId = task.id;
  form.title.value = task.title;
  form.description.value = task.description;
  form.due_date.value = task.due_date || "";
  document.querySelector("#form-title").textContent = "Editar tarea";
  form.querySelector("button[type=submit]").textContent = "Actualizar tarea";
  cancelButton.hidden = false;
  form.title.focus();
}

function resetForm() {
  editingId = null;
  form.reset();
  document.querySelector("#form-title").textContent = "Crear tarea";
  form.querySelector("button[type=submit]").textContent = "Guardar tarea";
  cancelButton.hidden = true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const task = {
    title: form.title.value,
    description: form.description.value,
    due_date: form.due_date.value || null,
  };
  const url = editingId === null ? `${API_URL}/tasks` : `${API_URL}/tasks/${editingId}`;
  const method = editingId === null ? "POST" : "PUT";
  const response = await fetch(url, {
    method,
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(task),
  });
  if (!response.ok) {
    const result = await response.json();
    showMessage(result.error || "Revisa los datos de la tarea.", true);
    return;
  }
  resetForm();
  showMessage("Tarea guardada.");
  await loadTasks();
});

cancelButton.addEventListener("click", resetForm);
loadTasks().catch((error) => showMessage(error.message, true));
