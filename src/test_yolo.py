from ultralytics import YOLO

print("Dang tai mo hinh YOLO...")

model = YOLO("yolo11n.pt")

print("Tai mo hinh thanh cong!")

vehicle_classes = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

for class_id, class_name in vehicle_classes.items():
    print(f"{class_id}: {class_name}")

print("YOLO READY!")