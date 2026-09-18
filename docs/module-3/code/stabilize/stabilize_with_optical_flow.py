"""Lab 3.1 solution: stabilize roll with sparse optical flow and RANSAC.

Run from the repository root:
    uv run python docs/module-3/code/stabilize/stabilize_with_optical_flow.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import cv2
import numpy as np


HERE = Path(__file__).parent
DATA = HERE / "roll_imu_dataset"


def frame_paths() -> list[Path]:
    """Use camera.csv as the ordered list of frames; no IMU data is read."""
    with (DATA / "camera.csv").open(newline="") as file:
        return [DATA / row["frame_file"] for row in csv.DictReader(file)]


def flow_rotation(old: np.ndarray, new: np.ndarray) -> tuple[float | None, np.ndarray]:
    """Return camera rotation and the RANSAC-approved corner tracks."""
    mask = np.zeros_like(old)
    # ponytail: dataset text is unrotated; remove this mask for a natural video.
    mask[100:, :] = 255
    points = cv2.goodFeaturesToTrack(old, mask=mask, maxCorners=100, qualityLevel=0.01, minDistance=7)
    if points is None:
        return None, np.empty((0, 4), dtype=np.float32)
    moved, status, _ = cv2.calcOpticalFlowPyrLK(old, new, points, None)
    if moved is None or status is None:
        return None, np.empty((0, 4), dtype=np.float32)

    good_old = points[status.ravel() == 1]
    good_new = moved[status.ravel() == 1]
    if len(good_old) < 3:
        return None, np.empty((0, 4), dtype=np.float32)
    transform, inliers = cv2.estimateAffinePartial2D(good_old, good_new, method=cv2.RANSAC)
    if transform is None or inliers is None:
        return None, np.empty((0, 4), dtype=np.float32)

    # Keep only the tracks RANSAC agrees belong to the main camera motion.
    accepted_old = good_old[inliers.ravel() == 1].reshape(-1, 2)
    accepted_new = good_new[inliers.ravel() == 1].reshape(-1, 2)
    return math.atan2(transform[1, 0], transform[0, 0]), np.hstack([accepted_old, accepted_new])


def label(frame: np.ndarray, text: str) -> np.ndarray:
    """Add a centered title below the dataset's top-left roll readout."""
    result = frame.copy()
    (text_width, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    cv2.putText(result, text, ((result.shape[1] - text_width) // 2, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return result


def draw_tracks(frame: np.ndarray, tracks: np.ndarray) -> None:
    """Draw each accepted track from its old point to its new point."""
    for old_x, old_y, new_x, new_y in tracks.astype(int):
        cv2.line(frame, (old_x, old_y), (new_x, new_y), (0, 255, 255), 2)
        cv2.circle(frame, (new_x, new_y), 4, (0, 0, 255), -1)


def main() -> None:
    paths = frame_paths()
    first = cv2.imread(str(paths[0]))
    if first is None:
        raise RuntimeError(f"Could not read {paths[0]}")
    height, width = first.shape[:2]
    previous_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    camera_roll = 0.0  # The first frame is our level reference.

    for path in paths:
        frame = cv2.imread(str(path))
        if frame is None:
            raise RuntimeError(f"Could not read {path}")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        image_turn, tracks = flow_rotation(previous_gray, gray)
        if image_turn is not None:
            # The static scene rotates opposite to the camera, so reverse the sign.
            camera_roll -= image_turn

        # Rotate toward the first frame. RANSAC makes a few wrong tracks harmless.
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), -math.degrees(camera_roll), 1.0)
        stabilized = cv2.warpAffine(frame, matrix, (width, height), borderMode=cv2.BORDER_REPLICATE)
        original = label(frame, "Original")
        draw_tracks(original, tracks)
        cv2.imshow("Lab 3.1 — Optical-flow stabilization", cv2.hconcat([original, label(stabilized, "Stabilized")]))
        if cv2.waitKey(33) & 0xFF in (ord("q"), 27):
            break
        previous_gray = gray

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
