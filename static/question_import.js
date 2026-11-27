
"use strict";

(() => {

    // ==========================================
    // CONFIGURATION
    // ==========================================

    const API_URL = "/api/questions/import";

    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

    const MAX_QUESTIONS = 500;

    const REQUIRED_COLUMNS = [
        "title",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct"
    ];

    // ==========================================
    // HTML ELEMENTS
    // ==========================================

    const fileInput = document.getElementById("questionFile");

    const previewButton = document.getElementById("previewButton");

    const importButton = document.getElementById("importButton");

    const previewTable = document.getElementById("previewTable");

    const previewCount = document.getElementById("previewCount");

    const importMessage = document.getElementById("importMessage");


    // Stop if this script is loaded on a page without the import form.
    if (
        !fileInput ||
        !previewButton ||
        !importButton ||
        !previewTable ||
        !importMessage
    ) {
        return;
    }


    // ==========================================
    // STATE
    // ==========================================

    let importedQuestions = [];

    let importInProgress = false;


    // ==========================================
    // HTML ESCAPING
    // ==========================================

    function escapeHtml(value) {

        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[character]);

    }


    // ==========================================
    // MESSAGE DISPLAY
    // ==========================================

    function showMessage(message, type = "success") {

        importMessage.textContent = message;

        importMessage.className = `message ${type}`;

    }


    // ==========================================
    // CLEAR PREVIOUS PREVIEW
    // ==========================================

    function clearPreview() {

        importedQuestions = [];

        importButton.disabled = true;

        previewTable.innerHTML = `
            <tr>
                <td colspan="6">
                    No questions uploaded yet.
                </td>
            </tr>
        `;

        if (previewCount) {
            previewCount.textContent = "Total questions: 0";
        }

    }


    // ==========================================
    // RESET BUTTONS
    // ==========================================

    function setLoading(isLoading) {

        previewButton.disabled = isLoading;

        importButton.disabled =
            isLoading || importedQuestions.length === 0;

        fileInput.disabled = isLoading;

        previewButton.textContent = isLoading
            ? "Please wait..."
            : "Preview Questions";

        importButton.textContent = isLoading
            ? "Processing..."
            : "Import Questions";

    }


    // ==========================================
    // NORMALIZE COLUMN HEADINGS
    // ==========================================

    function normalizeHeader(header) {

        return String(header ?? "")
            .replace(/^\uFEFF/, "")
            .trim()
            .toLowerCase()
            .replace(/[\s-]+/g, "_");

    }


    // ==========================================
    // NORMALIZE IMPORTED DATA
    // ==========================================

    function normalizeQuestions(rows) {

        return rows.map(row => {

            const normalizedRow = {};

            Object.entries(row).forEach(([key, value]) => {

                normalizedRow[normalizeHeader(key)] = value;

            });

            return {

                title: String(normalizedRow.title ?? "").trim(),

                option_a: String(normalizedRow.option_a ?? "").trim(),

                option_b: String(normalizedRow.option_b ?? "").trim(),

                option_c: String(normalizedRow.option_c ?? "").trim(),

                option_d: String(normalizedRow.option_d ?? "").trim(),

                correct: String(normalizedRow.correct ?? "")
                    .trim()
                    .toUpperCase()

            };

        }).filter(question => {

            // Ignore completely empty spreadsheet rows.
            return Object.values(question).some(value => value !== "");

        });

    }


    // ==========================================
    // VALIDATE COLUMN HEADINGS
    // ==========================================

    function validateHeaders(rows) {

        if (!rows.length) {

            throw new Error("The uploaded file is empty.");

        }

        const headers = Object.keys(rows[0])
            .map(normalizeHeader);

        const missingColumns = REQUIRED_COLUMNS.filter(
            column => !headers.includes(column)
        );

        if (missingColumns.length > 0) {

            throw new Error(
                "Missing required columns: " +
                missingColumns.join(", ")
            );

        }

    }


    // ==========================================
    // VALIDATE QUESTION CONTENT
    // ==========================================

    function validateQuestions(questions) {

        const errors = [];

        questions.forEach((question, index) => {

            const rowNumber = index + 2;

            if (!question.title) {

                errors.push(
                    `Row ${rowNumber}: Question text is missing.`
                );

            }

            if (!question.option_a) {

                errors.push(
                    `Row ${rowNumber}: Option A is missing.`
                );

            }

            if (!question.option_b) {

                errors.push(
                    `Row ${rowNumber}: Option B is missing.`
                );

            }

            if (!question.option_c) {

                errors.push(
                    `Row ${rowNumber}: Option C is missing.`
                );

            }

            if (!question.option_d) {

                errors.push(
                    `Row ${rowNumber}: Option D is missing.`
                );

            }

            if (!["A", "B", "C", "D"].includes(question.correct)) {

                errors.push(
                    `Row ${rowNumber}: Correct answer must be A, B, C or D.`
                );

            }

        });

        return errors;

    }


    // ==========================================
    // DISPLAY QUESTION PREVIEW
    // ==========================================

    function displayPreview(questions) {

        if (!questions.length) {

            clearPreview();

            return;

        }

        previewTable.innerHTML = questions.map(question => `

            <tr>

                <td>${escapeHtml(question.title)}</td>

                <td>${escapeHtml(question.option_a)}</td>

                <td>${escapeHtml(question.option_b)}</td>

                <td>${escapeHtml(question.option_c)}</td>

                <td>${escapeHtml(question.option_d)}</td>

                <td>
                    <strong>${escapeHtml(question.correct)}</strong>
                </td>

            </tr>

        `).join("");


        if (previewCount) {

            previewCount.textContent =
                `Total questions: ${questions.length}`;

        }

    }


    // ==========================================
    // READ CSV / EXCEL FILE
    // ==========================================

    async function readQuestionFile(file) {

        if (typeof XLSX === "undefined") {

            throw new Error(
                "Excel reading library could not load. " +
                "Check your internet connection."
            );

        }


        const extension = file.name
            .split(".")
            .pop()
            .toLowerCase();


        if (!["csv", "xlsx"].includes(extension)) {

            throw new Error(
                "Only CSV and Excel (.xlsx) files are supported."
            );

        }


        if (file.size === 0) {

            throw new Error("The selected file is empty.");

        }


        if (file.size > MAX_FILE_SIZE) {

            throw new Error(
                "File size exceeds the 5 MB limit."
            );

        }


        const buffer = await file.arrayBuffer();


        const workbook = XLSX.read(buffer, {

            type: "array",

            cellDates: false

        });


        if (!workbook.SheetNames.length) {

            throw new Error("No worksheet found in the file.");

        }


        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];


        const rows = XLSX.utils.sheet_to_json(firstSheet, {

            defval: "",

            raw: false

        });


        validateHeaders(rows);


        const questions = normalizeQuestions(rows);


        if (questions.length === 0) {

            throw new Error("No valid question rows were found.");

        }


        if (questions.length > MAX_QUESTIONS) {

            throw new Error(
                `Maximum ${MAX_QUESTIONS} questions can be imported at once.`
            );

        }


        return questions;

    }


    // ==========================================
    // PREVIEW BUTTON
    // ==========================================

    previewButton.addEventListener("click", async () => {

        if (importInProgress) return;

        clearPreview();

        showMessage("");

        const file = fileInput.files[0];


        if (!file) {

            showMessage(
                "Please select a CSV or Excel file first.",
                "error"
            );

            return;

        }


        try {

            setLoading(true);

            const questions = await readQuestionFile(file);


            const errors = validateQuestions(questions);


            if (errors.length > 0) {

                const visibleErrors = errors.slice(0, 10);

                const remaining = errors.length - visibleErrors.length;

                showMessage(
                    visibleErrors.join(" ") +
                    (remaining > 0
                        ? ` And ${remaining} more error(s).`
                        : ""),
                    "error"
                );

                return;

            }


            importedQuestions = questions;

            displayPreview(importedQuestions);

            importButton.disabled = false;


            showMessage(
                `${importedQuestions.length} questions validated successfully. ` +
                "Review the preview before importing."
            );


        } catch (error) {

            showMessage(error.message, "error");

        } finally {

            setLoading(false);

        }

    });


    // ==========================================
    // IMPORT QUESTIONS TO FLASK BACKEND
    // ==========================================

    importButton.addEventListener("click", async () => {

        if (importInProgress) return;


        if (importedQuestions.length === 0) {

            showMessage(
                "Please preview and validate questions first.",
                "error"
            );

            return;

        }


        const confirmed = window.confirm(

            `Are you sure you want to import ${importedQuestions.length} questions?`

        );


        if (!confirmed) return;


        importInProgress = true;

        setLoading(true);

        showMessage("Importing questions into the database...");


        try {

            const response = await fetch(API_URL, {

                method: "POST",

                headers: {

                    "Content-Type": "application/json",

                    "Accept": "application/json"

                },

                body: JSON.stringify({

                    questions: importedQuestions

                })

            });


            let data;

            try {

                data = await response.json();

            } catch {

                throw new Error(
                    "The server returned an invalid response."
                );

            }


            if (!response.ok) {

                throw new Error(
                    data.error || "Unable to import questions."
                );

            }


            if (
                data.ok !== true ||
                !Number.isInteger(data.imported) ||
                data.imported !== importedQuestions.length
            ) {

                throw new Error(
                    data.error ||
                    "The server did not confirm that all questions were imported."
                );

            }


            showMessage(

                `${data.imported} questions imported successfully! ` +
                "You can now activate them from the dashboard."

            );


            // Clear the imported file and preview after success.

            importedQuestions = [];

            fileInput.value = "";

            displayPreview([]);

            importButton.disabled = true;


        } catch (error) {

            showMessage(error.message, "error");

        } finally {

            importInProgress = false;

            setLoading(false);

        }

    });


    // ==========================================
    // FILE CHANGE EVENT
    // ==========================================

    fileInput.addEventListener("change", () => {

        clearPreview();

        showMessage("");

    });


    // ==========================================
    // INITIAL STATE
    // ==========================================

    clearPreview();

    console.log("PLICKERS 2.O Question Import Module Loaded.");

})();
