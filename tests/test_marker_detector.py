
import cv2
import numpy as np

from scanner.marker_detector import detect_red_markers


def test_detect_red_marker():

    image = np.zeros((300, 300, 3), dtype=np.uint8)

    # Add a red circular marker
    cv2.circle(
        image,
        (150, 150),
        15,
        (0, 0, 255),
        -1
    )

    markers = detect_red_markers(image)

    assert len(markers) >= 1


def test_no_red_marker():

    image = np.zeros((300, 300, 3), dtype=np.uint8)

    markers = detect_red_markers(image)

    assert len(markers) == 0


def test_multiple_red_markers():

    image = np.zeros((400, 400, 3), dtype=np.uint8)

    cv2.circle(image, (100, 100), 15, (0, 0, 255), -1)
    cv2.circle(image, (250, 250), 15, (0, 0, 255), -1)

    markers = detect_red_markers(image)

    assert len(markers) >= 2


def test_marker_coordinates():

    image = np.zeros((300, 300, 3), dtype=np.uint8)

    cv2.circle(image, (150, 150), 15, (0, 0, 255), -1)

    markers = detect_red_markers(image)

    assert len(markers) >= 1

    x, y = markers[0]

    assert 130 <= x <= 170
    assert 130 <= y <= 170
