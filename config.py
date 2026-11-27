
import os
import cv2
from pathlib import Path


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

PROJECT_NAME = "PLICKERS_2.0"
DEBUG = True


# ==========================================
# FOLDER CONFIGURATION
# ==========================================

OUTPUT_DIR = BASE_DIR / "output"

QR_FOLDER = OUTPUT_DIR / "qr_codes"

CARD_FOLDER = OUTPUT_DIR / "cards"

LOG_FOLDER = BASE_DIR / "logs"


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE_DIR = BASE_DIR / "database"

DATABASE_PATH = DATABASE_DIR / "plickers.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


# ==========================================
# QR CODE CONFIGURATION
# ==========================================

QR_VERSION = None

QR_ERROR_CORRECTION = "H"

QR_BOX_SIZE = 12

QR_BORDER = 4


# ==========================================
# QR CARD CONFIGURATION
# ==========================================

CARD_WIDTH = 900

CARD_HEIGHT = 1200

QR_SIZE = 500

MARKER_SIZE = 180


# ==========================================
# OPENCV / ARUCO CONFIGURATION
# ==========================================

ARUCO_DICTIONARY = cv2.aruco.DICT_4X4_50

ARUCO_MARKER_ID = 0

SUPPORTED_ANSWERS = ["A", "B", "C", "D"]

ORIENTATION_MAPPING = {
    "TOP": "A",
    "RIGHT": "B",
    "BOTTOM": "C",
    "LEFT": "D"
}


# ==========================================
# CAMERA CONFIGURATION
# ==========================================

CAMERA_INDEX = 0

FRAME_WIDTH = 1280

FRAME_HEIGHT = 720

CAMERA_FPS = 30


# ==========================================
# SCANNER CONFIGURATION
# ==========================================

ENABLE_MULTI_CARD_SCANNING = True

ALLOW_DUPLICATE_RESPONSES = False

MIN_QR_CONFIDENCE = 0.5


# ==========================================
# FLASK CONFIGURATION
# ==========================================

HOST = "127.0.0.1"

PORT = 5000

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "change-this-development-secret"
)


# ==========================================
# CREATE REQUIRED DIRECTORIES
# ==========================================

REQUIRED_DIRECTORIES = [
    OUTPUT_DIR,
    QR_FOLDER,
    CARD_FOLDER,
    LOG_FOLDER,
    DATABASE_DIR
]


def create_directories():
    """Create required project directories."""

    for directory in REQUIRED_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


# Create folders when configuration is imported.
create_directories()
