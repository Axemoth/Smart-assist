const API_BASE = window.location.origin;

// State management
let token = localStorage.getItem("jwt_auth_token") || null;
let currentFilter = "all";
let tasksList = [];
let activeSubtasks = [];
let activeSubtaskTaskId = null;

// DOM Elements
const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard-section");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginTabBtn = document.getElementById("login-tab-btn");
const registerTabBtn = document.getElementById("register-tab-btn");
const authMessage = document.getElementById("auth-message");
const userDisplayEmail = document.getElementById("user-display-email");

const taskForm = document.getElementById("task-form");
const editTaskId = document.getElementById("edit-task-id");
const taskTitle = document.getElementById("task-title");
const taskDesc = document.getElementById("task-desc");
const taskPriority = document.getElementById("task-priority");
const taskStatusSelect = document.getElementById("task-status");
const cancelEditBtn = document.getElementById("cancel-edit-btn");
const saveTaskBtn = document.getElementById("save-task-btn");
const formTitle = document.getElementById("form-title");

const aiParseForm = document.getElementById("ai-parse-form");
const aiPromptInput = document.getElementById("ai-prompt-input");
const aiParseSubmit = document.getElementById("ai-parse-submit");

const tasksContainer = document.getElementById("tasks-container");

// Modal Elements
const subtaskModal = document.getElementById("subtask-modal");
const modalTaskTitle = document.getElementById("modal-task-title");
const modalTaskDesc = document.getElementById("modal-task-desc");
const modalSubtasksContainer = document.getElementById("modal-subtasks-container");

// Initialize app
function init() {
    if (token) {
        showDashboard();
    } else {
        showAuth();
    }
}

// Switching UI views
function showAuth() {
    authSection.classList.remove("hidden");
    dashboardSection.classList.add("hidden");
    clearAuthFields();
}

function showDashboard() {
    authSection.classList.add("hidden");
    dashboardSection.classList.remove("hidden");
    
    // Simple email extraction from JWT (claims payload) for display
    try {
        const payloadBase64 = token.split(".")[1];
        // Replace chars for URL safe decoding
        const decodedPayload = JSON.parse(atob(payloadBase64.replace(/-/g, '+').replace(/_/g, '/')));
        userDisplayEmail.innerHTML = `<i class="fa-solid fa-user-astronaut"></i> User ID: ${decodedPayload.user_id} (${decodedPayload.role})`;
    } catch (e) {
        userDisplayEmail.innerHTML = `<i class="fa-solid fa-user-astronaut"></i> Active Member`;
    }

    loadTasks();
}

function switchAuthTab(tab) {
    if (tab === "login") {
        loginForm.classList.add("active");
        registerForm.classList.remove("active");
        loginTabBtn.classList.add("active");
        registerTabBtn.classList.remove("active");
    } else {
        loginForm.classList.remove("active");
        registerForm.classList.add("active");
        loginTabBtn.classList.remove("active");
        registerTabBtn.classList.add("active");
    }
    hideAlert();
}

function showAlert(text, isError = true) {
    authMessage.textContent = text;
    authMessage.className = `alert-message ${isError ? 'error' : 'success'}`;
    authMessage.classList.remove("hidden");
}

function hideAlert() {
    authMessage.classList.add("hidden");
}

function clearAuthFields() {
    loginForm.reset();
    registerForm.reset();
}

// Authentication Logic
async function handleLogin(e) {
    e.preventDefault();
    hideAlert();

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    // OAuth2PasswordRequestForm expects URLSearchParams (form data)
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            token = data.access_token;
            localStorage.setItem("jwt_auth_token", token);
            showDashboard();
        } else {
            showAlert(data.detail || "Authentication failed. Make sure your account is verified.");
        }
    } catch (error) {
        showAlert("Failed to connect to authentication server.");
    }
}

async function handleRegister(e) {
    e.preventDefault();
    hideAlert();

    const name = document.getElementById("register-name").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const role = "user";

    try {
        const res = await fetch(`${API_BASE}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, email, password, role })
        });

        const data = await res.json();

        if (res.ok) {
            showAlert("Account created successfully! For testing, your account has been automatically auto-activated or check logs.", false);
            switchAuthTab("login");
        } else {
            showAlert(data.detail || "Registration failed.");
        }
    } catch (error) {
        showAlert("Failed to connect to registration server.");
    }
}

function handleLogout() {
    localStorage.removeItem("jwt_auth_token");
    token = null;
    showAuth();
}

// Tasks Core CRUD API Callers
async function loadTasks() {
    tasksContainer.innerHTML = `
        <div class="loading-state">
            <i class="fa-solid fa-spinner fa-spin"></i> Loading tasks...
        </div>
    `;

    try {
        const res = await fetch(`${API_BASE}/tasks`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.status === 401) {
            handleLogout();
            return;
        }

        const data = await res.json();
        if (res.ok) {
            tasksList = data;
            renderTasks();
        } else {
            tasksContainer.innerHTML = `<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i> Error loading tasks: ${data.detail || 'unknown error'}</div>`;
        }
    } catch (error) {
        tasksContainer.innerHTML = `<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i> Network error loading tasks.</div>`;
    }
}

function renderTasks() {
    let filteredTasks = tasksList;
    if (currentFilter === "pending") {
        filteredTasks = tasksList.filter(t => t.status === "pending");
    } else if (currentFilter === "completed") {
        filteredTasks = tasksList.filter(t => t.status === "completed");
    }

    if (filteredTasks.length === 0) {
        tasksContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-calendar-xmark"></i>
                <p>No tasks found in this category.</p>
            </div>
        `;
        return;
    }

    // Sort: High priority first, then medium, then low
    const priorityWeights = { high: 3, medium: 2, low: 1 };
    filteredTasks.sort((a, b) => {
        // Pending first
        if (a.status === "pending" && b.status === "completed") return -1;
        if (a.status === "completed" && b.status === "pending") return 1;
        // Then by priority weight
        return priorityWeights[b.priority] - priorityWeights[a.priority];
    });

    tasksContainer.innerHTML = filteredTasks.map(task => `
        <div class="task-item ${task.status === 'completed' ? 'completed' : ''}" id="task-${task.task_id}">
            <div class="task-main">
                <div class="checkbox-container">
                    <input type="checkbox" class="task-checkbox" 
                           ${task.status === 'completed' ? 'checked' : ''} 
                           onclick="toggleTaskStatus(${task.task_id}, '${task.status}')">
                </div>
                <div class="task-content">
                    <div class="task-title-row">
                        <span class="task-title">${escapeHtml(task.title)}</span>
                        <span class="priority-tag ${task.priority}">${task.priority}</span>
                    </div>
                    <p class="task-description">${escapeHtml(task.description || "No details provided.")}</p>
                </div>
            </div>
            <div class="task-actions">
                <button class="action-btn edit-btn" onclick="startEditTask(${task.task_id})">
                    <i class="fa-solid fa-pen-to-square"></i> Edit
                </button>
                <button class="action-btn rewrite-ai-btn" id="rewrite-btn-${task.task_id}" onclick="handleAIRewrite(${task.task_id})">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> AI Rewrite
                </button>
                <button class="action-btn breakdown-ai-btn" id="breakdown-btn-${task.task_id}" onclick="handleAIBreakdown(${task.task_id})">
                    <i class="fa-solid fa-network-wired"></i> Breakdown Checklist
                </button>
                <button class="action-btn delete-btn" onclick="handleDeleteTask(${task.task_id})">
                    <i class="fa-solid fa-trash-can"></i> Delete
                </button>
            </div>
        </div>
    `).join("");
}

function setFilter(filter) {
    currentFilter = filter;
    document.querySelectorAll(".filter-btn").forEach(btn => btn.classList.remove("active"));
    document.getElementById(`filter-${filter}`).classList.add("active");
    renderTasks();
}

async function handleSaveTask(e) {
    e.preventDefault();

    const id = editTaskId.value;
    const title = taskTitle.value;
    const description = taskDesc.value;
    const priority = taskPriority.value;
    const status = taskStatusSelect.value;

    const payload = { title, description, priority };
    const method = id ? "PUT" : "POST";
    const url = id ? `${API_BASE}/tasks/${id}` : `${API_BASE}/tasks`;

    if (id) {
        // Include status if we are updating
        payload.status = status;
    }

    try {
        const res = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            resetTaskForm();
            loadTasks();
        } else {
            const data = await res.json();
            alert(data.detail || "Error saving task.");
        }
    } catch (error) {
        alert("Failed to save task. Check server logs.");
    }
}

async function toggleTaskStatus(id, currentStatus) {
    const task = tasksList.find(t => t.task_id === id);
    if (!task) return;

    const nextStatus = currentStatus === "pending" ? "completed" : "pending";
    const payload = {
        title: task.title,
        description: task.description,
        priority: task.priority,
        status: nextStatus
    };

    try {
        const res = await fetch(`${API_BASE}/tasks/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            loadTasks();
        }
    } catch (error) {
        console.error("Failed to toggle status:", error);
    }
}

function startEditTask(id) {
    const task = tasksList.find(t => t.task_id === id);
    if (!task) return;

    editTaskId.value = task.task_id;
    taskTitle.value = task.title;
    taskDesc.value = task.description;
    taskPriority.value = task.priority;
    taskStatusSelect.value = task.status;

    formTitle.textContent = "Edit Task";
    saveTaskBtn.textContent = "Save Changes";
    cancelEditBtn.classList.remove("hidden");
    
    // Scroll form into view
    taskTitle.focus();
}

function resetTaskForm() {
    taskForm.reset();
    editTaskId.value = "";
    formTitle.textContent = "Create New Task";
    saveTaskBtn.textContent = "Save Task";
    cancelEditBtn.classList.add("hidden");
}

async function handleDeleteTask(id) {
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
        const res = await fetch(`${API_BASE}/tasks/${id}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.ok) {
            loadTasks();
        } else {
            alert("Failed to delete task.");
        }
    } catch (error) {
        alert("Network error deleting task.");
    }
}

// DeepSeek AI Integrations
async function handleAIParse(e) {
    e.preventDefault();
    const prompt = aiPromptInput.value.trim();
    if (!prompt) return;

    setAILoadingState(aiParseSubmit, true, "Parsing...");

    try {
        const res = await fetch(`${API_BASE}/tasks/ai/parse`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ prompt })
        });

        const data = await res.json();

        if (res.ok) {
            // Populate form fields
            taskTitle.value = data.title;
            taskDesc.value = data.description;
            taskPriority.value = data.priority;
            
            aiPromptInput.value = ""; // clear prompter
            taskTitle.focus();
        } else {
            alert(data.detail || "AI parsing failed.");
        }
    } catch (error) {
        alert("Failed to connect to DeepSeek API endpoint.");
    } finally {
        setAILoadingState(aiParseSubmit, false, `<i class="fa-solid fa-brain"></i> Parse with DeepSeek`);
    }
}

async function handleAIRewrite(id) {
    const task = tasksList.find(t => t.task_id === id);
    if (!task) return;

    const btn = document.getElementById(`rewrite-btn-${id}`);
    setAILoadingState(btn, true, "Rewriting...");

    try {
        const res = await fetch(`${API_BASE}/tasks/ai/rewrite`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                title: task.title,
                description: task.description || ""
            })
        });

        const data = await res.json();

        if (res.ok) {
            // Update database automatically with rewritten values
            const updateRes = await fetch(`${API_BASE}/tasks/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    title: data.title,
                    description: data.description,
                    priority: data.priority,
                    status: task.status
                })
            });

            if (updateRes.ok) {
                loadTasks();
            } else {
                alert("Failed to save rewritten task.");
            }
        } else {
            alert(data.detail || "AI rewrite failed.");
        }
    } catch (error) {
        alert("Failed to connect to AI rewrite service.");
    } finally {
        setAILoadingState(btn, false, `<i class="fa-solid fa-wand-magic-sparkles"></i> AI Rewrite`);
    }
}

async function handleAIBreakdown(id) {
    const task = tasksList.find(t => t.task_id === id);
    if (!task) return;

    const btn = document.getElementById(`breakdown-btn-${id}`);
    setAILoadingState(btn, true, "Breaking down...");

    try {
        const res = await fetch(`${API_BASE}/tasks/ai/breakdown`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                title: task.title,
                description: task.description || ""
            })
        });

        const data = await res.json();

        if (res.ok) {
            activeSubtasks = data.subtasks;
            activeSubtaskTaskId = id;
            
            // Open modal
            modalTaskTitle.textContent = task.title;
            modalTaskDesc.textContent = task.description || "No description provided.";
            modalSubtasksContainer.innerHTML = activeSubtasks.map(subtask => `
                <div class="modal-subtask-item">
                    <i class="fa-solid fa-circle-arrow-right"></i>
                    <span>${escapeHtml(subtask)}</span>
                </div>
            `).join("");
            
            subtaskModal.classList.remove("hidden");
        } else {
            alert(data.detail || "Failed to breakdown task.");
        }
    } catch (error) {
        alert("Failed to connect to task breakdown service.");
    } finally {
        setAILoadingState(btn, false, `<i class="fa-solid fa-network-wired"></i> Breakdown Checklist`);
    }
}

async function addSubtasksToDescription() {
    if (!activeSubtaskTaskId || activeSubtasks.length === 0) return;
    
    const task = tasksList.find(t => t.task_id === activeSubtaskTaskId);
    if (!task) return;

    const subtasksText = "\n\n📋 AI Breakdown:\n" + activeSubtasks.map(s => `- [ ] ${s}`).join("\n");
    const newDescription = (task.description || "") + subtasksText;

    try {
        const res = await fetch(`${API_BASE}/tasks/${activeSubtaskTaskId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                title: task.title,
                description: newDescription,
                priority: task.priority,
                status: task.status
            })
        });

        if (res.ok) {
            closeSubtaskModal();
            loadTasks();
        } else {
            alert("Failed to append subtasks to description.");
        }
    } catch (error) {
        alert("Network error saving subtasks.");
    }
}

function closeSubtaskModal() {
    subtaskModal.classList.add("hidden");
    activeSubtaskTaskId = null;
    activeSubtasks = [];
}

// Helpers
function setAILoadingState(button, isLoading, text) {
    button.disabled = isLoading;
    button.innerHTML = text;
}

function escapeHtml(unsafe) {
    if (!unsafe) return "";
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Run init on load
init();
