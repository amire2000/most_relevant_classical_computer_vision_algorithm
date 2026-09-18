# Course roadmap

**Course:** Most Relevant Classical Computer Vision Algorithms Using Python and OpenCV  
**Format:** Concept-first reading map; implementations and labs are added separately.

## Learning path

### Module 1 — Images as data

- Pixels, channels, resolution, and image coordinates
- Grayscale and colour spaces
- Histograms, contrast, and noise
- OpenCV image I/O and display concepts

### Module 2 — Image filtering, gradients, and feature detection

- Gaussian blur and scale-space intuition
- Image gradients with Sobel operators
- Canny edge detection
- Edges, texture, and why optical flow needs image gradients
- What makes a point useful for tracking
- Harris corner detection
- Shi–Tomasi corner detection
- Why Shi–Tomasi is the natural feature-selection starting point for
  Lucas–Kanade
- Choosing tracks, regions of interest, and coordinate conventions

### [Module 3 — Sparse optical flow](module-3/index.md)

The first implementation module. Follow selected points across frames and use
their motion as a compact description of what is happening in a scene.

#### Core concepts

- Good feature points and track initialization
- Lucas–Kanade optical flow and the pyramidal approach
- Forward-backward checking, lost tracks, and outliers
- Track lifecycle: create, update, reject, and re-seed
- Visualizing trajectories and interpreting motion vectors

#### Real scenarios to study

1. **Camera motion estimation** — infer pan, tilt, or handheld shake from the
   background motion.
2. **Video stabilization** — estimate unwanted camera movement and define a
   stabilized view.
3. **Object tracking** — follow a selected object without a detector running on
   every frame.
4. **Motion-based activity detection** — distinguish a mostly static scene from
   meaningful movement.
5. **Sports and human movement analysis** — summarize local motion around a
   player, tool, or body joint.
6. **Visual odometry preview** — use tracked features as the starting point for
   estimating camera displacement.

#### Reading checkpoints

- Explain when sparse flow is preferable to dense flow.
- Identify tracking failure modes and the signals that expose them.
- Choose a scenario where point tracks are sufficient and one where they are
  not.
- Describe what can be inferred from the direction, magnitude, and consistency
  of tracked motion.

#### OpenCV anchor

- Pyramidal Lucas–Kanade
- Tracking corners between frames with `cv2.calcOpticalFlowPyrLK`

### Module 4 — Robust estimation

- RANSAC for rejecting bad tracks
- Affine transforms for approximate camera motion
- Homographies for planar scenes and perspective change
- Estimating overall camera motion from surviving point correspondences

### Module 5 — Feature matching and track recovery

- ORB descriptors and binary feature representations
- `BFMatcher` and match filtering
- Recovering when optical-flow tracks break
- Revisiting a previously seen place (a visual-relocalization introduction)

### Module 6 — Filtering and estimation

- Kalman filter intuition: state, measurement, prediction, and update
- Smoothing noisy tracks
- Briefly predicting a target position while features are lost
- Choosing process and measurement assumptions for a visual tracker

### Module 7 — Dense optical flow

- Dense motion fields and their visual interpretation
- When dense flow is worth its higher cost
- Scene motion, motion boundaries, and limitations

### Module 8 — Contours and geometric vision

- Contours, shape, and connected components
- Affine and perspective transforms
- Homographies and image registration
- Camera calibration concepts

### Module 9 — Segmentation and recognition primitives

- Thresholding and region-based segmentation
- Background subtraction
- Hough transforms and classical detection patterns

### Module 10 — Integrated classical vision systems

- Selecting an algorithm from scene constraints
- Combining detection, tracking, geometry, and segmentation
- Measuring accuracy, robustness, and runtime
- Capstone scenario selection and evaluation plan

---

## Scope boundary

This page is a reading map only. It intentionally contains no Python or OpenCV
implementation. Each module can later receive its own explanation, experiment,
and reference implementation.
