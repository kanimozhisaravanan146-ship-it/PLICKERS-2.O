
"""
scan_validation.py

Validates QR payloads and decoded answers
before submitting them to the response processor.
"""

import time
from typing import Optional


class ScanValidator:
    """
    Validates QR scan data and prevents repeated
    submissions within a configurable time window.
    """

    def __init__(self, debounce_seconds: float = 1.8):
        self.debounce_seconds = debounce_seconds

        # Stores the last scan time for each payload-answer pair.
        self.last_scans = {}

    @staticmethod
    def validate_payload(payload: Optional[str]) -> bool:
        """
        Check whether the QR payload has the correct format.
        Expected format: ROTQR:<random_token>
        """
        if not isinstance(payload, str):
            return False

        if not payload.startswith("ROTQR:"):
            return False

        token = payload[len("ROTQR:"):].strip()

        return bool(token)

    @staticmethod
    def validate_answer(answer: Optional[str]) -> bool:
        """
        Only A, B, C and D are accepted.
        """
        if not isinstance(answer, str):
            return False

        return answer.strip().upper() in {"A", "B", "C", "D"}

    def is_duplicate(self, payload: str, answer: str) -> bool:
        """
        Ignore the same payload-answer combination
        scanned within the debounce time window.
        """
        current_time = time.monotonic()

        key = (payload, answer.upper())

        last_time = self.last_scans.get(key)

        if last_time is not None:
            elapsed = current_time - last_time

            if elapsed < self.debounce_seconds:
                return True

        self.last_scans[key] = current_time

        return False

    def validate_scan(self, payload: Optional[str],
                      answer: Optional[str]) -> dict:
        """
        Perform complete scan validation.

        Returns:
            valid: Whether the scan is valid.
            status: Validation result.
            payload: Original QR payload.
            answer: Normalized answer.
        """

        if not self.validate_payload(payload):
            return {
                "valid": False,
                "status": "invalid_payload"
            }

        if not self.validate_answer(answer):
            return {
                "valid": False,
                "status": "invalid_answer"
            }

        normalized_answer = answer.strip().upper()

        if self.is_duplicate(payload, normalized_answer):
            return {
                "valid": False,
                "status": "duplicate"
            }

        return {
            "valid": True,
            "status": "valid",
            "payload": payload,
            "answer": normalized_answer
        }

    def clear_history(self):
        """
        Clear temporary debounce history.
        """
        self.last_scans.clear()
