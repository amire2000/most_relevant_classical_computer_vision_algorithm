"""Starter for Lab 3 — display the synchronized camera frames.

Run from the repository root:
    uv run python docs/module-3/code/lab-3/lab_3_imu_stabilization.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import cv2


HERE = Path(__file__).parent
DATA = HERE / "roll_imu_dataset"


def samples() -> list[tuple[Path, int, float]]:
    """Pair each camera frame with its timestamp and IMU roll rate."""
    with (DATA / "camera.csv").open(newline="") as file:
        camera = list(csv.DictReader(file))
    with (DATA / "imu.csv").open(newline="") as file:
        imu = list(csv.DictReader(file))
    if len(camera) != len(imu):
        raise RuntimeError("Each camera frame needs one IMU sample.")

    result = []
    for frame, gyro in zip(camera, imu, strict=True):
        if frame["timestamp_ns"] != gyro["timestamp_ns"]:
            raise RuntimeError("Camera and IMU timestamps do not match.")
        result.append((DATA / frame["frame_file"], int(frame["timestamp_ns"]), float(gyro["gx_rad_s"])))
    return result


def main() -> None:
    for path, _, _ in samples():
        frame = cv2.imread(str(path))
        if frame is None:
            raise RuntimeError(f"Could not read {path}")
        cv2.imshow("Lab 3 — IMU stabilization", frame)
        if cv2.waitKey(33) & 0xFF in (ord("q"), 27):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
