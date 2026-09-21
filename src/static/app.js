"use strict";

// Die Demo speichert ausschließlich in diesem Browser. Kein Konto nötig.
const STORAGE_KEY = "stadtwerk.tasks.v1";
const CATEGORIES = ["Service", "Strom", "Wasser", "Wärme"];
const EXAMPLES = [
  { id: "demo-1", title: "Zählerstand in der Lindenstraße prüfen", category: "Strom", done: false },
  { id: "demo-2", title: "Rückruf zur Wasserabrechnung erledigen", category: "Wasser", done: false },
  { id: "demo-3", title: "Unterlagen zum Fernwärmeanschluss versenden", category: "Wärme", done: false },
  { id: "demo-4", title: "Umzug für die Musterstraße erfassen", category: "Service", done: false },
  { id: "demo-5", title: "Abschlag für die Gartenstraße anpassen", category: "Strom", done: true },
  { id: "demo-6", title: "Termin für den Zählerwechsel bestätigen", category: "Wasser", done: true },
];

const $ = (selector) => document.querySelector(selector);
const list = $("#task-list");
const dialog = $("#task-dialog");
const form = $("#task-form");
const titleInput = $("#task-title");
let tasks = loadTasks();
let filter = "open";
let editingId = null;
let undoState = null;
let returnFocus = null;

function warnStorage(message) {
  $("#storage-warning").textContent = message;
  $("#storage-warning").hidden = false;
  $(".storage-note").hidden = true;
}

function loadTasks() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved !== null) {
      const data = JSON.parse(saved);
      if (!Array.isArray(data) || !data.every((task) =>
        task && typeof task.id === "string" && task.id.length > 0 &&
        typeof task.title === "string" && task.title.trim().length > 0 && task.title.length <= 120 &&
        CATEGORIES.includes(task.category) && typeof task.done === "boolean"
      ) || new Set(data.map((task) => task.id)).size !== data.length) {
        throw new Error("Ungültige gespeicherte Aufgaben");
      }
      return data;
    }
  } catch {
    warnStorage("Gespeicherte Aufgaben sind nicht verfügbar. Du startest mit den Beispieltickets.");
  }
  return EXAMPLES.map((task) => ({ ...task }));
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    $("#storage-warning").hidden = true;
    $(".storage-note").hidden = false;
  } catch {
    warnStorage("Dein Browser kann die Aufgaben gerade nicht speichern. Änderungen bleiben nur bis zum Neuladen erhalten.");
  }
}

function icon(name) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  svg.setAttribute("aria-hidden", "true");
  use.setAttribute("href", `#i-${name}`);
  svg.append(use);
  return svg;
}

function render() {
  const done = tasks.filter((task) => task.done).length;
  const visible = tasks.filter((task) => filter === "all" || task.done === (filter === "done"));
  $("#count-open").textContent = tasks.length - done;
  $("#count-done").textContent = done;
  $("#count-all").textContent = tasks.length;
  $("#progress-label").textContent = `${done} von ${tasks.length} erledigt`;
  $("#progress-message").textContent = tasks.length && done === tasks.length ? "Gut gemacht. Alles geschafft!" : "Jeder Schritt zählt.";
  $("#progress").max = tasks.length || 1;
  $("#progress").value = done;
  document.querySelectorAll(".filter").forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === filter);
    button.setAttribute("aria-pressed", String(button.dataset.filter === filter));
  });
  list.setAttribute("aria-label", { open: "Offene Aufgaben", done: "Erledigte Aufgaben", all: "Alle Aufgaben" }[filter]);
  list.replaceChildren();

  visible.forEach((task) => {
    const row = document.createElement("li");
    row.className = `task${task.done ? " done" : ""}`;
    row.dataset.id = task.id;
    const checkLabel = document.createElement("label");
    checkLabel.className = "check-label";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "task-check";
    checkbox.checked = task.done;
    checkbox.setAttribute("aria-label", `${task.title}: ${task.done ? "wieder öffnen" : "erledigen"}`);
    checkbox.addEventListener("change", () => {
      const index = visible.findIndex((item) => item.id === task.id);
      change(() => { task.done = checkbox.checked; }, task.done ? "Aufgabe wieder geöffnet." : "Aufgabe erledigt.");
      const next = list.querySelectorAll(".task-check");
      (next[Math.min(index, next.length - 1)] || $("#empty-add")).focus();
    });
    checkLabel.append(checkbox, icon("check"));
    const title = document.createElement("p");
    title.className = "task-title";
    title.textContent = task.title;
    const category = document.createElement("span");
    category.className = "category";
    category.dataset.category = task.category;
    category.textContent = task.category;
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "icon-button";
    edit.setAttribute("aria-label", `Bearbeiten: ${task.title}`);
    edit.title = "Aufgabe bearbeiten";
    edit.append(icon("edit"));
    edit.addEventListener("click", () => openEditor(task));
    row.append(checkLabel, title, category, edit);
    list.append(row);
  });

  $("#empty-state").hidden = visible.length > 0;
  $("#quick-add").hidden = visible.length === 0;
  const empty = tasks.length === 0
    ? ["Platz für deinen nächsten Schritt.", "Lege deine erste Aufgabe an. Ganz einfach."]
    : filter === "done"
      ? ["Der erste Haken wartet.", "Erledigte Aufgaben findest du hier."]
      : ["Alles erledigt.", "Gut gemacht. Zeit für einen kleinen Durchatmer."];
  $("#empty-title").textContent = empty[0];
  $("#empty-description").textContent = empty[1];
}

// Eine letzte Änderung lässt sich jederzeit rückgängig machen.
function change(mutate, message) {
  undoState = tasks.map((task) => ({ ...task }));
  mutate();
  persist();
  render();
  $("#toast").hidden = false;
  $("#toast-message").textContent = message;
  $("#undo").hidden = false;
}

function openEditor(task = null) {
  returnFocus = document.activeElement;
  editingId = task?.id ?? null;
  form.reset();
  titleInput.setCustomValidity("");
  titleInput.value = task?.title ?? "";
  $("#task-category").value = task?.category ?? "Service";
  $("#dialog-title").textContent = task ? "Aufgabe bearbeiten" : "Neue Aufgabe";
  $("#save-task").textContent = task ? "Speichern" : "Aufgabe anlegen";
  $("#delete-task").hidden = !task;
  dialog.showModal();
  titleInput.focus();
}

function closeEditor() {
  dialog.close();
}

dialog.addEventListener("close", () => {
  (returnFocus?.isConnected && !returnFocus.hidden ? returnFocus : $("#new-task")).focus();
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) {
    titleInput.setCustomValidity("Gib deiner Aufgabe bitte einen Titel.");
    titleInput.reportValidity();
    return;
  }
  const category = $("#task-category").value;
  const task = tasks.find((item) => item.id === editingId);
  change(() => {
    if (task) {
      Object.assign(task, { title, category });
    } else {
      tasks.unshift({ id: crypto.randomUUID(), title, category, done: false });
      if (filter === "done") filter = "open";
    }
  }, task ? "Aufgabe gespeichert." : "Aufgabe angelegt.");
  closeEditor();
});

titleInput.addEventListener("input", () => titleInput.setCustomValidity(""));
$("#delete-task").addEventListener("click", () => {
  change(() => { tasks = tasks.filter((task) => task.id !== editingId); }, "Aufgabe gelöscht.");
  closeEditor();
});
$("#undo").addEventListener("click", () => {
  if (!undoState) return;
  tasks = undoState;
  undoState = null;
  persist();
  render();
  $("#toast-message").textContent = "Änderung rückgängig gemacht.";
  $("#undo").hidden = true;
  $("#dismiss-toast").focus();
});
$("#dismiss-toast").addEventListener("click", () => {
  $("#toast").hidden = true;
  $("#new-task").focus();
});
document.querySelectorAll(".filter").forEach((button) => {
  button.addEventListener("click", () => { filter = button.dataset.filter; render(); });
});
["#new-task", "#quick-add", "#empty-add"].forEach((selector) => $(selector).addEventListener("click", () => openEditor()));
["#close-dialog", "#cancel-dialog"].forEach((selector) => $(selector).addEventListener("click", closeEditor));

$("#today").textContent = new Intl.DateTimeFormat("de-DE", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
render();
