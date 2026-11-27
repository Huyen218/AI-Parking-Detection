
from ultralytics import YOLO
import cv2
import os
from tkinter import Tk, filedialog

# 1. Mo cua so chon anh
root = Tk()
root.withdraw()

image_path = filedialog.askopenfilename(
    title="Chon anh bai do xe",
    filetypes=[
        ("Image files", "*.jpg *.jpeg *.png *.bmp")
    ]
)

root.destroy()

# Neu khong chon anh
if not image_path:
    print("Ban chua chon anh!")
    exit()

# 2. Doc anh
image = cv2.imread(image_path)

if image is None:
    print("Khong the doc anh!")
    exit()

print("Anh duoc chon:", image_path)

# 3. Tai mo hinh YOLO
print("Dang tai mo hinh YOLO...")
model = YOLO("yolo11n.pt")

# 4. Cac loai phuong tien COCO
vehicle_classes = [2, 3, 5, 7]

# 5. Nhan dien phuong tien
results = model(
    image,
    conf=0.25,
    classes=vehicle_classes
)

# 6. Dem phuong tien
vehicle_count = len(results[0].boxes)

# 7. Ve khung nhan dien
output = results[0].plot()

# 8. Hien thi so luong
cv2.putText(
    output,
    f"Vehicles: {vehicle_count}",
    (30, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)

# 9. Luu ket qua
os.makedirs("outputs/images", exist_ok=True)

output_path = os.path.join(
    "outputs/images",
    "detection_result.jpg"
)

cv2.imwrite(output_path, output)

# 10. Hien thi
cv2.imshow("Original Image", image)
cv2.imshow("AI Parking Detection", output)

print("So phuong tien:", vehicle_count)
print("Da luu ket qua:", output_path)

cv2.waitKey(0)
cv2.destroyAllWindows()
