"""Track a user-selected object with Shi-Tomasi corners and Lucas-Kanade flow."""

from pathlib import Path

import cv2
import numpy as np


VIDEO = Path(__file__).with_name("plane.mp4")
FEATURES = dict(maxCorners=200, qualityLevel=0.005, minDistance=5, blockSize=7)
LK = dict(
    winSize=(31, 31),
    maxLevel=4,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
)


def feature_points(gray: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray | None:
    x, y, width, height = box
    mask = np.zeros_like(gray)
    mask[y : y + height, x : x + width] = 255
    return cv2.goodFeaturesToTrack(gray, mask=mask, **FEATURES)


def median_motion(new: np.ndarray, old: np.ndarray) -> np.ndarray:
    return np.median(new.reshape(-1, 2) - old.reshape(-1, 2), axis=0)


def main() -> None:
    capture = cv2.VideoCapture(str(VIDEO))
    ok, first = capture.read()
    if not ok:
        raise RuntimeError(f"Could not open video: {VIDEO}")

    box = tuple(map(int, cv2.selectROI("Select object", first, fromCenter=False)))
    cv2.destroyWindow("Select object")
    if box[2] == 0 or box[3] == 0:
        raise SystemExit("No ROI selected.")

    old_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    points = feature_points(old_gray, box)
    if points is None:
        raise SystemExit("No trackable corners found in the selected ROI.")

    x, y, width, height = box
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if points is None:
            points = feature_points(gray, (x, y, width, height))
            old_gray = gray
            if points is None:
                cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 2)
                cv2.imshow("Sparse optical flow", frame)
                if cv2.waitKey(30) & 0xFF in (ord("q"), 27):
                    break
                continue
        next_points, status, _ = cv2.calcOpticalFlowPyrLK(
            old_gray, gray, points, None, **LK
        )

        if next_points is not None and status is not None:
            valid = status.ravel() == 1
            good_new = next_points[valid].reshape(-1, 2)
            good_old = points[valid].reshape(-1, 2)
        else:
            good_new = good_old = np.empty((0, 2), dtype=np.float32)

        if len(good_new) >= 3:
            motion = good_new - good_old
            center = np.median(motion, axis=0)
            distance = np.linalg.norm(motion - center, axis=1)
            inliers = distance <= max(3.0, 2.5 * np.median(distance))
            good_new, good_old = good_new[inliers], good_old[inliers]

        if len(good_new) >= 3:
            dx, dy = median_motion(good_new, good_old)
            x = int(np.clip(x + dx, 0, frame.shape[1] - width))
            y = int(np.clip(y + dy, 0, frame.shape[0] - height))
            points = good_new.reshape(-1, 1, 2).astype(np.float32)
        if len(good_new) < 8:
            # Re-seed corners inside the last known box when tracks disappear.
            new_points = feature_points(gray, (x, y, width, height))
            if new_points is not None:
                points = new_points

        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 2)
        cv2.putText(
            frame,
            f"tracks: {len(good_new)} | Q/Esc: quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.imshow("Sparse optical flow", frame)
        if cv2.waitKey(30) & 0xFF in (ord("q"), 27):
            break
        old_gray = gray

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
