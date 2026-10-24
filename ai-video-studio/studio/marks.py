"""Fills in Flow's small corner marks (the "Veo" text, or the sparkle) from the surrounding picture, frame by frame.

The marks sit at fixed spots on a 1080x1920 frame. Only a ~75 px patch around the mark is touched; the rest of the
frame, the audio and the composition are unchanged. Google's invisible SynthID mark is not affected.
"""
import subprocess

import cv2
import numpy as np

W, H = 1080, 1920
SPARKLE = (900, 1740, 37)  # centre x, centre y, radius
VEO_BOX = (1021, 1879, 1059, 1900)  # x0, y0, x1, y1
SAMPLES = 8


def _sparkle_mask():
    cx, cy, r = SPARKLE
    pad = 11
    size = r + pad
    ys, xs = np.mgrid[-size:size + 1, -size:size + 1]
    inside = (np.abs(xs) / size) ** 0.85 + (np.abs(ys) / size) ** 0.85 <= 1
    m = np.zeros((H, W), np.uint8)
    m[cy - size:cy + size + 1, cx - size:cx + size + 1] = inside * 255
    return cv2.dilate(m, np.ones((5, 5), np.uint8))


def _veo_mask():
    x0, y0, x1, y1 = VEO_BOX
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m


def _frames(cap, n):
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    out = []
    for k in range(n):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int((k + 0.5) * total / n))
        ok, f = cap.read()
        if ok:
            out.append(cv2.resize(f, (W, H)) if f.shape[1] != W else f)
    return out


def detect(path):
    """'sparkle', 'veo' or None. The sparkle is a pale overlay, so it is lighter than a ring just outside it;
    the text is a patch of near-white pixels."""
    cap = cv2.VideoCapture(str(path))
    frames = _frames(cap, SAMPLES)
    cap.release()
    if not frames:
        return None
    cx, cy, r = SPARKLE
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - cx, yy - cy)
    inner, ring = dist <= r * 0.5, (dist > r + 8) & (dist <= r + 24)
    lighter = 0
    for f in frames:
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if g[inner].mean() - g[ring].mean() > 6:
            lighter += 1
    if lighter >= 0.75 * len(frames):
        return "sparkle"
    x0, y0, x1, y1 = VEO_BOX
    stack = np.stack([f[y0:y1, x0:x1].min(axis=2) for f in frames])
    steady_white = (stack.min(axis=0) > 170).sum()  # bright in every sampled frame, so not moving picture content
    return "veo" if steady_white >= 15 else None


def clean(path, out_path, kind="auto"):
    """Returns the path to use: a cleaned copy, or the original if no mark is found."""
    kind = detect(path) if kind == "auto" else kind
    if kind not in ("sparkle", "veo"):
        return path
    mask = _sparkle_mask() if kind == "sparkle" else _veo_mask()
    ys, xs = np.where(mask > 0)
    y0, y1, x0, x1 = max(0, ys.min() - 20), min(H, ys.max() + 21), max(0, xs.min() - 20), min(W, xs.max() + 21)
    roi_mask = mask[y0:y1, x0:x1]

    alpha = (cv2.GaussianBlur(roi_mask, (0, 0), 3).astype(np.float32) / 255.0)[..., None]
    rng = np.random.default_rng(0)
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps),
         "-i", "-", "-i", str(path), "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "12",
         "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", str(out_path)],
        stdin=subprocess.PIPE)
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if (w, h) != (W, H):
            f = cv2.resize(f, (W, H))
        roi = f[y0:y1, x0:x1]
        filled = cv2.inpaint(roi, roi_mask, 5, cv2.INPAINT_TELEA).astype(np.float32)
        # Match the picture's own grain inside the patch, then feather the patch edge into the original.
        ring = (cv2.dilate(roi_mask, np.ones((25, 25), np.uint8)) > 0) & (roi_mask == 0)
        grey = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
        grain = float(np.std((grey - cv2.GaussianBlur(grey, (0, 0), 2))[ring])) if ring.any() else 0.0
        filled += rng.normal(0, grain, filled.shape).astype(np.float32) * (roi_mask[..., None] > 0)
        f[y0:y1, x0:x1] = np.clip(alpha * filled + (1 - alpha) * roi.astype(np.float32), 0, 255).astype(np.uint8)
        enc.stdin.write(f.tobytes())
    cap.release()
    enc.stdin.close()
    if enc.wait():
        raise RuntimeError(f"ffmpeg failed while cleaning {path}")
    return out_path
