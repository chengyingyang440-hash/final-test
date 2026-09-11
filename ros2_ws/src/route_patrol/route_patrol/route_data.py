WAYPOINTS = {
    1: (0.0, 0.0),
    2: (2.0, 0.0),
    3: (4.0, 1.0),
    4: (4.0, 3.0),
    5: (2.0, 4.0),
    6: (0.0, 4.0),
    7: (-1.0, 2.0),
    8: (-1.0, 1.0),
}

RING_ORDER = [1, 4, 7, 2, 5, 8, 3, 6]

def build_route(start, end):
    if start not in WAYPOINTS or end not in WAYPOINTS:
        raise ValueError('起点和终点必须是 1～8 的路径点编号')

    route = [start]
    index = RING_ORDER.index(start)

    while route[-1] != end:
        index = (index + 1) % len(RING_ORDER)
        route.append(RING_ORDER[index])

    return route

def build_patrol_route(start):
    if start not in WAYPOINTS:
        raise ValueError('起点必须是 1～8 的路径点编号')

    route = [start]
    index = RING_ORDER.index(start)

    for _ in range(len(RING_ORDER)):
        index = (index + 1) % len(RING_ORDER)
        route.append(RING_ORDER[index])

    return route