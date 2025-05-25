import math
import time
from typing import overload

import penalties
from lib import data_prep
from lib import planner

"""
Předpokládám, že do pracovníkovy doby strávené prací a "od - do" se nepočítá cestování
"""
script_start = time.time()
result = []
not_scheduled = []
fname = "02"
data = data_prep.prepare_data(f"{fname}.in")

data_prep.show_data(data, "roads")
data_prep.show_data(data, "homes")
data_prep.show_data(data, "workers")
data_prep.show_data(data, "cleanings")
print("-" * 50)

possible_cleanings = {}
for worker in data["workers"]:
    possible_cleanings[str(worker["worker"])] = []
    for cleaning in data["cleanings"]:
        if len(possible_cleanings[str(worker["worker"])]) > 0:
            prev_cleaning = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(possible_cleanings[str(worker["worker"])][-1]))[0]]
            current_cleaning = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(cleaning["cleaning"]))[0]]
            if prev_cleaning["end"] != current_cleaning["start"]:
                possible_cleanings[str(worker["worker"])].append(cleaning["cleaning"])
        else:
            possible_cleanings[str(worker["worker"])].append(cleaning["cleaning"])

print(possible_cleanings)
possible_cleanings_unassigned = possible_cleanings.copy()

assigned_cleanings = []
overload_amount = 0
for pc_key in possible_cleanings.keys():
    target_worker = data["workers"][data_prep.get_record(data["workers"], "worker", int(pc_key))[0]]
    target_worker_options = []
    in_work = 0
    delay = 0
    for idx_clid, cleaning_id in enumerate(possible_cleanings[pc_key]):
        cleaning = data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(cleaning_id))[0]]

        overload_penalty = 0
        if in_work + cleaning["duration"] > target_worker['hours_per_day']:
            print(f"Overload, in work {in_work}, target_duration: {target_worker['hours_per_day']} cleaning duration {cleaning['duration']}")
            # Going overload
            overload_penalty = cleaning["duration"] * penalties.OVERLOAD_PENALTY
            print(overload_penalty)
            print("/" * 5 )

        out_of_ideal_penalty = 0
        if cleaning["start"] > target_worker["end"] or cleaning["end"] < target_worker["start"]:
            # The whole work is out of the window
            out_of_ideal_penalty = cleaning["duration"] * penalties.OUT_OF_IDEAL
        elif cleaning["start"] < target_worker["start"]:
            # Start is before the window, end after
            out_of_ideal_penalty = (target_worker["start"] - cleaning["start"]) * penalties.OUT_OF_IDEAL
        elif cleaning["start"] < target_worker["end"]:
            # End is after window, start in the window
            out_of_ideal_penalty = (cleaning["end"] - target_worker["end"]) * penalties.OUT_OF_IDEAL

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

        print("--- TIME PENALTY COUNT ---")
        journey_end = path["time"] + journey_start  # ETA
        time_reserve = cleaning["start"] - data["cleanings"][data_prep.get_record(data["cleanings"], "cleaning", int(possible_cleanings_unassigned[pc_key][idx_clid - 1]))[0]]["end"]
        total_points_earned = (math.floor(cleaning["duration"]) * penalties.HOUR_CLEANING + penalties.CLEANING_DONE)
        time_over = path["time"] + delay - time_reserve
        travel_penalty = path["time"] * penalties.TRAVEL_PENALTY
        netto_points = total_points_earned - (time_over * penalties.ARRIVE_LATE) - travel_penalty - overload_penalty - out_of_ideal_penalty
        print("-" * 20)

        if netto_points < 0 < len(planner.can_do_it_someone_else(possible_cleanings, pc_key, cleaning_id)):
            print(f"Appending {cleaning_id} to not scheduled; netto points: {netto_points} < 0")
            # TODO: Count cumulative delay
            other_options = planner.can_do_it_someone_else(possible_cleanings_unassigned, pc_key, cleaning_id)
            # other_options_prev = planner.can_do_it_someone_else(possible_cleanings_unassigned, pc_key, int(possible_cleanings[pc_key][idx_clid - 1]))
            other_options_prev = []  # Implement later
            if len(other_options) == 0 and len(other_options_prev) == 0:
                print("Cleaning cannot be scheduled")
                not_scheduled.append(cleaning_id)

            if len(other_options) > 0:
                # Skip, try another worker ... if another worker is not available, unscheduled cleaning
                not_scheduled.append(cleaning_id)
                print(f"Appending {cleaning_id} to not scheduled")
                continue
            else:
                not_scheduled.append(cleaning_id)
                print(f"Appending {cleaning_id} to not scheduled")
                continue

        in_work += cleaning["duration"]
        delay += time_over
        print("Netto points", netto_points)
        result.append([cleaning_id, int(pc_key)])
        print(f"Assigning {cleaning_id}")
        if cleaning_id in not_scheduled:
            not_scheduled.remove(cleaning_id)
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

print("*-" * 20)
print(result)
print(set(sorted(not_scheduled)))
script_end = time.time()
print(f"Script finished in {script_end - script_start} seconds")
with open(f"output_files/{fname}.out", "w") as f:
    for row in result:
        f.write(" ".join(map(str, row)) + "\n")