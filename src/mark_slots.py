
import cv2
import json
import os
from tkinter import Tk, filedialog

# Chon anh bai do xe
root = Tk()
root.withdraw()

image_path = filedialog.askopenfilename(
    title="Chon anh bai do xe",
    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
)

root.destroy()

if not image_path:
    print("Ban chua chon anh!")
    exit()

image = cv2.imread(image_path)

if image is None:
    print("Khong the doc anh!")
    exit()

original = image.copy()
slots = []

drawing = False
start_x, start_y = 0, 0
current_x, current_y = 0, 0


def mouse_callback(event, x, y, flags, param):
    global drawing, start_x, start_y
    global current_x, current_y, image

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
        current_x, current_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        current_x, current_y = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        current_x, current_y = x, y

        x1 = min(start_x, current_x)
        y1 = min(start_y, current_y)
        x2 = max(start_x, current_x)
        y2 = max(start_y, current_y)

        if x2 - x1 > 5 and y2 - y1 > 5:
            slots.append({
                "id": len(slots) + 1,
                "x": x1,
                "y": y1,
                "w": x2 - x1,
                "h": y2 - y1
            })


cv2.namedWindow("Mark Parking Slots")
cv2.setMouseCallback("Mark Parking Slots", mouse_callback)

print("HUONG DAN:")
print("- Keo chuot trai de chon mot o do xe")
print("- Nhan R de xoa tat ca")
print("- Nhan S de luu")
print("- Nhan Q de thoat")

while True:
    display = original.copy()

    for slot in slots:
        x = slot["x"]
        y = slot["y"]
        w = slot["w"]
        h = slot["h"]

        cv2.rectangle(
            display,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            display,
            str(slot["id"]),
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    if drawing:
        cv2.rectangle(
            display,
            (start_x, start_y),
            (current_x, current_y),
            (0, 255, 255),
            2
        )

    cv2.putText(
        display,
        f"Parking slots: {len(slots)}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow("Mark Parking Slots", display)

    key = cv2.waitKey(20) & 0xFF

    if key == ord("r"):
        slots.clear()
        print("Da xoa tat ca o do xe!")

    elif key == ord("s"):
        data = {
            "image_name": os.path.basename(image_path),
            "parking_slots": slots
        }

        with open("parking_slots.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Da luu", len(slots), "o do xe!")
        print("File: parking_slots.json")
        break

    elif key == ord("q"):
        print("Da thoat, khong luu!")
        break

cv2.destroyAllWindows()
