
import json
import uuid
from pathlib import Path

import cv2
import numpy as np
import qrcode

from PIL import Image, ImageDraw, ImageFont


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

try:
    from config import QR_FOLDER, CARD_FOLDER

    QR_DIR = Path(QR_FOLDER)
    CARD_DIR = Path(CARD_FOLDER)

except ImportError:
    QR_DIR = BASE_DIR / "output" / "qr_codes"
    CARD_DIR = BASE_DIR / "output" / "cards"

MANIFEST_PATH = BASE_DIR / "output" / "qr_manifest.json"

SYSTEM_NAME = "PLICKERS_2.0"

# Same orientation marker on every card.
ARUCO_DICTIONARY = cv2.aruco.DICT_4X4_50
ARUCO_MARKER_ID = 0

from config import (
    CARD_WIDTH,
    CARD_HEIGHT,
    QR_SIZE,
    MARKER_SIZE,
    ARUCO_DICTIONARY,
    ARUCO_MARKER_ID
)


# --------------------------------------------------
# QR GENERATOR CLASS
# --------------------------------------------------

class QRGenerator:

    def __init__(self):

        QR_DIR.mkdir(parents=True, exist_ok=True)
        CARD_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

        self.dictionary = cv2.aruco.getPredefinedDictionary(
            ARUCO_DICTIONARY
        )

        self.generated_ids = set()

    # --------------------------------------------------
    # GENERATE UNIQUE QR IDENTIFICATION
    # --------------------------------------------------

    def create_unique_id(self):

        while True:

            unique_id = uuid.uuid4().hex

            if unique_id not in self.generated_ids:
                self.generated_ids.add(unique_id)
                return unique_id

    # --------------------------------------------------
    # GENERATE QR CODE
    # --------------------------------------------------

    def generate_qr(self, unique_id):

        qr_data = {
            "system": SYSTEM_NAME,
            "card_id": unique_id
        }

        qr_content = json.dumps(qr_data)

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4
        )

        qr.add_data(qr_content)
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white"
        ).convert("RGB")

        qr_image = qr_image.resize(
            (QR_SIZE, QR_SIZE),
            Image.Resampling.NEAREST
        )

        qr_path = QR_DIR / f"{unique_id}.png"

        qr_image.save(qr_path)

        return qr_image, qr_path

    # --------------------------------------------------
    # GENERATE ARUCO ORIENTATION MARKER
    # --------------------------------------------------

    def generate_orientation_marker(self):

        # Generate the same marker for every card.
        # Its position relative to the QR code
        # determines the selected answer.

        marker = cv2.aruco.generateImageMarker(
            self.dictionary,
            ARUCO_MARKER_ID,
            MARKER_SIZE
        )

        marker_image = Image.fromarray(marker).convert("RGB")

        return marker_image

    # --------------------------------------------------
    # GENERATE PRINTABLE CARD
    # --------------------------------------------------

    def generate_card(self, card_number, unique_id):

        qr_image, qr_path = self.generate_qr(unique_id)

        marker_image = self.generate_orientation_marker()

        card = Image.new(
            "RGB",
            (CARD_WIDTH, CARD_HEIGHT),
            "white"
        )

        draw = ImageDraw.Draw(card)

        try:
            title_font = ImageFont.truetype(
                "arial.ttf", 48
            )

            text_font = ImageFont.truetype(
                "arial.ttf", 30
            )

        except OSError:

            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Title
        title = "PLICKERS 2.0"

        title_box = draw.textbbox(
            (0, 0), title, font=title_font
        )

        title_width = title_box[2] - title_box[0]

        draw.text(
            ((CARD_WIDTH - title_width) // 2, 35),
            title,
            fill="black",
            font=title_font
        )

        # Orientation marker at the TOP of the QR.
        marker_x = (CARD_WIDTH - MARKER_SIZE) // 2
        marker_y = 140

        card.paste(
            marker_image,
            (marker_x, marker_y)
        )

        # QR code below the orientation marker.
        qr_x = (CARD_WIDTH - QR_SIZE) // 2
        qr_y = 400

        card.paste(
            qr_image,
            (qr_x, qr_y)
        )

        # Card number for human reference.
        card_label = f"CARD {card_number:03d}"

        label_box = draw.textbbox(
            (0, 0), card_label, font=text_font
        )

        label_width = label_box[2] - label_box[0]

        draw.text(
            ((CARD_WIDTH - label_width) // 2, 970),
            card_label,
            fill="black",
            font=text_font
        )

        # Orientation instructions.
        instruction = "Rotate card to select your answer"

        instruction_box = draw.textbbox(
            (0, 0), instruction, font=text_font
        )

        instruction_width = (
            instruction_box[2] - instruction_box[0]
        )

        draw.text(
            (
                (CARD_WIDTH - instruction_width) // 2,
                1040
            ),
            instruction,
            fill="black",
            font=text_font
        )

        # Save printable card.
        card_path = CARD_DIR / f"card_{card_number:03d}.png"

        card.save(card_path)

        return {
            "card_number": card_number,
            "card_id": unique_id,
            "qr_path": str(qr_path),
            "card_path": str(card_path)
        }

    # --------------------------------------------------
    # GENERATE ANY NUMBER OF CARDS
    # --------------------------------------------------

    def generate_cards(self, count):

        if not isinstance(count, int) or isinstance(count, bool):
            raise ValueError("Card count must be an integer.")

        if count <= 0:
            raise ValueError("Enter a number greater than zero.")

        results = []
        manifest = {}

        print("\nGenerating PLICKERS 2.0 QR cards...\n")

        for number in range(1, count + 1):

            unique_id = self.create_unique_id()

            result = self.generate_card(
                number,
                unique_id
            )

            results.append(result)

            manifest[unique_id] = {
                "card_number": number,
                "system": SYSTEM_NAME
            }

            print(
                f"Generated card {number}/{count}"
            )

        # Save QR identification mapping.
        with open(
            MANIFEST_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                manifest,
                file,
                indent=4
            )

        print("\n--------------------------------")
        print("QR GENERATION COMPLETED")
        print("--------------------------------")

        print(f"Total cards generated: {count}")
        print(f"Unique QR codes: {len(manifest)}")
        print(f"QR images folder: {QR_DIR}")
        print(f"Cards folder: {CARD_DIR}")
        print(f"Manifest: {MANIFEST_PATH}")

        return results


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    generator = QRGenerator()

    try:

        number_of_cards = int(
            input("Enter the number of QR cards to generate: ")
        )

        generator.generate_cards(number_of_cards)

    except ValueError as error:

        print(f"\nError: {error}")

    except Exception as error:

        print(f"\nGeneration failed: {error}")
