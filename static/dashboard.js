

"use strict";

// ======================================
// API HELPER
// ======================================

async function api(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...options.headers
        }
    });

    let data = {};

    try {
        data = await response.json();
    } catch {
        throw new Error("Invalid server response.");
    }

    if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
    }

    return data;
}


// ======================================
// HTML ESCAPING
// ======================================

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}


// ======================================
// MESSAGE DISPLAY
// ======================================

function showMessage(elementId, message, type = "success") {
    const element = document.getElementById(elementId);

    if (!element) return;

    element.textContent = message;
    element.className = `message ${type}`;
}


// ======================================
// STUDENT MANAGEMENT
// ======================================

async function loadStudents() {
    const table = document.getElementById("studentTable");

    if (!table) return;

    try {
        const students = await api("/api/students");

        document.getElementById("studentCount").textContent =
            `${students.length} Students`;

        if (students.length === 0) {
            table.innerHTML =
                '<tr><td colspan="2">No students registered yet.</td></tr>';
            return;
        }

        table.innerHTML = students.map(student => `
            <tr>
                <td>${escapeHtml(student.student_code)}</td>
                <td>${escapeHtml(student.name)}</td>
            </tr>
        `).join("");

    } catch (error) {
        table.innerHTML =
            `<tr><td colspan="2">${escapeHtml(error.message)}</td></tr>`;
    }
}


const studentForm = document.getElementById("studentForm");

if (studentForm) {
    studentForm.addEventListener("submit", async event => {
        event.preventDefault();

        const studentCode =
            document.getElementById("studentCode").value.trim();

        const studentName =
            document.getElementById("studentName").value.trim();

        if (!studentCode || !studentName) {
            showMessage(
                "studentMessage",
                "Please enter both Student ID and Name.",
                "error"
            );
            return;
        }

        const button = studentForm.querySelector("button");
        button.disabled = true;

        try {
            await api("/api/students", {
                method: "POST",
                body: JSON.stringify({
                    student_code: studentCode,
                    name: studentName
                })
            });

            showMessage(
                "studentMessage",
                "Student registered successfully!"
            );

            studentForm.reset();

            await loadStudents();

        } catch (error) {
            showMessage("studentMessage", error.message, "error");

        } finally {
            button.disabled = false;
        }
    });
}


// ======================================
// QUESTION MANAGEMENT
// ======================================

async function loadQuestions() {
    const table = document.getElementById("questionTable");

    if (!table) return;

    try {
        const questions = await api("/api/questions");

        if (questions.length === 0) {
            table.innerHTML =
                '<tr><td colspan="4">No questions created yet.</td></tr>';
            return;
        }

        table.innerHTML = questions.map(question => `
            <tr>
                <td>${escapeHtml(question.title)}</td>

                <td>${escapeHtml(question.correct)}</td>

                <td>
                    ${question.active
                        ? '<span class="active-tag">ACTIVE</span>'
                        : '<span class="inactive-tag">INACTIVE</span>'}
                </td>

                <td>
                    ${question.active
                        ? "Currently Active"
                        : `<button
                            class="activate-button"
                            data-question-id="${Number(question.id)}">
                            Activate
                           </button>`}
                </td>
            </tr>
        `).join("");

        table.querySelectorAll(".activate-button").forEach(button => {
            button.addEventListener("click", async () => {
                await activateQuestion(button.dataset.questionId);
            });
        });

    } catch (error) {
        table.innerHTML =
            `<tr><td colspan="4">${escapeHtml(error.message)}</td></tr>`;
    }
}


async function activateQuestion(questionId) {
    if (!/^\d+$/.test(String(questionId))) return;

    try {
        await api(`/api/questions/${questionId}/activate`, {
            method: "POST"
        });

        showMessage(
            "questionMessage",
            "Question activated successfully!"
        );

        await loadQuestions();
        await loadActiveQuestion();
        await loadResults();

    } catch (error) {
        showMessage("questionMessage", error.message, "error");
    }
}


// ======================================
// ACTIVE QUESTION
// ======================================

async function loadActiveQuestion() {
    const element = document.getElementById("activeQuestion");

    if (!element) return;

    try {
        const question = await api("/api/active-question");

        if (!question) {
            element.textContent =
                "No active question. Please create or activate one.";
            return;
        }

        element.textContent =
            `Q${question.id}: ${question.title}`;

    } catch (error) {
        element.textContent = error.message;
    }
}


// ======================================
// LIVE RESULTS
// ======================================

async function loadResults() {
    const table = document.getElementById("resultsTable");

    if (!table) return;

    try {
        const data = await api("/api/results");

        const questionText = document.getElementById("resultsQuestion");

        if (!data.question) {
            questionText.textContent =
                "No active question. Activate a question to begin.";

            updateStat("counted", 0);
            updateStat("classSize", 0);
            updateStat("correct", 0);
            updateStat("wrong", 0);
            updateStat("notCounted", 0);

            table.innerHTML =
                '<tr><td colspan="4">No active question.</td></tr>';

            return;
        }

        questionText.textContent =
            `Active Question: ${data.question.title}`;

        const counted = Number(data.counted) || 0;
        const classSize = Number(data.total) || 0;
        const correct = Number(data.correct) || 0;
        const wrong = Number(data.wrong) || 0;
        const notCounted = Math.max(0, classSize - counted);

        updateStat("counted", counted);
        updateStat("classSize", classSize);
        updateStat("correct", correct);
        updateStat("wrong", wrong);
        updateStat("notCounted", notCounted);

        if (!data.students || data.students.length === 0) {
            table.innerHTML =
                '<tr><td colspan="4">No responses received yet.</td></tr>';
        } else {
            table.innerHTML = data.students.map(student => `
                <tr>
                    <td>${escapeHtml(student.student_code)}</td>

                    <td>${escapeHtml(student.name)}</td>

                    <td>${escapeHtml(student.answer)}</td>

                    <td>
                        ${student.is_correct
                            ? '<span class="correct-tag">CORRECT</span>'
                            : '<span class="wrong-tag">WRONG</span>'}
                    </td>
                </tr>
            `).join("");
        }

        document.getElementById("lastUpdated").textContent =
            `Last updated: ${new Date().toLocaleTimeString()}`;

    } catch (error) {
        document.getElementById("resultsMessage").textContent =
            `Unable to refresh results: ${error.message}`;
    }
}


function updateStat(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


// ======================================
// INITIALIZATION
// ======================================

async function initializeDashboard() {
    await Promise.all([
        loadStudents(),
        loadQuestions(),
        loadActiveQuestion(),
        loadResults()
    ]);

    // Refresh live results every 2 seconds.
    setInterval(loadResults, 2000);

    // Refresh question and student lists less frequently.
    setInterval(loadStudents, 10000);
    setInterval(loadQuestions, 5000);
    setInterval(loadActiveQuestion, 3000);
}

if (document.getElementById("studentForm")) {
    initializeDashboard();
}
