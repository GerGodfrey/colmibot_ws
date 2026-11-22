"""Heuristic cardboard-box detector (demo).

Approach:
  1. Keep pixels whose colour looks like cardboard (brown/tan in HSV).
  2. Clean the mask and find connected blobs.
  3. Keep blobs that are large and box-shaped: they fill most of their
     rotated bounding rectangle and their outline simplifies to 4-6 corners
     (4 = one face seen head-on, 6 = a box seen at an angle).

Limitations: anything cardboard-coloured and roughly rectangular counts
(wooden tables, some skin tones, beige walls). Coordinates are pixels, not
meters. Use the "Box Controls" sliders to tune the colour range live.
"""
import cv2
import numpy as np

# -------------------- Tunable parameters --------------------
# OpenCV HSV ranges: H 0-179, S 0-255, V 0-255.
HSV_LOW = (5, 40, 60)
HSV_HIGH = (25, 220, 245)

MIN_BOX_AREA = 4000          # pixels; ignore small blobs
MIN_RECT_FILL = 0.75         # blob area / rotated-rect area
MIN_SOLIDITY = 0.85          # blob area / convex-hull area
MIN_CORNERS, MAX_CORNERS = 4, 6
MORPH_KERNEL_SIZE = 7

CONTROLS_WINDOW = "Box Controls"


def cardboard_mask(frame, hsv_low=HSV_LOW, hsv_high=HSV_HIGH):
    """Binary mask of pixels in the cardboard colour range."""
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(hsv_low), np.array(hsv_high))

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE)
    )
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # remove specks
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # fill small holes
    return mask


def find_boxes(mask):
    """Return detection dicts for box-shaped blobs in the mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_BOX_AREA:
            continue

        rotated = cv2.minAreaRect(contour)
        (rw, rh) = rotated[1]
        if rw * rh == 0:
            continue
        fill = area / (rw * rh)
        if fill < MIN_RECT_FILL:
            continue

        hull_area = cv2.contourArea(cv2.convexHull(contour))
        solidity = area / hull_area if hull_area else 0
        if solidity < MIN_SOLIDITY:
            continue

        perimeter = cv2.arcLength(contour, True)
        polygon = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if not MIN_CORNERS <= len(polygon) <= MAX_CORNERS:
            continue

        x, y, w, h = (int(v) for v in cv2.boundingRect(contour))
        moments = cv2.moments(contour)
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

        detections.append({
            "bbox": (x, y, x + w, y + h),
            "center": (cx, cy),
            "area": int(area),
            "angle": round(float(rotated[2]), 1),
            "corners": len(polygon),
            # Rough 0-1 shape score, not a calibrated probability.
            "score": round(float(min(fill, solidity)), 2),
            "outline": polygon,
            "rotated_rect": rotated,
        })

    detections.sort(key=lambda d: d["area"], reverse=True)
    return detections


def detect_boxes(frame, hsv_low=HSV_LOW, hsv_high=HSV_HIGH):
    """Return (annotated_frame, mask, detections)."""
    mask = cardboard_mask(frame, hsv_low, hsv_high)
    detections = find_boxes(mask)
    return draw_detections(frame, detections), mask, detections


def draw_detections(frame, detections):
    output = frame.copy()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cx, cy = det["center"]
        box_pts = cv2.boxPoints(det["rotated_rect"]).astype(np.int32)

        cv2.drawContours(output, [det["outline"]], -1, (255, 0, 0), 2)  # blue: outline
        cv2.drawContours(output, [box_pts], -1, (0, 255, 255), 2)        # yellow: rotated rect
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 3)        # green: bbox
        cv2.circle(output, (cx, cy), 6, (0, 0, 255), -1)                 # red: center
        cv2.putText(
            output,
            f"Box  score {det['score']:.2f}  center ({cx}, {cy})",
            (x1, max(25, y1 - 12)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
        )

    cv2.putText(
        output, f"Possible boxes: {len(detections)}", (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
    )
    return output


# -------------------- Live demo with tuning sliders --------------------
def create_controls():
    cv2.namedWindow(CONTROLS_WINDOW)
    for name, value, maximum in [
        ("H low", HSV_LOW[0], 179), ("H high", HSV_HIGH[0], 179),
        ("S low", HSV_LOW[1], 255), ("S high", HSV_HIGH[1], 255),
        ("V low", HSV_LOW[2], 255), ("V high", HSV_HIGH[2], 255),
    ]:
        cv2.createTrackbar(name, CONTROLS_WINDOW, value, maximum, lambda _: None)


def read_controls():
    get = lambda name: cv2.getTrackbarPos(name, CONTROLS_WINDOW)
    low = (get("H low"), get("S low"), get("V low"))
    high = (get("H high"), get("S high"), get("V high"))
    return low, high


_last_count = None


def process_frame(frame):
    global _last_count
    low, high = read_controls()
    annotated, mask, detections = detect_boxes(frame, low, high)

    # Print to the terminal only when the number of boxes changes.
    if len(detections) != _last_count:
        _last_count = len(detections)
        summary = [(d["center"], d["score"]) for d in detections]
        print(f"{len(detections)} box(es): {summary}")

    return {"Box Detection": annotated, "Cardboard Mask": mask}


if __name__ == "__main__":
    from camera import run_live

    create_controls()
    print("Sliders in 'Box Controls' set the HSV colour range. Press q to quit.")
    print(f"Defaults: low={HSV_LOW} high={HSV_HIGH}")
    run_live(process_frame)
