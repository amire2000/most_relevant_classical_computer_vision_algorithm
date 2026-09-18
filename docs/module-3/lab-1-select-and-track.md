# Lab 1 — Select and track one object

This is the first hands-on lab for Module 3. You will select the plane in
`plane.mp4`, find Shi–Tomasi corners with `goodFeaturesToTrack`, and follow
those corners with pyramidal Lucas–Kanade optical flow.

Read [Sparse optical flow](sparse-optical-flow.md) first. Work in
[`code/lab/lab.py`](code/lab/lab.py); consult the completed
[`code/example/track_object.py`](code/example/track_object.py) reference only
after you have attempted each checkpoint.

## Learning goals

By the end of this lab, you can:

- explain why an ROI is selected before tracking;
- distinguish feature detection from feature tracking;
- describe the roles of `goodFeaturesToTrack` and
  `calcOpticalFlowPyrLK`;
- identify when a tracker needs new corners.

---

## Start with the smallest program

From the project root:

```bash
uv sync
uv run python docs/module-3/code/lab/lab.py
```

This starter only opens the video, displays frames, and exits on **Q**, **Esc**,
or end-of-file. Do not open `track_object.py` yet; that is the finished
reference.

---

## Build the tracker step by step

After each step, run `lab.py` again and confirm the checkpoint before moving
on. Add the code yourself; the collapsed clue is there only when you need it.

### Step 1 — Read and display frames

Read the `capture.read()` result as `(ok, frame)`. When `ok` is false, leave the
loop. `imshow` displays one frame and `waitKey` gives the window time to draw.

**Try it:** change the delay from `30` to `100`. What changes?

???+ tip "Clue for Step 1"
    The loop needs `if not ok: break` before calling `imshow`. Always release
    the capture and destroy windows after the loop.

### Step 2 — Select the object and use grayscale

Read the first frame before the loop, then add:

```python
box = cv2.selectROI("Select object", first, fromCenter=False)
old_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
```

**Try it:** print `box`. What do its four values represent?

???+ tip "Clue for Step 2"
    The values are `x, y, width, height`. Use `cv2.destroyWindow("Select object")`
    after the user presses Enter.

### Step 3 — Find good points in the ROI

Create a mask that is white only inside the selected rectangle, then call:

```python
import numpy as np

mask = np.zeros_like(old_gray)
x, y, width, height = map(int, box)
mask[y:y + height, x:x + width] = 255
p0 = cv2.goodFeaturesToTrack(
    old_gray, mask=mask, maxCorners=100, qualityLevel=0.01,
    minDistance=7, blockSize=7,
)
```

**Try it:** draw each point on the first frame. Select the plane, then select
only the sky. Which ROI produces more useful points?

???+ tip "Clue for Step 3"
    `p0` is normally shaped `(number_of_points, 1, 2)`. Loop over
    `p0.reshape(-1, 2)` when drawing points.

### Step 4 — Track points with Lucas–Kanade

Inside the frame loop, convert the new frame to grayscale and call:

```python
frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
p1, status, error = cv2.calcOpticalFlowPyrLK(
    old_gray, frame_gray, p0, None,
    winSize=(21, 21), maxLevel=3,
)
good_new = p1[status.ravel() == 1]
good_old = p0[status.ravel() == 1]
```

**Try it:** draw `good_new` as red dots. Do the dots stay on the plane?

???+ tip "Clue for Step 4"
    `status == 1` means OpenCV found a corresponding point. Update
    `old_gray = frame_gray` and `p0 = good_new.reshape(-1, 1, 2)` at the end
    of each iteration.

### Step 5 — Move the ROI

Calculate the typical point movement and add it to `x` and `y`:

```python
motion = good_new.reshape(-1, 2) - good_old.reshape(-1, 2)
dx, dy = np.median(motion, axis=0)
x = int(np.clip(x + dx, 0, frame.shape[1] - width))
y = int(np.clip(y + dy, 0, frame.shape[0] - height))
cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 2)
```

**Try it:** replace `median` with `mean`. Which one behaves better when one
point jumps incorrectly?

???+ tip "Clue for Step 5"
    Use the same point pairs for `good_new` and `good_old`; subtract before
    taking the median. The rectangle colour is BGR, so `(255, 0, 0)` is blue.

### Step 6 — Recover lost points

When fewer than three points survive, call `goodFeaturesToTrack` again using
the latest ROI and replace `p0`. This is the first useful recovery strategy;
later labs will compare it with RANSAC and ORB matching.

**Try it:** deliberately select a tiny or textureless ROI and observe when
re-seeding occurs.

???+ tip "Clue for Step 6"
    Guard the optical-flow call when `p0 is None`. A tracker cannot estimate
    motion without at least one input point, and three points make the median
    motion more stable.

---

## Guided hands-on checkpoints

### Checkpoint 1 — Select a useful ROI

Run the demo three times and select:

1. the plane tightly;
2. the plane with some surrounding sky;
3. only a nearly textureless part of the sky.

Record how many tracks appear and how long the rectangle remains useful. A
good ROI contains corners or texture that moves with the object.

### Checkpoint 2 — Inspect feature detection

In [`code/example/track_object.py`](code/example/track_object.py), temporarily print the number of points returned by
`feature_points`. Compare the tight plane ROI with the sky-only ROI. Restore the
script after observing the difference.

Question to answer: why does a large uniform sky region provide poor tracking
features?

### Checkpoint 3 — Observe optical flow

Change the selected ROI size and observe the result. The tracker does not
recognize the plane semantically; it estimates how selected image points move
between consecutive frames.

### Checkpoint 4 — Force track loss

Select a very small ROI or one with few visible details. Observe when the
script re-seeds corners. Explain why re-detection is needed instead of calling
Lucas–Kanade forever with an empty point set.

---

## Quiz

<form class="quiz" data-answer="b" data-explanation="It returns corners that are likely to be stable to track, using Shi–Tomasi scoring.">
  <fieldset>
    <legend>1. What does <code>goodFeaturesToTrack</code> return?</legend>
    <label><input type="radio" name="lab1-q1" value="a"> Every pixel in the ROI</label><br>
    <label><input type="radio" name="lab1-q1" value="b"> Trackable corner points</label><br>
    <label><input type="radio" name="lab1-q1" value="c"> A complete object mask</label>
  </fieldset>
  <button type="button" class="quiz-check">Check answer</button>
  <p class="quiz-result" aria-live="polite"></p>
</form>

<form class="quiz" data-answer="a" data-explanation="Lucas–Kanade estimates where the supplied points moved in the next frame.">
  <fieldset>
    <legend>2. What does <code>calcOpticalFlowPyrLK</code> estimate?</legend>
    <label><input type="radio" name="lab1-q2" value="a"> New positions of known points</label><br>
    <label><input type="radio" name="lab1-q2" value="b"> The colour of each pixel</label><br>
    <label><input type="radio" name="lab1-q2" value="c"> The object’s class label</label>
  </fieldset>
  <button type="button" class="quiz-check">Check answer</button>
  <p class="quiz-result" aria-live="polite"></p>
</form>

<form class="quiz" data-answer="c" data-explanation="This lesson uses intensity gradients, so grayscale is sufficient and cheaper than tracking colour channels.">
  <fieldset>
    <legend>3. Why convert frames to grayscale?</legend>
    <label><input type="radio" name="lab1-q3" value="a"> To make the video shorter</label><br>
    <label><input type="radio" name="lab1-q3" value="b"> To detect the object’s name</label><br>
    <label><input type="radio" name="lab1-q3" value="c"> Optical flow uses image intensity gradients</label>
  </fieldset>
  <button type="button" class="quiz-check">Check answer</button>
  <p class="quiz-result" aria-live="polite"></p>
</form>

<form class="quiz" data-answer="b" data-explanation="The median is less affected by a few incorrectly tracked points than the mean.">
  <fieldset>
    <legend>4. Why use median point displacement?</legend>
    <label><input type="radio" name="lab1-q4" value="a"> It detects corners</label><br>
    <label><input type="radio" name="lab1-q4" value="b"> It reduces the effect of outliers</label><br>
    <label><input type="radio" name="lab1-q4" value="c"> It increases video resolution</label>
  </fieldset>
  <button type="button" class="quiz-check">Check answer</button>
  <p class="quiz-result" aria-live="polite"></p>
</form>

<form class="quiz" data-answer="a" data-explanation="The tracker depends on visible texture and does not yet use stronger recovery methods such as RANSAC, ORB, or Kalman filtering.">
  <fieldset>
    <legend>5. Why can this tracker lose the plane?</legend>
    <label><input type="radio" name="lab1-q5" value="a"> Too few reliable visible features remain</label><br>
    <label><input type="radio" name="lab1-q5" value="b"> The video has no frames</label><br>
    <label><input type="radio" name="lab1-q5" value="c"> Grayscale prevents all motion tracking</label>
  </fieldset>
  <button type="button" class="quiz-check">Check answer</button>
  <p class="quiz-result" aria-live="polite"></p>
</form>

---

## AI tips for faster learning

Use AI as a questioning partner, not as a replacement for running the lab.
Try one prompt at a time and verify the answer in the video or source code:

- “Explain `goodFeaturesToTrack` using the plane ROI as an example. Use no
  equations.”
- “Predict what will happen if I select only the sky, then explain why.”
- “Ask me five Socratic questions about the difference between detecting and
  tracking a point. Do not give the answers first.”
- “Review my explanation of `calcOpticalFlowPyrLK`; point out one incorrect
  claim and one missing idea.”
- “Suggest one parameter change that could help fast motion, and tell me what
  trade-off to observe.”

When asking AI about a failure, include the exact traceback, the selected ROI
description, and the smallest relevant code fragment. Ask for a hypothesis
and a test before asking for a fix.

---

## Completion checklist

- [ ] I can select the plane and run the tracker.
- [ ] I compared a textured ROI with a textureless ROI.
- [ ] I can explain detection versus tracking.
- [ ] I answered the five quiz questions.
- [ ] I can name one reason tracks are lost.
