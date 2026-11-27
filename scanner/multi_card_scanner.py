
import cv2
import math

from scanner.marker_detector import MarkerDetector
from scanner.qr_detector import QRDetector


class MultiCardScanner:
    def __init__(self):
        self.marker_detector = MarkerDetector()
        self.qr_detector = QRDetector()

        # Maximum distance allowed between QR centre and marker.
        self.max_marker_distance = 300

    def calculate_distance(self, point1, point2):
        """Calculate distance between two points."""
        return math.sqrt(
            (point1[0] - point2[0]) ** 2
            + (point1[1] - point2[1]) ** 2
        )

    def decode_answer(self, qr_center, marker_center):
        """
        Determine answer based on marker position relative
        to QR centre.

        TOP = A
        RIGHT = B
        BOTTOM = C
        LEFT = D
        """
        dx = marker_center[0] - qr_center[0]
        dy = marker_center[1] - qr_center[1]

        if abs(dx) > abs(dy):
            if dx > 0:
                return "B"
            return "D"

        if dy > 0:
            return "C"

        return "A"

    def scan_frame(self, frame):
        """
        Detect multiple QR cards and their answer markers.

        Expected QRDetector.detect_qr_codes(frame) output:
        [
            {
                "data": "ROTQR:student_token",
                "center": (x, y)
            }
        ]

        Returns:
        [
            {
                "student_token": "...",
                "answer": "A",
                "qr_center": (x, y),
                "marker_center": (x, y)
            }
        ]
        """
        if frame is None:
            return []

        qr_codes = self.qr_detector.detect_qr_codes(frame)
        markers = self.marker_detector.detect_markers(frame)

        results = []
        used_markers = set()

        for qr in qr_codes:
            qr_data = qr.get("data")
            qr_center = qr.get("center")

            if not qr_data or qr_center is None:
                continue

            # Only accept QR codes belonging to this project.
            if not qr_data.startswith("ROTQR:"):
                continue

            closest_marker = None
            closest_distance = float("inf")
            closest_index = None

            for index, marker in enumerate(markers):
                if index in used_markers:
                    continue

                marker_center = marker["center"]

                distance = self.calculate_distance(
                    qr_center,
                    marker_center
                )

                if (
                    distance < closest_distance
                    and distance <= self.max_marker_distance
                ):
                    closest_distance = distance
                    closest_marker = marker
                    closest_index = index

            # No suitable marker found for this QR code.
            if closest_marker is None:
                continue

            marker_center = closest_marker["center"]

            answer = self.decode_answer(
                qr_center,
                marker_center
            )

            student_token = qr_data.replace("ROTQR:", "", 1)

            results.append({
                "student_token": student_token,
                "answer": answer,
                "qr_center": qr_center,
                "marker_center": marker_center
            })

            used_markers.add(closest_index)

        return results

    def draw_results(self, frame, results):
        """Draw detected answers on the camera frame."""
        output = frame.copy()

        for result in results:
            qr_x, qr_y = result["qr_center"]
            marker_x, marker_y = result["marker_center"]

            answer = result["answer"]

            cv2.circle(
                output,
                (marker_x, marker_y),
                8,
                (0, 255, 0),
                -1
            )

            cv2.line(
                output,
                (qr_x, qr_y),
                (marker_x, marker_y),
                (255, 0, 0),
                2
            )

            cv2.putText(
                output,
                answer,
                (qr_x, qr_y - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        return output


if __name__ == "__main__":
    from scanner.camera import Camera

    scanner = MultiCardScanner()
    camera = Camera()

    if camera.start():
        try:
            while True:
                frame = camera.read_frame()

                if frame is None:
                    continue

                results = scanner.scan_frame(frame)
                output = scanner.draw_results(frame, results)

                for result in results:
                    print(
                        "Student:", result["student_token"],
                        "| Answer:", result["answer"]
                    )

                cv2.imshow("PLICKERS 2.0 - Multi Card Scanner", output)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            camera.stop()
            cv2.destroyAllWindows()
