import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import json
import time
import os

from detect_parking import detect_parking
from auto_slots import detect_parking_auto

from bfs import bfs
from dfs import dfs
from ucs import ucs
from astar import astar

from parking_map import (
    parking_map,
    start,
    get_available_slots
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOT_FILE = os.path.join(BASE_DIR, "parking_slots.json")


class ParkingApp:

    def __init__(self, root):

        self.root = root
        self.root.title("AI PARKING ROUTING")
        self.root.geometry("1250x850")
        self.root.configure(bg="#17202A")

        self.image_path = None
        self.original_image = None
        self.photo = None

        self.scale_x = 1
        self.scale_y = 1

        self.slots = []
        self.start_x = None
        self.start_y = None
        self.current_rect = None

        self.create_interface()

    # =================================
    # 1. TAO GIAO DIEN
    # =================================

    def create_interface(self):

        title = tk.Label(
            self.root,
            text="AI PARKING ROUTING",
            font=("Arial", 24, "bold"),
            bg="#17202A",
            fg="white"
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            self.root,
            text="HE THONG NHAN DIEN VA TIM KIEM CHO DO XE",
            font=("Arial", 11),
            bg="#17202A",
            fg="#AAB7B8"
        )
        subtitle.pack()

        control = tk.Frame(self.root, bg="#17202A")
        control.pack(pady=15)

        tk.Button(
            control,
            text="1. CHON ANH",
            command=self.select_image,
            bg="#2980B9",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            control,
            text="2. LUU O DO",
            command=self.save_slots,
            bg="#8E44AD",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            control,
            text="3. NHAN DIEN YOLO",
            command=self.run_detection,
            bg="#27AE60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            control,
            text="3B. TU DONG (KHONG KHOANH)",
            command=self.run_auto_detection,
            bg="#E67E22",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            control,
            text="XOA O DA KHOANH",
            command=self.clear_slots,
            bg="#C0392B",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=12,
            pady=8
        ).pack(side="left", padx=5)

        content = tk.Frame(self.root, bg="#17202A")
        content.pack(fill="both", expand=True, padx=15)

        # Khu vuc anh
        left = tk.LabelFrame(
            content,
            text=" ANH BAI DO XE - KHOANH O BANG CHUOT ",
            font=("Arial", 11, "bold"),
            bg="#17202A",
            fg="white"
        )
        left.pack(side="left", fill="both", expand=True, padx=8)

        self.canvas = tk.Canvas(
            left,
            width=540,
            height=380,
            bg="#263238",
            highlightthickness=0
        )
        self.canvas.pack(padx=8, pady=8)

        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.drawing)
        self.canvas.bind("<ButtonRelease-1>", self.finish_draw)

        tk.Label(
            left,
            text="Keo chuot tu goc tren trai den goc duoi phai de khoanh o do.",
            bg="#17202A",
            fg="#F1C40F",
            font=("Arial", 9)
        ).pack(pady=5)

        self.slot_label = tk.Label(
            left,
            text="So o da khoanh: 0",
            bg="#17202A",
            fg="white",
            font=("Arial", 11)
        )
        self.slot_label.pack(pady=5)

        # Khu vuc ban do
        right = tk.LabelFrame(
            content,
            text=" BAN DO BAI DO XE ",
            font=("Arial", 11, "bold"),
            bg="#17202A",
            fg="white"
        )
        right.pack(side="right", fill="both", expand=True, padx=8)

        self.map_frame = tk.Frame(right, bg="#17202A")
        self.map_frame.pack(expand=True, pady=15)

        self.stats_label = tk.Label(
            self.root,
            text="Hay chon anh bai do xe de bat dau",
            font=("Arial", 11),
            bg="#17202A",
            fg="#F1C40F"
        )
        self.stats_label.pack(pady=8)

        # Chon thuat toan
        algorithm_frame = tk.Frame(self.root, bg="#17202A")
        algorithm_frame.pack(pady=8)

        tk.Label(
            algorithm_frame,
            text="Thuat toan:",
            font=("Arial", 11),
            bg="#17202A",
            fg="white"
        ).pack(side="left", padx=5)

        self.algorithm = ttk.Combobox(
            algorithm_frame,
            values=["BFS", "DFS", "UCS", "A*"],
            state="readonly",
            width=12
        )
        self.algorithm.current(0)
        self.algorithm.pack(side="left", padx=5)

        tk.Button(
            algorithm_frame,
            text="TIM CHO DO XE",
            command=self.run_algorithm,
            bg="#16A085",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=7
        ).pack(side="left", padx=10)

        tk.Button(
            algorithm_frame,
            text="SO SANH 4 THUAT TOAN",
            command=self.compare_algorithms,
            bg="#D35400",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=7
        ).pack(side="left", padx=10)

        self.result_label = tk.Label(
            self.root,
            text="Ket qua tim kiem se hien thi tai day",
            font=("Arial", 11),
            bg="#17202A",
            fg="white",
            justify="left"
        )
        self.result_label.pack(pady=2)

    # =================================
    # 2. CHON ANH
    # =================================

    def select_image(self):

        path = filedialog.askopenfilename(
            title="Chon anh bai do xe",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp")
            ]
        )

        if not path:
            return

        image = cv2.imread(path)

        if image is None:
            messagebox.showerror("Loi", "Khong the doc anh!")
            return

        self.image_path = path
        self.original_image = image
        self.slots = []

        self.show_image(image)
        self.update_slot_label()

        self.stats_label.config(
            text="Da chon anh. Hay khoanh cac o do xe.",
            fg="#F1C40F"
        )

        self.result_label.config(
            text="Chua chay nhan dien."
        )

        self.draw_map()

    # =================================
    # 3. HIEN THI ANH
    # =================================

    def show_image(self, image):

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)

        original_width, original_height = pil_image.size

        pil_image.thumbnail((540, 380))

        display_width, display_height = pil_image.size

        self.scale_x = original_width / display_width
        self.scale_y = original_height / display_height

        self.photo = ImageTk.PhotoImage(pil_image)

        self.canvas.config(
            width=display_width,
            height=display_height
        )

        self.canvas.delete("all")

        self.canvas.create_image(
            0, 0,
            anchor="nw",
            image=self.photo
        )

    # =================================
    # 4. KHOANH O DO
    # =================================

    def start_draw(self, event):

        if self.original_image is None:
            return

        self.start_x = event.x
        self.start_y = event.y

        self.current_rect = self.canvas.create_rectangle(
            event.x,
            event.y,
            event.x,
            event.y,
            outline="#00FF00",
            width=2
        )

    def drawing(self, event):

        if self.current_rect is not None:

            self.canvas.coords(
                self.current_rect,
                self.start_x,
                self.start_y,
                event.x,
                event.y
            )

    def finish_draw(self, event):

        if self.current_rect is None:
            return

        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        w = x2 - x1
        h = y2 - y1

        if w < 5 or h < 5:

            self.canvas.delete(self.current_rect)
            self.current_rect = None
            return

        real_x = round(x1 * self.scale_x)
        real_y = round(y1 * self.scale_y)
        real_w = round(w * self.scale_x)
        real_h = round(h * self.scale_y)

        slot_id = len(self.slots) + 1

        self.slots.append({
            "id": slot_id,
            "x": real_x,
            "y": real_y,
            "w": real_w,
            "h": real_h
        })

        self.canvas.create_text(
            x1 + 5,
            y1 + 5,
            text=str(slot_id),
            fill="yellow",
            anchor="nw",
            font=("Arial", 12, "bold")
        )

        self.current_rect = None
        self.update_slot_label()

    def update_slot_label(self):

        self.slot_label.config(
            text=f"So o da khoanh: {len(self.slots)}"
        )

    # =================================
    # 5. XOA O DA KHOANH
    # =================================

    def clear_slots(self):

        if self.original_image is None:
            return

        self.slots = []

        self.show_image(self.original_image)
        self.update_slot_label()

    # =================================
    # 6. LUU TOA DO O DO
    # =================================

    def save_slots(self):

        if self.original_image is None:

            messagebox.showwarning(
                "Thong bao",
                "Ban chua chon anh!"
            )
            return False

        if not self.slots:

            messagebox.showwarning(
                "Thong bao",
                "Ban chua khoanh o do nao!"
            )
            return False

        data = {
            "image_name": os.path.basename(self.image_path),
            "parking_slots": self.slots
        }

        with open(SLOT_FILE, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        messagebox.showinfo(
            "Thanh cong",
            f"Da luu {len(self.slots)} o do xe!"
        )

        return True

    # =================================
    # 7. CHAY YOLO
    # =================================

    def run_detection(self):

        if self.original_image is None:

            messagebox.showwarning(
                "Thong bao",
                "Hay chon anh truoc!"
            )
            return

        if not self.slots:

            messagebox.showwarning(
                "Thong bao",
                "Hay khoanh cac o do truoc!"
            )
            return

        if not self.save_slots():
            return

        try:

            self.stats_label.config(
                text="YOLO dang nhan dien...",
                fg="#F1C40F"
            )

            self.root.update_idletasks()

            output, stats = detect_parking(self.image_path)

            self.show_image(output)

            # Ve lai cac o tren anh ket qua
            for slot in self.slots:

                x1 = round(slot["x"] / self.scale_x)
                y1 = round(slot["y"] / self.scale_y)

                x2 = round(
                    (slot["x"] + slot["w"]) / self.scale_x
                )

                y2 = round(
                    (slot["y"] + slot["h"]) / self.scale_y
                )

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="#00FF00",
                    width=2
                )

            self.stats_label.config(
                text=(
                    f"Tong o: {stats['total']}   |   "
                    f"O trong: {stats['empty']}   |   "
                    f"O co xe: {stats['occupied']}   |   "
                    f"Phuong tien: {stats['vehicles']}"
                ),
                fg="#2ECC71"
            )

            self.draw_map()

            if stats["warning"]:

                messagebox.showwarning(
                    "Canh bao",
                    stats["warning"]
                )

        except Exception as error:

            messagebox.showerror(
                "Loi nhan dien",
                str(error)
            )

    # =================================
    # 7B. TU DONG TIM O DO + NHAN DIEN
    # =================================

    def run_auto_detection(self):

        if self.original_image is None:
            messagebox.showwarning("Thong bao", "Hay chon anh truoc!")
            return

        try:
            self.stats_label.config(
                text="YOLO dang tu dong tim o do...",
                fg="#F1C40F"
            )
            self.root.update_idletasks()

            output, stats = detect_parking_auto(self.image_path)

            self.show_image(output)

            self.stats_label.config(
                text=(
                    f"Tong o: {stats['total']}   |   "
                    f"O trong: {stats['empty']}   |   "
                    f"O co xe: {stats['occupied']}   |   "
                    f"Phuong tien: {stats['vehicles']}"
                ),
                fg="#2ECC71"
            )

            self.draw_map()

        except Exception as error:
            messagebox.showerror("Loi nhan dien", str(error))

    # =================================
    # 8. VE BAN DO DONG
    # =================================

    def draw_map(self, path=None, destination=None):

        path = path or []

        available_slots = get_available_slots()

        for widget in self.map_frame.winfo_children():
            widget.destroy()

        rows = len(parking_map)

        if rows == 0:
            return

        cols = len(parking_map[0])

        cell_size = 4 if rows <= 7 else 3
        font_size = 16 if rows <= 7 else 12

        for i, row in enumerate(parking_map):

            for j, cell in enumerate(row):

                position = (i, j)

                text = "."
                color = "#ECF0F1"

                if position == start:

                    text = "S"
                    color = "#3498DB"

                elif position == destination:

                    text = "D"
                    color = "#27AE60"

                elif position in path:

                    text = "*"
                    color = "#F1C40F"

                elif position in available_slots:

                    text = "E"
                    color = "#2ECC71"

                elif cell == 1:

                    text = "#"
                    color = "#7F8C8D"

                tk.Label(
                    self.map_frame,
                    text=text,
                    font=("Arial", font_size, "bold"),
                    width=cell_size,
                    height=2,
                    bg=color,
                    fg="#17202A",
                    relief="ridge",
                    borderwidth=2
                ).grid(
                    row=i,
                    column=j,
                    padx=2,
                    pady=2
                )

    # =================================
    # 9. CHAY THUAT TOAN TIM DUONG
    # =================================

    def run_algorithm(self):

        if self.original_image is None:

            messagebox.showwarning(
                "Thong bao",
                "Hay chon anh truoc!"
            )
            return

        if not os.path.exists(SLOT_FILE):

            messagebox.showwarning(
                "Thong bao",
                "Hay luu cac o do truoc!"
            )
            return

        available_slots = get_available_slots()

        if not available_slots:

            messagebox.showwarning(
                "Thong bao",
                "Khong con o do trong!"
            )
            return

        choice = self.algorithm.get()

        try:

            if choice == "BFS":

                path, destination = bfs()
                cost = len(path) - 1 if path else None

            elif choice == "DFS":

                path, destination = dfs()
                cost = len(path) - 1 if path else None

            elif choice == "UCS":

                path, destination, cost = ucs()

            elif choice == "A*":

                path, destination, cost = astar()

            else:

                messagebox.showwarning(
                    "Thong bao",
                    "Vui long chon thuat toan!"
                )
                return

            if path:

                self.result_label.config(
                    text=(
                        f"Thuat toan: {choice}\n"
                        f"O do duoc chon: {destination}\n"
                        f"So buoc: {len(path) - 1}\n"
                        f"Tong chi phi: {cost}"
                    ),
                    fg="#2ECC71"
                )

                self.draw_map(path, destination)

            else:

                self.result_label.config(
                    text="Khong tim thay duong di!",
                    fg="#E74C3C"
                )

                self.draw_map()

        except Exception as error:

            messagebox.showerror(
                "Loi thuat toan",
                str(error)
            )

    # =================================
    # 9B. SO SANH 4 THUAT TOAN
    # =================================

    def compare_algorithms(self):

        if not get_available_slots():
            messagebox.showwarning(
                "Thong bao",
                "Khong co o do trong! Hay nhan dien YOLO truoc."
            )
            return

        lines = [
            f"{'Thuat toan':<12}{'Buoc':>6}{'Chi phi':>9}{'Thoi gian (ms)':>16}"
        ]

        for name, func in [("BFS", bfs), ("DFS", dfs), ("UCS", ucs), ("A*", astar)]:

            start_time = time.perf_counter()
            result = func()
            elapsed = (time.perf_counter() - start_time) * 1000

            path = result[0]
            steps = len(path) - 1 if path else "-"

            lines.append(
                f"{name:<12}{steps:>6}{steps:>9}{elapsed:>16.3f}"
            )

        self.result_label.config(
            text="\n".join(lines),
            fg="#2ECC71",
            font=("Courier New", 11),
            justify="left"
        )


# =================================
# 10. KHOI DONG CHUONG TRINH
# =================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ParkingApp(root)

    root.mainloop()