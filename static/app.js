async function loadTasks() {
    const res = await fetch("/tasks");
    const tasks = await res.json();

    const list = document.getElementById("taskList");
    list.innerHTML = "";

    tasks.forEach(t => {
        const li = document.createElement("li");
        li.textContent = t.content;
        if (t.completed) li.classList.add("done");

        li.onclick = async () => {
            await fetch(`/tasks/${t.id}`, { method: "PUT" });
            loadTasks();
        };

        const del = document.createElement("button");
        del.textContent = "X";
        del.onclick = async (e) => {
            e.stopPropagation();
            await fetch(`/tasks/${t.id}`, { method: "DELETE" });
            loadTasks();
        };

        li.appendChild(del);
        list.appendChild(li);
    });
}

async function addTask() {
    const input = document.getElementById("taskInput");
    if (!input.value) return;

    await fetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: input.value })
    });

    input.value = "";
    loadTasks();
}

loadTasks();
