#!/usr/bin/env python3
"""Generate synchronized 30 FPS camera frames and IMU gyro data for roll.

The virtual camera rotates about its optical axis (the image X axis in this
example).  A horizontal bar drawn in the world therefore appears to rotate in
the opposite direction in the image.  This is an intentionally simple dataset
for learning gyro-based image stabilization.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("roll_imu_dataset"))
    parser.add_argument("--duration", type=float, default=5.0, help="Seconds")
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--amplitude-deg", type=float, default=20.0)
    parser.add_argument("--frequency-hz", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.duration <= 0 or args.fps <= 0:
        raise ValueError("duration and fps must be positive")

    frames_dir = args.output / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    frame_count = round(args.duration * args.fps)
    dt = 1.0 / args.fps
    amplitude_rad = math.radians(args.amplitude_deg)
    angular_frequency = 2.0 * math.pi * args.frequency_hz
    center = (args.width // 2, args.height // 2)
    bar_half_length = int(min(args.width, args.height) * 0.30)

    with (args.output / "camera.csv").open("w", newline="") as camera_file, (
        args.output / "imu.csv"
    ).open("w", newline="") as imu_file:
        camera_writer = csv.writer(camera_file)
        imu_writer = csv.writer(imu_file)
        camera_writer.writerow(["timestamp_ns", "frame_file", "roll_rad"])
        imu_writer.writerow(["timestamp_ns", "gx_rad_s", "gy_rad_s", "gz_rad_s"])

        for index in range(frame_count):
            t_s = index * dt
            timestamp_ns = round(t_s * 1_000_000_000)

            # Camera roll and ideal synchronous gyro measurement.
            roll_rad = amplitude_rad * math.sin(angular_frequency * t_s)
            gx_rad_s = amplitude_rad * angular_frequency * math.cos(angular_frequency * t_s)

            # A static world bar appears to rotate opposite to the camera roll.
            visible_angle = -roll_rad
            direction = (math.cos(visible_angle), math.sin(visible_angle))
            p1 = tuple(round(center[i] - bar_half_length * direction[i]) for i in range(2))
            p2 = tuple(round(center[i] + bar_half_length * direction[i]) for i in range(2))

            frame = Image.new("RGB", (args.width, args.height), "black")
            draw = ImageDraw.Draw(frame)
            draw.line((p1, p2), fill="white", width=8)
            for point, color in ((p1, (0, 180, 255)), (p2, (0, 255, 100)), (center, (80, 80, 255))):
                radius = 14 if point != center else 7
                draw.ellipse((point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius), fill=color)
            draw.text((20, 20), f"frame={index:03d}  roll={math.degrees(roll_rad):+.2f} deg", fill=(220, 220, 220))

            filename = f"frame_{index:04d}.png"
            frame.save(frames_dir / filename)
            camera_writer.writerow([timestamp_ns, f"frames/{filename}", f"{roll_rad:.12f}"])
            imu_writer.writerow([timestamp_ns, f"{gx_rad_s:.12f}", "0.0", "0.0"])

    print(f"Generated {frame_count} synchronized frames at {args.fps:g} FPS in {args.output}")
    print("camera.csv contains frame timestamps; imu.csv contains gx roll-rate samples.")


if __name__ == "__main__":
    main()
