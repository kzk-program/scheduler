import os
from src.solver import solver, similar_name
from src.constraint import Constraints, Constraint
from src.target import Target
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument(
    "--cfg", type=str, default="config/sample.yaml", help="Path to the config file"
)
args = parser.parse_args()

with open(args.cfg, "r") as f:
    config = yaml.safe_load(f)


current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = config["data_path"]
result_dir = config["result_dir"]
os.makedirs(result_dir, exist_ok=True)
column_band_name = config["column"]["band_name"]
columns_possible_schedules = config["column"]["possible_schedules"]
columns_members = config["column"]["members"]
columns_info = config["column"]["info"]

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
if config["constraint"]["close_schedule"]["active"]:
    constraints.add(Constraint.CLOSE_SCHEDULE, {"gap": config["constraint"]["close_schedule"]["gap"]})

if config["target"] == 1:
    target = Target.MAXIMIZE_BAND_GAP

solver(
    data_path,
    result_dir,
    column_band_name,
    columns_possible_schedules,
    columns_members,
    columns_info,
    target,
    constraints,
)
