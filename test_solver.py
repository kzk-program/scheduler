import os
from src.solver import solver, similar_name
from src.constraint import Constraints, Constraint
from src.target import Target

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "data", "sample.csv")
result_dir = os.path.join(current_dir, "result", "sample")
os.makedirs(result_dir, exist_ok=True)
column_band_name = 2
columns_possible_schedules = list(range(9, 14))
columns_members = list(range(3, 8))
columns_info = [2, 1, 3, 4, 5, 6, 7, 14]

for member1, member2 in similar_name(data_path, column_band_name, columns_possible_schedules, columns_members, columns_info):
    print(
        f"{member1}と{member2}は似た名前です。無視して別人として続けますか？(y/n)"
    )
    answer = input()
    if answer == "y":
        continue
    else:
        exit()
        
constraints = Constraints()
constraints.add(Constraint.ONE_BAND_PER_SCHEDULE, {})
constraints.add(Constraint.ONE_POSSIBLE_SCHEDULE_PER_BAND, {})
constraints.add(Constraint.CLOSE_SCHEDULE, {"gap": 1})

solver(
    data_path,
    result_dir,
    column_band_name,
    columns_possible_schedules,
    columns_members,
    columns_info,
    Target.MAXIMIZE_BAND_GAP,
    constraints,
)
