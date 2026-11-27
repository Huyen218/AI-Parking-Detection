
import json
import os
import math

# =================================
# 1. KHAI BAO DUONG DAN
# =================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_FILE = os.path.join(BASE_DIR, "parking_status.json")

# =================================
# 2. KHOI TAO BAN DO
# =================================

# 0: Duong di / o trong
# 1: Vat can / o da co xe

start = (0, 0)

parking_map = [
    [0, 0, 0, 0, 0]
]

slot_positions = {}


# =================================
# 3. DOC TRANG THAI TU YOLO
# =================================

def load_parking_status():

    if not os.path.exists(STATUS_FILE):
        print("Khong tim thay parking_status.json!")
        return {}

    with open(STATUS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    status_dict = {}

    for slot in data.get("parking_slots", []):
        status_dict[slot["id"]] = slot["status"]

    return status_dict


# =================================
# 4. TAO BAN DO THEO SO O DO
# =================================

def update_parking_map():

    global parking_map

    status_dict = load_parking_status()

    if not status_dict:
        parking_map[:] = [[0, 0, 0, 0, 0]]
        slot_positions.clear()
        print("Chua co du lieu trang thai bai do xe!")
        return []

    # So hang tu dong tang theo so o do
    number_of_slots = max(status_dict.keys())

    rows = max(5, number_of_slots + 1)
    cols = 5

    # Tao ban do moi, tat ca la duong di
    new_map = [
        [0 for _ in range(cols)]
        for _ in range(rows)
    ]

    # Xoa va tao lai vi tri cac o do
    slot_positions.clear()

    available_slots = []

    for slot_id in sorted(status_dict.keys()):

        # Moi o do nam o cot cuoi cung
        position = (slot_id, cols - 1)

        slot_positions[slot_id] = position

        x, y = position

        if status_dict[slot_id] == "OCCUPIED":
            new_map[x][y] = 1

        elif status_dict[slot_id] == "EMPTY":
            new_map[x][y] = 0
            available_slots.append(position)

        else:
            new_map[x][y] = 1

    # Cap nhat list tai cho de cac thuat toan nhan duoc ban do moi
    parking_map[:] = new_map

    return available_slots


# =================================
# 5. HIEN THI BAN DO
# =================================

def display_map():

    available_slots = update_parking_map()

    print("\n===== BAN DO BAI DO XE =====")

    for i, row in enumerate(parking_map):

        line = ""

        for j, cell in enumerate(row):

            position = (i, j)

            if position == start:
                line += " S "

            elif position in available_slots:
                line += " E "

            elif cell == 1:
                line += " # "

            else:
                line += " . "

        print(line)


# =================================
# 6. LAY DANH SACH O DO TRONG
# =================================

def get_available_slots():
    return update_parking_map()


# =================================
# 7. CHAY THU
# =================================

if __name__ == "__main__":

    available_slots = update_parking_map()

    print("Cac o do con trong:", available_slots)
    print("So luong o do:", len(slot_positions))

    display_map()
