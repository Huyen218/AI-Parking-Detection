# AI Parking Detection

## 1. Giới thiệu
Hệ thống nhận diện ô đỗ xe trống bằng YOLO11 và OpenCV, sau đó dùng các thuật
toán tìm kiếm (BFS, DFS, UCS, A*) để tìm đường từ lối vào đến ô trống gần nhất.

## 2. Công nghệ
Python, YOLO11 (Ultralytics), OpenCV, Tkinter, NumPy, Pandas, Matplotlib, Pillow

## 3. Cấu trúc dự án
- src/main.py: giao diện chương trình
- src/detect_parking.py: nhận diện xe và xác định ô trống
- src/parking_map.py: tạo bản đồ lưới từ trạng thái ô đỗ
- src/bfs.py, dfs.py, ucs.py, astar.py: các thuật toán tìm đường
- src/benchmark.py: so sánh 4 thuật toán
- yolo11n.pt: mô hình YOLO (pretrained)

## 4. Cách chạy
pip install -r requirements.txt
cd src
python main.py

Các bước: Chọn ảnh -> Khoanh ô đỗ -> Lưu ô đỗ -> Nhận diện YOLO -> Chạy thuật toán.

## 5. Trạng thái
- [x] Nhận diện phương tiện từ ảnh
- [x] Xác định ô đỗ trống/có xe
- [x] Giao diện Tkinter
- [x] Cài đặt BFS, DFS, UCS, A*
- [x] Benchmark so sánh thuật toán
- [ ] Đánh giá độ chính xác YOLO trên nhiều ảnh

## 6. Thành viên
| Họ tên | MSSV | Công việc |
|---|---|---|
| (điền) | (điền) | (điền) |