
// ==========================================
// RotQR Classroom - Scanner JavaScript
// Camera capture and communication with Flask
// ==========================================

// HTML elements
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

const startButton = document.getElementById("startCamera");
const stopButton = document.getElementById("stopCamera");

const statusText = document.getElementById("scannerStatus");
const activeQuestion = document.getElementById("activeQuestion");
const scanLog = document.getElementById("scanLog");

// Camera variables
let cameraStream = null;
let scanning = false;
let scanBusy = false;

let scanTimer = null;
let questionTimer = null;

// Capture interval in milliseconds
const SCAN_INTERVAL = 250;

// Frame quality
const IMAGE_QUALITY = 0.75;

// ==========================================
// API helper
// ==========================================

async function api(url, options = {}) {

    const response = await fetch(url, options);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Server request failed.");
    }

    return data;
}

// ==========================================
// Start camera
// ==========================================

async function startCamera() {

    if (scanning) return;

    try {

        statusText.textContent = "Requesting camera permission...";

        cameraStream = await navigator.mediaDevices.getUserMedia({

            video: {
                facingMode: "environment",
                width: {
                    ideal: 1280
                },
                height: {
                    ideal: 720
                }
            },

            audio: false

        });

        video.srcObject = cameraStream;

        await video.play();

        scanning = true;

        startButton.disabled = true;
        stopButton.disabled = false;

        statusText.textContent = "Camera started. Scanning classroom...";

        scanFrame();

        // Refresh active question every 3 seconds
        await updateActiveQuestion();

        questionTimer = setInterval(
            updateActiveQuestion,
            3000
        );

    } catch (error) {

        console.error("Camera error:", error);

        statusText.textContent =
            "Unable to access camera. Allow camera permission and use HTTPS or localhost.";

        stopCamera();

    }
}

// ==========================================
// Capture and send camera frame
// ==========================================

async function scanFrame() {

    if (!scanning || scanBusy) return;

    scanBusy = true;

    try {

        if (
            video.readyState >= video.HAVE_CURRENT_DATA &&
            video.videoWidth > 0
        ) {

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const context = canvas.getContext("2d", {
                willReadFrequently: true
            });

            context.drawImage(
                video,
                0,
                0,
                canvas.width,
                canvas.height
            );

            // Convert frame to JPEG
            const blob = await new Promise(resolve => {

                canvas.toBlob(
                    resolve,
                    "image/jpeg",
                    IMAGE_QUALITY
                );

            });

            if (!blob) {
                throw new Error("Unable to capture camera frame.");
            }

            // Send frame to Flask backend
            const formData = new FormData();

            formData.append(
                "frame",
                blob,
                "classroom.jpg"
            );

            const result = await api("/api/scan-frame", {

                method: "POST",
                body: formData

            });

            // Process all detected student cards
            if (Array.isArray(result.results)) {

                result.results.forEach(processScanResult);

            }

            if (result.status === "no_question") {

                statusText.textContent =
                    "No active question. Start one from dashboard.";

            } else if (result.status === "ok") {

                statusText.textContent =
                    result.results.length > 0
                        ? `${result.results.length} scan result(s) received.`
                        : "Camera active. Looking for QR cards...";

            }

        }

    } catch (error) {

        console.error("Scanning error:", error);

        statusText.textContent =
            "Scanner error: " + error.message;

    } finally {

        scanBusy = false;

        // Schedule next frame
        if (scanning) {

            scanTimer = setTimeout(
                scanFrame,
                SCAN_INTERVAL
            );

        }

    }

}

// ==========================================
// Process individual scan result
// ==========================================

function processScanResult(result) {

    const student = result.student_code || "Unknown student";
    const answer = result.answer || "-";

    if (result.status === "counted") {

        const correctness = result.is_correct
            ? "CORRECT"
            : "WRONG";

        addLog(
            `${student}: ${answer} (${correctness})`
        );

    } else if (result.status === "duplicate") {

        addLog(
            `${student} already counted for this question.`
        );

    } else if (result.status === "unknown") {

        addLog(
            "Unknown student QR detected."
        );

    } else if (result.status === "invalid") {

        addLog(
            "Invalid QR or orientation."
        );

    } else if (result.status === "no_question") {

        statusText.textContent =
            "No active question.";

    } else if (result.status === "error") {

        addLog(
            result.message || "Unable to process card."
        );

    }

}

// ==========================================
// Add scan activity to log
// ==========================================

function addLog(message) {

    const item = document.createElement("li");

    // textContent prevents HTML injection
    item.textContent =
        `${new Date().toLocaleTimeString()} - ${message}`;

    scanLog.prepend(item);

    // Keep only latest 12 results
    while (scanLog.children.length > 12) {

        scanLog.removeChild(
            scanLog.lastElementChild
        );

    }

}

// ==========================================
// Get active question
// ==========================================

async function updateActiveQuestion() {

    try {

        const data = await api("/api/active-question");

        if (data.question) {

            activeQuestion.textContent =
                `Active Q${data.question.id}: ${data.question.title}`;

        } else {

            activeQuestion.textContent =
                "No active question. Start one from dashboard.";

        }

    } catch (error) {

        console.error(
            "Question loading error:",
            error
        );

        activeQuestion.textContent =
            "Unable to load active question.";

    }

}

// ==========================================
// Stop camera
// ==========================================

function stopCamera() {

    scanning = false;

    clearTimeout(scanTimer);
    clearInterval(questionTimer);

    if (cameraStream) {

        cameraStream.getTracks().forEach(track => {
            track.stop();
        });

        cameraStream = null;

    }

    video.srcObject = null;

    startButton.disabled = false;
    stopButton.disabled = true;

    statusText.textContent = "Camera stopped.";

}

// ==========================================
// Button events
// ==========================================

startButton.addEventListener(
    "click",
    startCamera
);

stopButton.addEventListener(
    "click",
    stopCamera
);

// Stop camera when leaving the page
window.addEventListener(
    "pagehide",
    stopCamera
);
