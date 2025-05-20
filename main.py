from lib import data_prep
from lib import planner

"""
Předpokládám, že do pracovníkovy doby strávené prací a "od - do" se nepočítá cestování
"""
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

assigned_cleanings = []
for pc_key in possible_cleanings.keys():
    target_worker = data["workers"][data_prep.get_record(data["workers"], "worker", int(pc_key))[0]]
    target_worker_options = []
    in_work = 0
    for idx_clid, cleaning_id in enumerate(possible_cleanings[pc_key]):
        cleaning = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(cleaning_id))[0]]
        path = planner.best_path(target_worker["home"], cleaning["home"], data)

        if path["time"] == -1:
            # Path does not exist
            continue

        if in_work + cleaning["duration"] > target_worker["hours_per_day"]:
            # can somebody else?
            # if so, drop
            continue

        if idx_clid == 0:
            origin = target_worker["home"]
        else:
            origin = possible_cleanings[pc_key][idx_clid - 1]["home"]

        destination = cleaning["home"]

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
