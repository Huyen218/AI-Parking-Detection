# AI Parking Detection

Hệ thống nhận diện ô đỗ xe trống từ ảnh bãi đỗ bằng **YOLO11**, sau đó dùng các thuật toán tìm kiếm **BFS, DFS, UCS, A\*** để tìm đường từ lối vào đến ô trống gần nhất. Chương trình có giao diện **Tkinter** và có phần benchmark để so sánh hiệu năng bốn thuật toán.

## Mục lục

1. [Giới thiệu](#1-giới-thiệu)
2. [Tính năng](#2-tính-năng)
3. [Công nghệ](#3-công-nghệ)
4. [Cấu trúc dự án](#4-cấu-trúc-dự-án)
5. [Cài đặt](#5-cài-đặt)
6. [Hướng dẫn sử dụng](#6-hướng-dẫn-sử-dụng)
7. [Nguyên lý hoạt động](#7-nguyên-lý-hoạt-động)
8. [Kết quả benchmark](#8-kết-quả-benchmark)
9. [Hạn chế và hướng phát triển](#9-hạn-chế-và-hướng-phát-triển)

## 1. Giới thiệu

Tìm chỗ đỗ xe trong bãi lớn thường mất thời gian. Dự án giải quyết bài toán theo hai bước:

1. **Nhận diện**: dùng YOLO11 phát hiện xe trong ảnh bãi đỗ, từ đó xác định ô nào còn trống, ô nào đã có xe.
2. **Tìm đường**: chuyển trạng thái các ô thành bản đồ dạng lưới, rồi dùng các thuật toán tìm kiếm trong môn Trí tuệ nhân tạo để tìm đường ngắn nhất từ lối vào đến một ô trống.

## 2. Tính năng

- Nhận diện phương tiện (ô tô, xe máy, xe buýt, xe tải) bằng YOLO11.
- Hai chế độ xác định ô đỗ:
  - **Thủ công**: người dùng khoanh từng ô đỗ bằng chuột trên ảnh.
  - **Tự động**: chương trình tự suy ra các hàng đỗ và các ô trống từ vị trí các xe, không cần khoanh.
- Hiển thị ảnh kết quả với ô xanh (trống) và ô đỏ (có xe), kèm thống kê số ô trống, ô có xe và số phương tiện.
- Tạo bản đồ lưới từ trạng thái ô đỗ và vẽ đường đi tìm được trên giao diện.
- Chọn thuật toán BFS, DFS, UCS hoặc A\* để tìm chỗ đỗ.
- So sánh nhanh 4 thuật toán ngay trên giao diện, và benchmark chi tiết bằng `benchmark.py` (xuất CSV và biểu đồ).

## 3. Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python |
| Nhận diện vật thể | YOLO11 (Ultralytics), mô hình pretrained trên COCO |
| Xử lý ảnh | OpenCV, NumPy, Pillow |
| Giao diện | Tkinter |
| Phân tích và biểu đồ | Pandas, Matplotlib |

## 4. Cấu trúc dự án

```
AI-Parking-Detection/
├── data/
│   └── parking_01.png          # ảnh mẫu
├── outputs/
│   └── images/                 # ảnh kết quả nhận diện
├── src/
│   ├── main.py                 # giao diện chương trình (Tkinter)
│   ├── detect_parking.py       # nhận diện xe, phân loại ô đỗ (chế độ khoanh tay)
│   ├── auto_slots.py           # tự suy ra hàng đỗ và ô trống (chế độ tự động)
│   ├── parking_map.py          # tạo bản đồ lưới từ trạng thái ô đỗ
│   ├── bfs.py                  # tìm kiếm theo chiều rộng
│   ├── dfs.py                  # tìm kiếm theo chiều sâu
│   ├── ucs.py                  # tìm kiếm chi phí đồng nhất
│   ├── astar.py                # A* với heuristic Manhattan
│   ├── benchmark.py            # so sánh 4 thuật toán trên bản đồ ngẫu nhiên
│   ├── benchmark_results.csv   # kết quả từng lần chạy
│   ├── benchmark_summary.csv   # kết quả trung bình theo kịch bản
│   ├── benchmark_chart.png     # biểu đồ so sánh
│   ├── mark_slots.py           # công cụ khoanh ô đỗ độc lập (OpenCV)
│   ├── detect_image.py         # nhận diện xe trên một ảnh (chạy thử)
│   └── test_yolo.py            # kiểm tra YOLO hoạt động
├── parking_slots.json          # toạ độ các ô đỗ đã khoanh
├── parking_status.json         # trạng thái ô đỗ (EMPTY / OCCUPIED)
├── yolo11n.pt                  # mô hình YOLO11 nano (chế độ khoanh tay)
├── yolo11m.pt                  # mô hình YOLO11 medium (chế độ tự động)
└── requirements.txt
```

## 5. Cài đặt

```bash
git clone https://github.com/Huyen218/AI-Parking-Detection.git
cd AI-Parking-Detection

# (khuyến nghị) tạo môi trường ảo
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

Tkinter đi kèm bản cài đặt Python chuẩn. Trên một số bản Linux cần cài thêm gói `python3-tk`.

## 6. Hướng dẫn sử dụng

```bash
cd src
python main.py
```

**Chế độ khoanh tay**

1. Bấm **1. CHON ANH** và chọn ảnh bãi đỗ.
2. Kéo chuột từ góc trên trái đến góc dưới phải để khoanh từng ô đỗ. Bấm **XOA O DA KHOANH** nếu muốn làm lại.
3. Bấm **2. LUU O DO** để lưu toạ độ vào `parking_slots.json`.
4. Bấm **3. NHAN DIEN YOLO** để nhận diện xe và phân loại ô trống hoặc có xe.

**Chế độ tự động**

1. Bấm **1. CHON ANH**.
2. Bấm **3B. TU DONG (KHONG KHOANH)**. Chương trình tự tìm các hàng đỗ và các ô trống.

**Tìm đường**

1. Chọn thuật toán trong ô **Thuat toan**.
2. Bấm **TIM CHO DO XE** để xem đường đi từ lối vào đến ô trống trên bản đồ.
3. Bấm **SO SANH 4 THUAT TOAN** để xem bảng so sánh số bước và thời gian chạy.

**Chạy benchmark riêng**

```bash
cd src
python benchmark.py
```

Lệnh này ghi `benchmark_results.csv`, `benchmark_summary.csv` và `benchmark_chart.png` vào thư mục `src/`.

## 7. Nguyên lý hoạt động

### 7.1 Nhận diện xe

YOLO11 chạy với ngưỡng tin cậy `conf = 0.20` và `imgsz = 1280`, chỉ giữ các lớp phương tiện của COCO: ô tô (2), xe máy (3), xe buýt (5), xe tải (7). Ngưỡng thấp và ảnh đầu vào lớn giúp phát hiện được các xe nhỏ, ở xa camera.

### 7.2 Xác định ô trống

**Chế độ khoanh tay** (`detect_parking.py`): một ô được coi là *có xe* nếu tâm của bounding box một xe nằm trong hình chữ nhật của ô. Ngược lại ô là *trống*. Kết quả ghi vào `parking_status.json`.

**Chế độ tự động** (`auto_slots.py`), dùng `yolo11m.pt` cho độ chính xác cao hơn:

1. Loại các box quá nhỏ (nhỏ hơn 30% diện tích trung vị).
2. Gom các xe thành hàng theo toạ độ y của tâm.
3. Với mỗi hàng có ít nhất 3 xe, ước lượng khoảng cách giữa hai xe liền nhau (trung vị). Nếu một khoảng cách lớn hơn 1,8 lần khoảng cách này thì suy ra có ô trống ở giữa.
4. Loại các ô trống suy ra mà chồng lên xe thật quá 25% diện tích.
5. Loại các ô trống mà vùng ảnh có nhiều chi tiết như một chiếc xe (dùng Canny, ngưỡng 60% so với mật độ cạnh của xe thật), để tránh trường hợp YOLO bỏ sót xe.
6. Chọn tối đa 6 ô đưa lên bản đồ để không tràn giao diện.

### 7.3 Bản đồ và tìm đường

`parking_map.py` tạo lưới 5 cột. Số hàng là `max(5, số ô đỗ + 1)`. Điểm bắt đầu là `(0, 0)`, mỗi ô đỗ nằm ở cột cuối cùng. Ô có xe là chướng ngại (`1`), ô trống là đích (`0`), đường đi là các ô `0`. Mỗi bước di chuyển (lên, xuống, trái, phải) có chi phí bằng 1.

| Thuật toán | Cấu trúc dữ liệu | Đặc điểm |
|---|---|---|
| BFS | Hàng đợi | Tìm được đường ngắn nhất, duyệt nhiều nút |
| DFS | Ngăn xếp | Nhanh nhưng đường đi không tối ưu |
| UCS | Hàng đợi ưu tiên theo g(n) | Tối ưu, tương đương BFS khi chi phí đều bằng 1 |
| A\* | Hàng đợi ưu tiên theo f(n) = g(n) + h(n) | Tối ưu, h là khoảng cách Manhattan đến ô trống gần nhất |

## 8. Kết quả benchmark

`benchmark.py` chạy 4 thuật toán trên 6 kịch bản bản đồ ngẫu nhiên, mỗi kịch bản 20 bản đồ (seed 0 đến 19), mỗi bản đồ có 3 ô đích. Bảng dưới là giá trị trung bình trên các bản đồ có đường đi.

| Kịch bản | Thuật toán | Số bản đồ giải được | Độ dài đường đi | Số nút mở rộng | Thời gian (ms) |
|---|---|---|---|---|---|
| 20x20, 20% vật cản | BFS | 19 | 27,00 | 247,47 | 0,15 |
| | DFS | 19 | 34,74 | 64,74 | 0,04 |
| | UCS | 19 | 27,00 | 237,79 | 0,20 |
| | A\* | 19 | 27,00 | 95,00 | 0,14 |
| 50x50, 25% vật cản | BFS | 19 | 70,32 | 1447,89 | 0,87 |
| | DFS | 19 | 128,79 | 327,26 | 0,23 |
| | UCS | 19 | 70,32 | 1424,05 | 1,32 |
| | A\* | 19 | 70,32 | 456,53 | 0,66 |

Toàn bộ 6 kịch bản nằm trong `src/benchmark_summary.csv`, biểu đồ nằm trong `src/benchmark_chart.png`.

**Nhận xét**

- BFS, UCS và A\* luôn cho đường đi có cùng độ dài tối ưu, vì mọi bước có chi phí bằng 1.
- A\* mở rộng ít nút hơn nhiều so với BFS và UCS (ở bản đồ 50x50 chỉ khoảng 1/3). Nhờ vậy A\* nhanh hơn BFS và UCS khi bản đồ lớn.
- DFS mở rộng ít nút nhất và chạy nhanh nhất, nhưng đường đi dài hơn tối ưu rất nhiều (128,79 so với 70,32 ở bản đồ 50x50).
- UCS chậm nhất vì phải duy trì hàng đợi ưu tiên mà không có thêm thông tin định hướng so với BFS.

## 9. Hạn chế và hướng phát triển

- Chưa đánh giá độ chính xác của YOLO (precision, recall) trên tập nhiều ảnh có nhãn.
- Chế độ khoanh tay chỉ đúng khi ảnh được chọn trùng với ảnh đã khoanh ô. Chương trình chỉ cảnh báo, chưa chặn.
- Chế độ tự động cần ít nhất 3 xe thẳng hàng trong một hàng, và có thể bỏ sót ô trống khi YOLO nhận diện thiếu xe.
- Bản đồ lưới hiện đơn giản hoá bãi đỗ thành 5 cột và tối đa vài ô, chưa phản ánh đúng bố cục thật của bãi.
- Mới xử lý ảnh tĩnh. Hướng phát triển: xử lý video hoặc camera thời gian thực, huấn luyện lại mô hình trên dữ liệu bãi đỗ riêng, mở rộng bản đồ theo bố cục thật.
