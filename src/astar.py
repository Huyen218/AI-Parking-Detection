
import heapq

from parking_map import parking_map, start, get_available_slots


# =================================
# 1. HAM HEURISTIC MANHATTAN
# =================================

def heuristic(position, goal):

    x1, y1 = position
    x2, y2 = goal

    return abs(x1 - x2) + abs(y1 - y2)


# =================================
# 2. THUAT TOAN A*
# =================================

def astar():

    parking_slots = get_available_slots()

    # Kiem tra khong con o do trong
    if not parking_slots:
        return None, None, None

    rows = len(parking_map)
    cols = len(parking_map[0])

    # Hang doi uu tien: (f, g, vi tri, duong di)
    priority_queue = [
        (0, 0, start, [start])
    ]

    # Chi phi tot nhat den moi vi tri
    cost_so_far = {
        start: 0
    }

    directions = [
        (-1, 0),  # Len
        (1, 0),   # Xuong
        (0, -1),  # Trai
        (0, 1)    # Phai
    ]

    while priority_queue:

        f, g, current, path = heapq.heappop(priority_queue)

        # Bo qua duong di khong con tot nhat
        if g > cost_so_far[current]:
            continue

        # Neu den o do xe trong
        if current in parking_slots:
            return path, current, g

        x, y = current

        for dx, dy in directions:

            nx = x + dx
            ny = y + dy

            if (
                0 <= nx < rows
                and 0 <= ny < cols
                and parking_map[nx][ny] == 0
            ):

                new_position = (nx, ny)
                new_g = g + 1

                if (
                    new_position not in cost_so_far
                    or new_g < cost_so_far[new_position]
                ):

                    cost_so_far[new_position] = new_g

                    # Uoc luong khoang cach den dich gan nhat
                    h = min(
                        heuristic(new_position, slot)
                        for slot in parking_slots
                    )

                    new_f = new_g + h

                    heapq.heappush(
                        priority_queue,
                        (
                            new_f,
                            new_g,
                            new_position,
                            path + [new_position]
                        )
                    )

    return None, None, None


# =================================
# 3. CHAY THU
# =================================

if __name__ == "__main__":

    path, destination, cost = astar()

    if path:

        print("Tim thay duong di!")
        print("O do xe duoc chon:", destination)
        print("Duong di:", path)
        print("Tong chi phi:", cost)
        print("So buoc di:", len(path) - 1)

    else:

        print("Khong tim thay duong di!")
