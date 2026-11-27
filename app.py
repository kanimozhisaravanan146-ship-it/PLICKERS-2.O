
import os
import logging

from flask import (
    Flask,
    render_template,
    jsonify,
    request
)

# Existing project modules
from scanner.camera import Camera
from scanner.multi_card_scanner import MultiCardScanner
from services.question_service import QuestionService
from services.response_processor import ResponseProcessor
from services.result_service import ResultService


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config["JSON_SORT_KEYS"] = False

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# INITIALIZE EXISTING SERVICES
# --------------------------------------------------

camera = None
scanner = None

question_service = QuestionService()
response_processor = ResponseProcessor()
result_service = ResultService()

active_question_id = None
scanning = False


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# QUESTIONS PAGE
# --------------------------------------------------

@app.route("/questions")
def questions():
    return render_template("questions.html")


# --------------------------------------------------
# SCANNER PAGE
# --------------------------------------------------

@app.route("/scanner")
def scanner_page():
    return render_template("scanner.html")


# --------------------------------------------------
# CAMERA INITIALIZATION
# --------------------------------------------------

@app.route("/api/camera/start", methods=["POST"])
def start_camera():

    global camera
    global scanner

    try:

        if camera is None:

            camera = Camera()

            # Initialize the multi-card scanner
            scanner = MultiCardScanner(camera)

        return jsonify({
            "success": True,
            "message": "Camera initialized"
        })

    except Exception as error:

        logger.exception("Camera initialization failed")

        camera = None
        scanner = None

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# --------------------------------------------------
# STOP CAMERA
# --------------------------------------------------

@app.route("/api/camera/stop", methods=["POST"])
def stop_camera():

    global camera
    global scanner
    global scanning

    scanning = False

    try:

        if camera is not None:
            camera.release()

        camera = None
        scanner = None

        return jsonify({
            "success": True,
            "message": "Camera stopped"
        })

    except Exception as error:

        logger.exception("Camera stop failed")

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# --------------------------------------------------
# ACTIVATE QUESTION
# --------------------------------------------------

@app.route("/api/questions/activate", methods=["POST"])
def activate_question():

    global active_question_id

    data = request.get_json(silent=True) or {}

    question_id = data.get("question_id")

    if not question_id:

        return jsonify({
            "success": False,
            "message": "Question ID is required"
        }), 400

    try:

        # Use existing question service
        active_question_id = question_id

        return jsonify({
            "success": True,
            "question_id": active_question_id
        })

    except Exception as error:

        logger.exception("Question activation failed")

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# --------------------------------------------------
# START BATCH SCANNING
# --------------------------------------------------

@app.route("/api/scan/start", methods=["POST"])
def start_scanning():

    global scanning

    if camera is None or scanner is None:

        return jsonify({
            "success": False,
            "message": "Start the camera first"
        }), 400

    if active_question_id is None:

        return jsonify({
            "success": False,
            "message": "Activate a question first"
        }), 400

    scanning = True

    return jsonify({
        "success": True,
        "message": "Batch scanning started",
        "question_id": active_question_id
    })


# --------------------------------------------------
# STOP BATCH SCANNING
# --------------------------------------------------

@app.route("/api/scan/stop", methods=["POST"])
def stop_scanning():

    global scanning

    scanning = False

    return jsonify({
        "success": True,
        "message": "Batch scanning stopped"
    })


# --------------------------------------------------
# PROCESS BATCH OF QR CARDS
# --------------------------------------------------

@app.route("/api/scan/process", methods=["POST"])
def process_batch():

    if not scanning or scanner is None:

        return jsonify({
            "success": False,
            "message": "Scanner is not active"
        }), 400

    try:

        # Capture and detect all visible cards.
        # This method must match the implementation
        # inside your multi_card_scanner.py.

        results = scanner.scan_all_cards()

        processed_results = []

        for card in results:

            # Send each detected student response
            # through the existing response processor.

            response = response_processor.process_response(
                card,
                active_question_id
            )

            if response:

                processed_results.append(response)

        return jsonify({
            "success": True,
            "question_id": active_question_id,
            "total_detected": len(results),
            "total_processed": len(processed_results),
            "results": processed_results
        })

    except Exception as error:

        logger.exception("Batch scanning failed")

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# --------------------------------------------------
# GET QUESTION RESULTS
# --------------------------------------------------

@app.route("/api/results", methods=["GET"])
def get_results():

    question_id = request.args.get(
        "question_id",
        active_question_id
    )

    if not question_id:

        return jsonify({
            "success": False,
            "message": "No active question"
        }), 400

    try:

        results = result_service.get_results(
            question_id
        )

        return jsonify({
            "success": True,
            "question_id": question_id,
            "results": results
        })

    except Exception as error:

        logger.exception("Result retrieval failed")

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# --------------------------------------------------
# APPLICATION STATUS
# --------------------------------------------------

@app.route("/api/status", methods=["GET"])
def application_status():

    return jsonify({
        "application": "PLICKERS-2.0",
        "camera_initialized": camera is not None,
        "scanning": scanning,
        "active_question": active_question_id,
        "student_capacity": "Dynamic"
    })


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 45)
    print("          PLICKERS-2.0")
    print("=" * 45)
    print("Dynamic QR Batch Scanning")
    print("Multi-Student Detection")
    print("Custom Red Marker Orientation")
    print("=" * 45)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
