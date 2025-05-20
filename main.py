from lib import data_prep
from lib import planner

data = data_prep.prepare_data("01")

sorted_cleanings = sorted(data["cleanings"], key=lambda x: x['start'])
sorted_workers = sorted(data["workers"], key=lambda x: x['start'])

if sorted_cleanings[0]['start'] < sorted_workers[0]['start']:
    print("impossible to schedule")


data_prep.show_data(data, "roads")
data_prep.show_data(data, "homes")
data_prep.show_data(data, "workers")
# data_prep.show_data(data, "cleanings")

print(planner.best_path(1, 4, data))

# Obecná kolize úklidů --> pokud ne ++
# pracovníků > úklidů --> vybrat nejbližšího s praovní dobou
#   Optimalizace zda se doba na trase vyplatí oproti práci mimo dobu



