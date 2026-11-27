import json
import os
import statistics

import cv2
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_FILE = os.path.join(BASE_DIR, "yolo11n.pt")
STATUS_FILE = os.path.join(BASE_DIR, "parking_status.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "images")

MAX_MAP_SLOTS = 12      # so o toi da dua len ban do giao dien
MIN_CARS_PER_ROW = 3    # hang it nhat 3 xe moi tin cay
GAP_RATIO = 1.6         # khoang cach > 1.6 buoc do => co o trong


def infer_slots(vehicle_boxes):
    boxes = [b for b in vehicle_boxes if b[2] > b[0] and b[3] > b[1]]
    if len(boxes) < MIN_CARS_PER_ROW:
        return []

    # Bo cac box qua nho (nhieu hoac xe bi cat)
    areas = [(b[2] - b[0]) * (b[3] - b[1]) for b in boxes]
    med_area = statistics.median(areas)
    boxes = [b for b, a in zip(boxes, areas) if a >= 0.3 * med_area]

    med_h = statistics.median(b[3] - b[1] for b in boxes)

    # Gom thanh hang theo toa do y cua tam
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in boxes:
        cy = (b[1] + b[3]) / 2
        if rows and abs(cy - statistics.mean((r[1] + r[3]) / 2 for r in rows[-1])) <= 0.6 * med_h:
            rows[-1].append(b)
        else:
            rows.append([b])

    slots = []
    for row_index, row in enumerate(rows):
        if len(row) < MIN_CARS_PER_ROW:
            continue
        row.sort(key=lambda b: (b[0] + b[2]) / 2)
        centers = [((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for b in row]
        dists = [centers[i + 1][0] - centers[i][0] for i in range(len(centers) - 1)]
        pitch = statistics.median(dists)
        if pitch <= 0:
            continue
        w = statistics.median(b[2] - b[0] for b in row)
        h = statistics.median(b[3] - b[1] for b in row)

        for i, b in enumerate(row):
            slots.append({"x": b[0], "y": b[1], "w": b[2] - b[0], "h": b[3] - b[1],
                          "status": "OCCUPIED", "row": row_index})
            if i < len(dists) and dists[i] > GAP_RATIO * pitch:
                missing = round(dists[i] / pitch) - 1
                (cx1, cy1), (cx2, cy2) = centers[i], centers[i + 1]
                for k in range(1, missing + 1):
                    t = k / (missing + 1)
                    cx, cy = cx1 + (cx2 - cx1) * t, cy1 + (cy2 - cy1) * t
                    slots.append({"x": cx - w / 2, "y": cy - h / 2, "w": w, "h": h,
                                  "status": "EMPTY", "row": row_index})

    slots.sort(key=lambda s: (s["row"], s["x"]))
    return slots


def pick_map_slots(slots):
    empties = [s for s in slots if s["status"] == "EMPTY"][:MAX_MAP_SLOTS]
    chosen = list(empties)
    if len(chosen) < MAX_MAP_SLOTS:
        rows = {s["row"] for s in empties}
        extra = [s for s in slots if s["status"] == "OCCUPIED" and (s["row"] in rows or not rows)]

        def dist(s):
            if not empties:
                return 0
            return min(abs(s["x"] - e["x"]) + abs(s["y"] - e["y"]) for e in empties)

        extra.sort(key=dist)
        chosen += extra[:MAX_MAP_SLOTS - len(chosen)]
    chosen.sort(key=lambda s: (s["row"], s["x"]))
    return chosen


def detect_parking_auto(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Khong the doc anh da chon!")
    height, width = image.shape[:2]

    model = YOLO(MODEL_FILE)
    results = model(image, conf=0.20, imgsz=1280, classes=[2, 3, 5, 7])
    vehicle_boxes = [tuple(map(float, b.xyxy[0])) for b in results[0].boxes]

    slots = infer_slots(vehicle_boxes)
    if not slots:
        raise ValueError(
            "Khong tu tim duoc cac hang do xe (can it nhat 3 xe thang hang). "
            "Hay thu anh khac hoac dung che do khoanh tay."
        )

    shown = pick_map_slots(slots)
    output = image.copy()
    for s in slots:
        x, y, w, h = int(s["x"]), int(s["y"]), int(s["w"]), int(s["h"])
        color = (0, 255, 0) if s["status"] == "EMPTY" else (0, 0, 255)
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2 if s in shown else 1)

    status = []
    for new_id, s in enumerate(shown, start=1):
        x, y = int(s["x"]), int(s["y"])
        color = (0, 255, 0) if s["status"] == "EMPTY" else (0, 0, 255)
        cv2.putText(output, str(new_id), (x + 3, y + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        status.append({"id": new_id, "status": s["status"]})

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({"parking_slots": status}, f, indent=4, ensure_ascii=False)

    empty = sum(1 for s in slots if s["status"] == "EMPTY")
    occupied = len(slots) - empty
    cv2.rectangle(output, (0, 0), (width, 65), (40, 40, 40), -1)
    cv2.putText(output, f"AUTO | EMPTY: {empty} | OCCUPIED: {occupied}", (15, 42),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "parking_result_auto.jpg")
    cv2.imwrite(out_path, output)

    return output, {
        "total": len(slots), "vehicles": len(vehicle_boxes),
        "empty": empty, "occupied": occupied,
        "warning": None, "output_path": out_path,
    }