
import math


def decode_answer(qr_corners, marker_center):
    """
    Decode the student's answer using the red marker position
    relative to the QR code centre.

    Args:
        qr_corners: Four corner points of the QR code.
                    Example: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

        marker_center: Centre of the red marker.
                       Example: (marker_x, marker_y)

    Returns:
        "A", "B", "C", "D", or None if decoding fails.
    """

    if qr_corners is None or marker_center is None:
        return None

    try:
        # Calculate the centre of the QR code
        qr_center_x = sum(point[0] for point in qr_corners) / 4
        qr_center_y = sum(point[1] for point in qr_corners) / 4

        # Calculate marker position relative to QR centre
        dx = marker_center[0] - qr_center_x
        dy = marker_center[1] - qr_center_y

        # Find the angle of the marker
        angle = math.degrees(math.atan2(dx, -dy))

        # Convert angle into one of four directions
        sector = int(math.floor((angle + 45) / 90)) % 4

        # Map directions to answers
        answers = ["A", "B", "C", "D"]

        return answers[sector]

    except (TypeError, ValueError, IndexError, ZeroDivisionError):
        return None
