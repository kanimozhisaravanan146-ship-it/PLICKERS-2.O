
import cv2
import numpy as np


class MarkerDetector:
    def __init__(self, min_radius=5, max_radius=60):
        self.min_radius = min_radius
        self.max_radius = max_radius

    def detect_markers(self, frame):
        """
        Detect red circular markers in a frame.

        Returns:
            List of dictionaries:
            [
                {"center": (x, y), "radius": radius}
            ]
        """
        if frame is None:
            return []

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Red appears at both ends of the HSV hue range.
        lower_red_1 = np.array([0, 100, 80])
        upper_red_1 = np.array([10, 255, 255])

        lower_red_2 = np.array([160, 100, 80])
        upper_red_2 = np.array([180, 255, 255])

        mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
        mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

        mask = cv2.bitwise_or(mask_1, mask_2)

        # Remove small noise.
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(
            mask, cv2.MORPH_OPEN, kernel
        )
        mask = cv2.morphologyEx(
            mask, cv2.MORPH_CLOSE, kernel
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        markers = []

        for contour in contours:
            area = cv2.contourArea(contour)

            if area <= 0:
                continue

            perimeter = cv2.arcLength(contour, True)

            if perimeter == 0:
                continue

            circularity = (
                4 * np.pi * area / (perimeter * perimeter)
            )

            (x, y), radius = cv2.minEnclosingCircle(contour)

            if not (
                self.min_radius <= radius <= self.max_radius
            ):
                continue

            # Reject shapes that are not sufficiently circular.
            if circularity < 0.65:
                continue

            markers.append({
                "center": (int(x), int(y)),
                "radius": int(radius)
            })

        return markers

    def draw_markers(self, frame, markers):
        """Draw detected markers for debugging."""
        output = frame.copy()

        for marker in markers:
            x, y = marker["center"]
            radius = marker["radius"]

            cv2.circle(
                output,
                (x, y),
                radius,
                (0, 255, 0),
                2
            )

            cv2.circle(
                output,
                (x, y),
                3,
                (255, 0, 0),
                -1
            )

        return output
