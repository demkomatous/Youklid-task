def prepare_data(file: str) -> dict:
    with (open(f"input_files/{file}", "r") as f):
        # TODO: Add replace \r

        data = f.read()
        data = data.replace("\r", "")
        data = data.split("\n\n")

    return {
        "roads": define_roads(data[0].split("\n")),
        "homes": define_homes(data[1].split("\n")),
        "workers": define_workers(data[2].split("\n")),
        "cleanings": define_cleanings(data[3].split("\n"))
    }

def define_roads(data: list[str]) -> list:
    roads = []
    for road in data:
        road_list = road.split(" ")
        if len(road_list) != 3:
            continue
        roads.append(
            {
                "nodes": [int(road_list[0]), int(road_list[1])],
                "duration": float(road_list[2])
            }
        )

    return sorted(roads, key=lambda x: x['duration'])


def define_homes(data: list[str]) -> list[dict]:
    home_2_node = []
    for home in data:
        home_list = home.split(" ")
        if len(home_list) != 3:
            continue
        home_2_node.append(
            {
                "home": int(home_list[0]),
                "node": int(home_list[1]),
                "walk_time": float(home_list[2])
            }
        )

    return home_2_node

def define_workers(data: list[str]) -> list[dict]:
    workers = []
    for worker in data:
        worker_list = worker.split(" ")
        if len(worker_list) != 7:
            continue
        workers.append(
            {
                "worker": int(worker_list[0]),
                "home": int(worker_list[1]),
                "hours_per_day": float(worker_list[2]),
                "start": float(worker_list[4]),
                "end": float(worker_list[5])
            }
        )

    return sorted(workers, key=lambda x: x['start'])

def define_cleanings(data: list[str]) -> list[dict]:
    cleanings = []
    for cleaning in data:
        cleaning_list = cleaning.split(" ")
        if len(cleaning_list) != 5:
            continue
        cleanings.append(
            {
                "cleaning": int(cleaning_list[0]),
                "home": int(cleaning_list[1]),
                "start": float(cleaning_list[2]),
                "end": float(cleaning_list[2]) + float(cleaning_list[3]),
                "duration": float(cleaning_list[3]),
                "pkg_required": bool(int(cleaning_list[4]))
            }
        )

    return sorted(cleanings, key=lambda x: x['start'])

def show_data(data: dict, idx: str) -> None:
    print(idx.upper())
    for d in data[idx]:
        print(d)
    print("-" * 20)


def get_record(data, idx_name, value):
    return [i for i, entry in enumerate(data) if entry[idx_name] == value]