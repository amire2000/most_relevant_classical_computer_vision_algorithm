# Module 3 — Sparse optical flow

This self-contained example tracks a moving object selected by the user. It
uses Shi–Tomasi corners (`cv2.goodFeaturesToTrack`) and pyramidal
Lucas–Kanade optical flow (`cv2.calcOpticalFlowPyrLK`).

## Run

From the project root:

```bash
uv sync
uv run python module_3_sparse_optical_flow/track_object.py
```

For the guided, step-by-step version, use `lab.py` and follow Lab 1 in the
course site. The finished reference remains `track_object.py`.

Drag a rectangle around the object in the first frame and press **Enter**.
Press **Q** or **Esc** to stop playback. The blue rectangle follows the median
motion of the tracked corners.

## Algorithms used

- `cv2.VideoCapture`: reads the bundled video frame by frame.
- `cv2.selectROI`: lets the user select the object in the first frame.
- `cv2.cvtColor`: converts BGR frames to grayscale for optical flow.
- `cv2.goodFeaturesToTrack`: Shi–Tomasi corner detection inside the ROI.
- `cv2.calcOpticalFlowPyrLK`: pyramidal Lucas–Kanade sparse optical flow.
- `cv2.rectangle`, `cv2.putText`, `cv2.imshow`, and `cv2.waitKey`: draw the
  current ROI, show status, and control playback.

NumPy calculates the median motion and rejects inconsistent point movements.
The demo does not yet include RANSAC, affine transforms, homographies, ORB,
BFMatcher, or a Kalman filter.

The bundled `plane.mp4` is the input video. This directory is intentionally a
small runnable lesson, not a complete tracker: it does not yet add RANSAC,
ORB-based recovery, or Kalman filtering.
