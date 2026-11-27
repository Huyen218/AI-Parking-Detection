from ultralytics import YOLO
import cv2
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SLOT_FILE = os.path.join(BASE_DIR, "parking_slots.json")
MODEL_FILE = os.path.join(BASE_DIR, "yolo11n.pt")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "images")
STATUS_FILE = os.path.join(BASE_DIR, "parking_status.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def detect_parking(image_path):

    # Doc anh
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Khong the doc anh da chon!")

    height, width = image.shape[:2]

    # Doc cac o do da khoanh
    if not os.path.exists(SLOT_FILE):
        raise FileNotFoundError("Khong tim thay parking_slots.json!")

    with open(SLOT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    slots = data.get("parking_slots", [])

    if not slots:
        raise ValueError("Chua co o do xe nao trong parking_slots.json!")

    saved_image = data.get("image_name")
    warning = None

    if saved_image and saved_image != os.path.basename(image_path):
        warning = (
            "Anh duoc chon khong trung voi anh da khoanh o do. "
            "Ket qua co the khong chinh xac."
        )

    # Tai YOLO va nhan dien
    model = YOLO(MODEL_FILE)

    results = model(
        image,
        conf=0.20,
        imgsz=1280,
        classes=[2, 3, 5, 7]
    )

    vehicle_boxes = []

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        vehicle_boxes.append((x1, y1, x2, y2))

    # Phan loai cac o do
    output = image.copy()

    empty_count = 0
    occupied_count = 0
    parking_status = []

    for slot in slots:

        x = int(slot["x"])
        y = int(slot["y"])
        w = int(slot["w"])
        h = int(slot["h"])

        occupied = False

        for vx1, vy1, vx2, vy2 in vehicle_boxes:

            center_x = (vx1 + vx2) // 2
            center_y = (vy1 + vy2) // 2

            if (
                x <= center_x <= x + w
                and y <= center_y <= y + h
            ):
                occupied = True
                break

        if occupied:
            color = (0, 0, 255)
            label = "OCCUPIED"
            occupied_count += 1
        else:
            color = (0, 255, 0)
            label = "EMPTY"
            empty_count += 1

        parking_status.append({
            "id": slot["id"],
            "status": label
        })

        # Ve khung va nhan
        cv2.rectangle(
            output,
            (x, y),
            (x + w, y + h),
            color,
            2
        )

        cv2.putText(
            output,
            f'{slot["id"]}: {label}',
            (x, max(20, y - 7)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

    # Luu trang thai
    status_data = {
        "parking_slots": parking_status
    }

    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            status_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Hien thi thong ke tren anh
    summary = f"EMPTY: {empty_count} | OCCUPIED: {occupied_count}"

    cv2.rectangle(
        output,
        (0, 0),
        (width, 65),
        (40, 40, 40),
        -1
    )

    cv2.putText(
        output,
        summary,
        (15, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    # Luu anh ket qua
    output_path = os.path.join(
        OUTPUT_DIR,
        "parking_result.jpg"
    )

    cv2.imwrite(output_path, output)

    # Tra ket qua ve giao dien
    stats = {
        "total": len(slots),
        "vehicles": len(vehicle_boxes),
        "empty": empty_count,
        "occupied": occupied_count,
        "warning": warning,
        "output_path": output_path
    }

    return output, stats