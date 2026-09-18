"""Reference: stabilize roll by fusing sparse optical flow and IMU samples.

Run from the repository root:
    uv run python docs/module-3/code/stabilize/stabilize_with_fusion.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import cv2
import numpy as np


HERE = Path(__file__).parent
DATA = HERE / "roll_imu_dataset"
FRAMES = DATA / "frames"
IMU = DATA / "imu.csv"
OUTPUT = HERE / "stabilized_fused.mp4"
# The synthetic IMU is clean, so trust it more than the small optical-flow drift.
VISION_WEIGHT = 0.2


def read_imu() -> list[tuple[int, float]]:
    """Return (time in ns, roll rate in rad/s) for each IMU sample."""
    with IMU.open(newline="") as file:
        return [(int(row["timestamp_ns"]), float(row["gx_rad_s"])) for row in csv.DictReader(file)]


def flow_rotation(old: np.ndarray, new: np.ndarray) -> float | None:
    """Estimate image rotation from tracked corners; None means no safe estimate."""
    points = cv2.goodFeaturesToTrack(old, maxCorners=100, qualityLevel=0.01, minDistance=7)
    if points is None:
        return None

    moved, status, _ = cv2.calcOpticalFlowPyrLK(old, new, points, None)
    if moved is None or status is None:
        return None
    good_old = points[status.ravel() == 1]
    good_new = moved[status.ravel() == 1]
    if len(good_old) < 3:
        return None

    # RANSAC ignores a few bad tracks. The affine matrix tells us the image rotation.
    matrix, _ = cv2.estimateAffinePartial2D(good_old, good_new, method=cv2.RANSAC)
    if matrix is None:
        return None
    return math.atan2(matrix[1, 0], matrix[0, 0])


def labeled(frame: np.ndarray, text: str) -> np.ndarray:
    """Copy a frame and label it so the output video is easy to compare."""
    result = frame.copy()
    (text_width, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    # Center the label below the dataset's roll readout in the top-left corner.
    cv2.putText(result, text, ((result.shape[1] - text_width) // 2, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return result


def main() -> None:
    paths = sorted(FRAMES.glob("frame_*.png"))
    imu = read_imu()
    if len(paths) != len(imu):
        raise RuntimeError("Each frame needs one matching IMU row.")

    first = cv2.imread(str(paths[0]))
    if first is None:
        raise RuntimeError(f"Could not read {paths[0]}")
    height, width = first.shape[:2]
    fps = 1_000_000_000 / (imu[1][0] - imu[0][0])
    writer = cv2.VideoWriter(str(OUTPUT), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width * 2, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create {OUTPUT}")

    # At the first frame, both estimates say the camera is level.
    previous_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    imu_roll = vision_roll = 0.0
    writer.write(cv2.hconcat([labeled(first, "Original"), labeled(first, "Stabilized")]))

    for index, path in enumerate(paths[1:], start=1):
        frame = cv2.imread(str(path))
        if frame is None:
            raise RuntimeError(f"Could not read {path}")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Gyro rate × time gives camera roll. Trapezoids are accurate enough here.
        dt = (imu[index][0] - imu[index - 1][0]) / 1_000_000_000
        imu_roll += dt * (imu[index - 1][1] + imu[index][1]) / 2

        image_turn = flow_rotation(previous_gray, gray)
        if image_turn is not None:
            # The static scene turns opposite to the camera, so reverse its sign.
            vision_roll -= image_turn

        # Both sensors measure roll. Use vision as a small correction to the IMU.
        roll = (1 - VISION_WEIGHT) * imu_roll + VISION_WEIGHT * vision_roll
        center = (width / 2, height / 2)
        # The scene tilts opposite to camera roll, so rotate the frame back by -roll.
        rotate_back = cv2.getRotationMatrix2D(center, -math.degrees(roll), 1.0)
        stabilized = cv2.warpAffine(frame, rotate_back, (width, height), borderMode=cv2.BORDER_REPLICATE)
        # Put both views in one frame: original on the left, corrected on the right.
        writer.write(cv2.hconcat([labeled(frame, "Original"), labeled(stabilized, "Stabilized")]))
        previous_gray = gray

    writer.release()
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
