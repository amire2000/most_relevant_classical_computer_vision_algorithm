"""Lab 4 solution: detect activity from sparse optical-flow magnitude.

Run from the repository root:
    uv run python docs/module-3/code/lab-4/activity_detection.py
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


VIDEO = Path(__file__).parents[1] / "lab-1" / "plane.mp4"
ACTIVITY_THRESHOLD = 8.0  # pixels per frame for this video


def tracks(old: np.ndarray, new: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return matching corner positions from two grayscale frames."""
    points = cv2.goodFeaturesToTrack(old, maxCorners=100, qualityLevel=0.01, minDistance=7)
    if points is None:
        return np.empty((0, 2)), np.empty((0, 2))
    moved, status, _ = cv2.calcOpticalFlowPyrLK(old, new, points, None)
    if moved is None or status is None:
        return np.empty((0, 2)), np.empty((0, 2))
    valid = status.ravel() == 1
    return points[valid].reshape(-1, 2), moved[valid].reshape(-1, 2)


def main() -> None:
    capture = cv2.VideoCapture(str(VIDEO))
    ok, previous = capture.read()
    if not ok:
        raise RuntimeError(f"Could not open {VIDEO}")
    previous_gray = cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        old, new = tracks(previous_gray, gray)

        # The median ignores one or two badly tracked corners.
        distance = np.linalg.norm(new - old, axis=1) if len(new) else np.empty(0)
        score = float(np.median(distance)) if len(distance) else 0.0
        active = score >= ACTIVITY_THRESHOLD

        for (old_x, old_y), (new_x, new_y) in zip(old.astype(int), new.astype(int)):
            cv2.line(frame, (old_x, old_y), (new_x, new_y), (0, 255, 255), 2)
            cv2.circle(frame, (new_x, new_y), 4, (0, 0, 255), -1)

        state = "ACTIVITY" if active else "quiet"
        color = (0, 0, 255) if active else (0, 255, 0)
        cv2.putText(frame, f"{state}: {score:.1f}px | Q/Esc: quit", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.imshow("Lab 4 — Motion activity detection", frame)
        if cv2.waitKey(30) & 0xFF in (ord("q"), 27):
            break
        previous_gray = gray

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
