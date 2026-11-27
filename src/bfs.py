
from collections import deque
from parking_map import parking_map, start, get_available_slots

def bfs():
    parking_slots = get_available_slots()
    rows = len(parking_map)
    cols = len(parking_map[0])

    queue = deque([(start, [start])])
    visited = {start}

    directions = [
        (-1, 0),  # Len
        (1, 0),   # Xuong
        (0, -1),  # Trai
        (0, 1)    # Phai
    ]

    while queue:
        current, path = queue.popleft()
        x, y = current

        # Neu den o do xe trong
        if current in parking_slots:
            return path, current

        for dx, dy in directions:
            nx = x + dx
            ny = y + dy

            if (
                0 <= nx < rows
                and 0 <= ny < cols
                and parking_map[nx][ny] == 0
                and (nx, ny) not in visited
            ):
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return None, None



if __name__ == "__main__":
    path, destination = bfs()

    if path:
        print("Tim thay duong di!")
        print("O do xe duoc chon:", destination)
        print("Duong di:", path)
        print("So buoc di:", len(path) - 1)

        print("\n===== BAN DO DUONG DI =====")

        for i in range(len(parking_map)):
            line = ""

            for j in range(len(parking_map[0])):
                position = (i, j)

                if position == start:
                    line += " S "
                elif position == destination:
                    line += " E "
                elif position in path:
                    line += " * "
                elif parking_map[i][j] == 1:
                    line += " # "
                else:
                    line += " . "

            print(line)
    else:
        print("Khong tim thay duong di!")
