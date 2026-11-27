import time, random, heapq, csv, statistics
from collections import deque

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def neighbors(grid, pos):
    r, c = pos
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0:
            yield (nr, nc)


def rebuild(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def bfs(grid, start, goals):
    q, parent, expanded, mx = deque([start]), {start: None}, 0, 1
    while q:
        cur = q.popleft(); expanded += 1
        if cur in goals:
            p = rebuild(parent, cur); return p, len(p) - 1, expanded, mx
        for n in neighbors(grid, cur):
            if n not in parent:
                parent[n] = cur; q.append(n); mx = max(mx, len(q))
    return None, None, expanded, mx


def dfs(grid, start, goals):
    st, parent, seen, expanded, mx = [start], {start: None}, set(), 0, 1
    while st:
        cur = st.pop()
        if cur in seen:
            continue
        seen.add(cur); expanded += 1
        if cur in goals:
            p = rebuild(parent, cur); return p, len(p) - 1, expanded, mx
        for n in neighbors(grid, cur):
            if n not in seen:
                parent.setdefault(n, cur); st.append(n); mx = max(mx, len(st))
    return None, None, expanded, mx


def ucs(grid, start, goals):
    pq, parent, best, expanded, mx = [(0, start)], {start: None}, {start: 0}, 0, 1
    while pq:
        g, cur = heapq.heappop(pq)
        if g > best[cur]:
            continue
        expanded += 1
        if cur in goals:
            p = rebuild(parent, cur); return p, g, expanded, mx
        for n in neighbors(grid, cur):
            ng = g + 1
            if n not in best or ng < best[n]:
                best[n] = ng; parent[n] = cur
                heapq.heappush(pq, (ng, n)); mx = max(mx, len(pq))
    return None, None, expanded, mx


def astar(grid, start, goals):
    h = lambda p: min(abs(p[0] - g[0]) + abs(p[1] - g[1]) for g in goals)
    pq, parent, best, expanded, mx = [(h(start), 0, start)], {start: None}, {start: 0}, 0, 1
    while pq:
        f, g, cur = heapq.heappop(pq)
        if g > best[cur]:
            continue
        expanded += 1
        if cur in goals:
            p = rebuild(parent, cur); return p, g, expanded, mx
        for n in neighbors(grid, cur):
            ng = g + 1
            if n not in best or ng < best[n]:
                best[n] = ng; parent[n] = cur
                heapq.heappush(pq, (ng + h(n), ng, n)); mx = max(mx, len(pq))
    return None, None, expanded, mx


ALGOS = {"BFS": bfs, "DFS": dfs, "UCS": ucs, "A*": astar}


def make_map(size, obstacle_rate, n_goals, seed):
    rnd = random.Random(seed)
    grid = [[1 if rnd.random() < obstacle_rate else 0 for _ in range(size)] for _ in range(size)]
    grid[0][0] = 0
    goals = set()
    cells = list(range(1, size))
    rnd.shuffle(cells)
    for r in cells[:n_goals]:
        grid[r][size - 1] = 0
        goals.add((r, size - 1))
    return grid, (0, 0), goals


def main():
    scenarios = [(10, 0.0), (10, 0.2), (20, 0.2), (20, 0.3), (30, 0.25), (50, 0.25)]
    rows = []
    for size, rate in scenarios:
        for seed in range(20):
            grid, start, goals = make_map(size, rate, 3, seed)
            for name, fn in ALGOS.items():
                t = time.perf_counter()
                for _ in range(20):
                    path, cost, exp, mx = fn(grid, start, goals)
                ms = (time.perf_counter() - t) / 20 * 1000
                if path:
                    rows.append([f"{size}x{size}_obs{int(rate*100)}", seed, name, cost, exp, mx, round(ms, 4)])

    with open("benchmark_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "seed", "algorithm", "path_cost", "nodes_expanded", "max_frontier", "time_ms"])
        w.writerows(rows)

    summary = []
    for size, rate in scenarios:
        sc = f"{size}x{size}_obs{int(rate*100)}"
        for name in ALGOS:
            sel = [r for r in rows if r[0] == sc and r[2] == name]
            if sel:
                summary.append([sc, name, len(sel)] + [round(statistics.mean(r[i] for r in sel), 2) for i in (3, 4, 5, 6)])
    with open("benchmark_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "algorithm", "solved_maps", "avg_cost", "avg_expanded", "avg_frontier", "avg_time_ms"])
        w.writerows(summary)

    print(f"{'scenario':<16}{'algo':<6}{'solved':>7}{'cost':>8}{'expanded':>10}{'frontier':>10}{'ms':>9}")
    for s in summary:
        print(f"{s[0]:<16}{s[1]:<6}{s[2]:>7}{s[3]:>8}{s[4]:>10}{s[5]:>10}{s[6]:>9}")

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        scs = [f"{s}x{s}_obs{int(r*100)}" for s, r in scenarios]
        fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
        for ax, idx, title in ((axes[0], 3, "Do dai duong di trung binh"), (axes[1], 4, "So nut mo rong trung binh")):
            width = 0.2
            for i, name in enumerate(ALGOS):
                vals = [next((s[idx] for s in summary if s[0] == sc and s[1] == name), 0) for sc in scs]
                ax.bar([x + i * width for x in range(len(scs))], vals, width, label=name)
            ax.set_xticks([x + 1.5 * width for x in range(len(scs))]); ax.set_xticklabels(scs, rotation=30, ha="right")
            ax.set_title(title); ax.set_ylim(bottom=0); ax.legend()
        plt.tight_layout(); plt.savefig("benchmark_chart.png", dpi=150)
        print("Da luu benchmark_chart.png")
    except ImportError:
        print("Chua cai matplotlib: pip install matplotlib")


if __name__ == "__main__":
    main()