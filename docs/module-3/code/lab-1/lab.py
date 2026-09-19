"""Beginner starter for Lab 1. Extend this file one step at a time."""

from pathlib import Path

import cv2


VIDEO = Path(__file__).with_name("plane.mp4")


def main() -> None:
    capture = cv2.VideoCapture(str(VIDEO))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {VIDEO}")

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        cv2.imshow("Lab 1", frame)
        if cv2.waitKey(30) & 0xFF in (ord("q"), 27):
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
