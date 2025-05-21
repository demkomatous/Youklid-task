import time
from lib import data_prep
from lib import planner

"""
Předpokládám, že do pracovníkovy doby strávené prací a "od - do" se nepočítá cestování
"""
script_start = time.time()
result = []
not_scheduled = []

data = data_prep.prepare_data("01.in")

data_prep.show_data(data, "roads")
data_prep.show_data(data, "homes")
data_prep.show_data(data, "workers")
data_prep.show_data(data, "cleanings")
print("-" * 50)

# possible_workers = {}
# for cleaning in data["cleanings"]:
#     possible_workers[str(cleaning["cleaning"])] = []
#     for worker in data["workers"]:
#         if (
#                 worker["start"] <= cleaning["start"] and
#                 worker["end"] >= cleaning["end"] and
#                 worker["hours_per_day"] >= cleaning["duration"]
#         ):
#             possible_workers[str(cleaning["cleaning"])].append(worker["worker"])

possible_cleanings = {}
for worker in data["workers"]:
    possible_cleanings[str(worker["worker"])] = []
    for cleaning in data["cleanings"]:
        # Nezačíná a končí úklid před/po pracovní době
        if (
                worker["start"] <= cleaning["start"] and
                worker["end"] >= cleaning["end"] and
                worker["hours_per_day"] >= cleaning["duration"]
        ):
            possible_cleanings[str(worker["worker"])].append(cleaning["cleaning"])

print(possible_cleanings)
possible_cleanings_unassigned = possible_cleanings.copy()

assigned_cleanings = []
for pc_key in possible_cleanings.keys():
    target_worker = data["workers"][data_prep.get_record(data["workers"], "worker", int(pc_key))[0]]
    target_worker_options = []
    in_work = 0
    for idx_clid, cleaning_id in enumerate(possible_cleanings[pc_key]):
        cleaning = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(cleaning_id))[0]]

        if in_work + cleaning["duration"] > target_worker["hours_per_day"]:
            # can somebody else?
            # if so, drop
            continue

        if idx_clid == 0:
            origin = target_worker["home"]
            journey_start = 0  # Ensure he is gonna make it to work
        else:
            origin = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(possible_cleanings_unassigned[pc_key][idx_clid - 1]))[0]]["home"]
            journey_start = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(possible_cleanings_unassigned[pc_key][idx_clid - 1]))[0]]["end"]  # Now he is leaving house

        destination = cleaning["home"]

        path = planner.best_path(origin, destination, data)

        if path["time"] == -1:
            # Path does not exist
            continue

        journey_end = path["time"] + journey_start  # ETA
        if journey_end > cleaning["start"]:
            print("Worker is not gonna make it to work")
            other_options = planner.can_do_it_someone_else(possible_cleanings_unassigned, pc_key, cleaning_id)
            # other_options_prev = planner.can_do_it_someone_else(possible_cleanings_unassigned, pc_key, int(possible_cleanings[pc_key][idx_clid - 1]))
            other_options_prev = []  # Implement later
            if len(other_options) == 0 and len(other_options_prev) == 0:
                print("Cleaning cannot be scheduled")
                not_scheduled.append(pc_key)

            if len(other_options) > 0:
                # Skip, try another worker ... if another worker is not available, unscheduled cleaning
                continue
            else:
                not_scheduled.append(cleaning_id)
                continue

        in_work += cleaning["duration"]
        result.append([cleaning_id, int(pc_key)])
        possible_cleanings_unassigned = planner.remove_from_all_except(possible_cleanings_unassigned, pc_key, cleaning_id)
        print(possible_cleanings_unassigned)

        # Odkud jede?
        # Kam jede?
        # To, kam jede, jak dlouho tam bude?
        #   Když víc, než má pracovat, zahodit
        # Stihne to?
        #   Jaký má ETA?
        #   Bude mít zpoždění?
        #       Kolik bude to zpoždění stát? -- zatím se zpožděním vyhodit
        # Může úklid udělat někdo jiný?
        #   Pokud ne a nikdo nemůže udělat ani ten předchozí, nechat
        #   Co jinak zatím nevím



# for pw_key in possible_workers.keys():
#     # Kdo se tam dostane nejrychleji
#     target_cleaning = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(pw_key))[0]]
#     target_cleaning_options = []
#     for worker_id in possible_workers[pw_key]:
#         worker = data["workers"][data_prep.get_record(data["workers"], "worker", int(worker_id))[0]]
#         path = planner.best_path(worker["home"], target_cleaning["home"], data)
#
#         if path["time"] == -1:
#             # Path does not exist
#             continue
#
#         target_cleaning_options.append(
#             {
#                 "worker": worker_id,
#                 "cleaning": pw_key,
#                 "time": path["time"]
#             }
#         )
#
#     if len(target_cleaning_options) == 0:
#         print("Cleaning cannot be scheduled")
#         not_scheduled.append(pw_key)
#         continue

    # Tady mám přiřazené možné pracovníky k úklidu
    # Je potřeba vybrat toho "nejlepšího"
    #   Nejlepší je takový, který se tam dostane nejrychleji z předchozího místa a nepřekročí pracovní dobu

print("*-" * 20)
print(result)
print(not_scheduled)
script_end = time.time()
print(f"Script finished in {script_end - script_start} seconds")