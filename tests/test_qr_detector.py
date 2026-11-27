
import cv2
import numpy as np
import qrcode

from scanner.qr_detector import (
    decode_student_id,
    detect_multiple_qr
)


def create_qr(student_id):

    qr = qrcode.make(student_id)

    qr = qr.convert("RGB")

    image = np.array(qr)

    return cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )


def test_unique_student_id():

    qr_data = "STUDENT001"

    student_id = decode_student_id(qr_data)

    assert student_id == "STUDENT001"


def test_json_student_id():

    qr_data = '{"student_id": "STUDENT025"}'

    student_id = decode_student_id(qr_data)

    assert student_id == "STUDENT025"


def test_invalid_qr_data():

    student_id = decode_student_id("")

    assert student_id is None


def test_multiple_qr_detection():

    qr1 = create_qr("STUDENT001")
    qr2 = create_qr("STUDENT002")
    qr3 = create_qr("STUDENT003")

    separator = np.ones(
        (qr1.shape[0], 30, 3),
        dtype=np.uint8
    ) * 255

    combined = np.hstack([
        qr1,
        separator,
        qr2,
        separator,
        qr3
    ])

    detector = cv2.QRCodeDetector()

    success, decoded_info, points, _ = (
        detector.detectAndDecodeMulti(combined)
    )

    assert success

    detected_ids = [
        value for value in decoded_info if value
    ]

    assert len(detected_ids) == 3

    assert set(detected_ids) == {
        "STUDENT001",
        "STUDENT002",
        "STUDENT003"
    }


def test_batch_detection_function():

    image = create_qr("STUDENT001")

    results = detect_multiple_qr(image)

    assert isinstance(results, list)
