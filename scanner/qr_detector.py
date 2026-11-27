
"""
qr_detector.py

Detects and decodes multiple RotQR student cards
from a single camera frame using OpenCV.
"""

import cv2
import numpy as np
from typing import Optional


class QRDetector:
    """Detect and decode multiple ROTQR QR codes."""

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def detect_multiple(self, frame: np.ndarray) -> list[dict]:
        """
        Detect multiple QR codes in one frame.

        Returns:
            A list of dictionaries containing:
            - payload
            - token
            - corners
            - center
            - size
        """

        if frame is None or frame.size == 0:
            return []

        results = []

        try:
            success, decoded_info, points, _ = (
                self.detector.detectAndDecodeMulti(frame)
            )
        except cv2.error:
            return []

        if not success or points is None:
            return []

        for payload, qr_points in zip(decoded_info, points):

            # Ignore empty or invalid QR payloads.
            if not payload or not payload.startswith("ROTQR:"):
                continue

            token = payload[len("ROTQR:"):].strip()

            if not token:
                continue

            # Convert corner points into NumPy array.
            corners = np.asarray(qr_points, dtype=np.float32)

            if corners.shape != (4, 2):
                continue

            # Calculate QR centre using the four corners.
            center = np.mean(corners, axis=0)

            # Calculate the two diagonal lengths.
            diagonal_1 = np.linalg.norm(corners[0] - corners[2])
            diagonal_2 = np.linalg.norm(corners[1] - corners[3])

            qr_size = max(diagonal_1, diagonal_2)

            if qr_size <= 0:
                continue

            results.append({
                "payload": payload,
                "token": token,
                "corners": corners,
                "center": (
                    float(center[0]),
                    float(center[1])
                ),
                "size": float(qr_size)
            })

        return results

    def detect_single(self, frame: np.ndarray) -> Optional[dict]:
        """
        Detect the first valid ROTQR code in a frame.
        Useful for individual QR testing.
        """

        results = self.detect_multiple(frame)

        return results[0] if results else None

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: list[dict]
    ) -> np.ndarray:
        """
        Draw QR boundaries and decoded payloads
        for debugging purposes.
        """

        output = frame.copy()

        for detection in detections:

            corners = detection["corners"].astype(np.int32)

            # Draw QR boundary.
            cv2.polylines(
                output,
                [corners],
                True,
                (0, 255, 0),
                2
            )

            center_x, center_y = map(
                int, detection["center"]
            )

            # Draw centre point.
            cv2.circle(
                output,
                (center_x, center_y),
                5,
                (255, 0, 0),
                -1
            )

            # Display QR payload.
            cv2.putText(
                output,
                detection["payload"],
                (center_x - 60, center_y - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return output
