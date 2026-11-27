
import heapq
from parking_map import parking_map, start, get_available_slots

def ucs():
    parking_slots = get_available_slots()
    rows = len(parking_map)
    cols = len(parking_map[0])

    # Hang doi uu tien: (chi phi, vi tri, duong di)
    priority_queue = [(0, start, [start])]
    visited = {}

    directions = [
        (-1, 0),  # Len
        (1, 0),   # Xuong
        (0, -1),  # Trai
        (0, 1)    # Phai
    ]

    while priority_queue:
        cost, current, path = heapq.heappop(priority_queue)

        if current in visited and visited[current] <= cost:
            continue

        visited[current] = cost

        # Kiem tra da den o do xe trong chua
        if current in parking_slots:
            return path, current, cost

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
                new_cost = cost + 1

                if (
                    new_position not in visited
                    or new_cost < visited[new_position]
                ):
                    heapq.heappush(
                        priority_queue,
                        (new_cost, new_position, path + [new_position])
                    )

    return None, None, None


if __name__ == "__main__":
    path, destination, cost = ucs()

    if path:
        print("Tim thay duong di!")
        print("O do xe duoc chon:", destination)
        print("Duong di:", path)
        print("Tong chi phi:", cost)
        print("So buoc di:", len(path) - 1)
    else:
        print("Khong tim thay duong di!")
