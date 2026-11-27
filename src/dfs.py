
from parking_map import parking_map, start, get_available_slots

def dfs():
    parking_slots = get_available_slots()
    rows = len(parking_map)
    cols = len(parking_map[0])

    stack = [(start, [start])]
    visited = {start}

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    while stack:
        current, path = stack.pop()
        x, y = current

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
                stack.append(((nx, ny), path + [(nx, ny)]))

    return None, None


if __name__ == "__main__":
    path, destination = dfs()

    if path:
        print("Tim thay duong di!")
        print("O do xe duoc chon:", destination)
        print("Duong di:", path)
        print("So buoc di:", len(path) - 1)
    else:
        print("Khong tim thay duong di!")
