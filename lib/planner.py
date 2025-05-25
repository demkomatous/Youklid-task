import heapq


def best_path(home_start: int, home_end: int, data: dict):
    """
    Finds the best path to visit homes
    :param home_start: start home id
    :param home_end: end home id
    :param data: all given data
    :return:
    """
    starting_nodes = []
    exit_nodes = []

    for dh in data["homes"]:
        if dh["home"] == home_start:
            starting_nodes.append(
                {
                    "node": dh["node"],
                    "time": dh["walk_time"]
                }
            )
        if dh["home"] == home_end:
            exit_nodes.append(
                {
                    "node": dh["node"],
                    "time": dh["walk_time"]
                }
            )

    if len(starting_nodes) == 0 or len(exit_nodes) == 0:
        raise Exception("Home has no node")

    paths = []
    for sn in starting_nodes:
        for en in exit_nodes:
            path = dijkstra(generate_edges_indirect(data["roads"]), sn["node"], en["node"])
            paths.append(
                {
                    "path": path[1],
                    "time": sn["time"] + path[0] + en["time"]
                }
            )

    return sorted(paths, key=lambda x: x['time'])[0]


def dijkstra(edges, start, end):
    """
    """
    heap = [(0, start, [])]
    visited = set()

    while heap:
        cost, node, path = heapq.heappop(heap)
        if node in visited:
            continue
        path = path + [node]
        if node == end:
            return cost, path
        visited.add(node)
        for neighbor, weight in edges.get(node, []):
            if neighbor not in visited:
                heapq.heappush(heap, (cost + weight, neighbor, path))
    return -1, []


def generate_edges_direct(roads):
    edges = {}
    for road in roads:
        u, v = road['nodes']
        duration = road['duration']
        if u not in edges:
            edges[u] = []
        edges[u].append((v, duration))

    return edges


def generate_edges_indirect(roads):
    edges = {}
    for road in roads:
        u, v = road['nodes']
        duration = road['duration']
        edges.setdefault(u, []).append((v, duration))
        edges.setdefault(v, []).append((u, duration))
    return edges


def can_do_it_someone_else(possibilities, worker, cleaning):
    """
    V1 - score on 02 = -95960.2
    :param possibilities:
    :param worker:
    :param cleaning:
    :return:
    """
    eligible_workers = []
    for other_worker, cleanings in possibilities.items():
        if other_worker == str(worker) or other_worker == worker:
            continue
        if cleaning in cleanings or str(cleaning) in cleanings:
            eligible_workers.append(int(other_worker))
    return eligible_workers


def _can_do_it_someone_else(possibilities, worker, cleaning):
    """
    V2 - score on 02 = -84700
    :param possibilities:
    :param worker:
    :param cleaning:
    :return:
    """
    eligible_workers = []
    worker_id = int(worker)
    for other_worker, cleanings in possibilities.items():
        other_id = int(other_worker)
        if other_id <= worker_id:
            continue
        if cleaning in cleanings:
            eligible_workers.append(other_id)
    return eligible_workers

def remove_from_all_except(possibilities, worker, cleaning):
    for w_id in possibilities:
        if str(w_id) == str(worker):
            continue
        if cleaning in possibilities[w_id]:
            possibilities[w_id].remove(cleaning)

    return possibilities