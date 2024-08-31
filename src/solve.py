import os
import csv
import pulp
from managers import Member, Band, Schedule, MemberBandManager
from csv_parser import bands_parser
from constraints import one_band_per_schedule, one_band_per_possible_schedule, close_schedule
from target import maxmize_band_gap
from output import output_schedule, output_members_schedule

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
data_path = os.path.join(parent_dir, "data", "sample.csv")
result_dir = os.path.join(parent_dir, "result", "sample")
os.makedirs(result_dir, exist_ok=True)


mb_manager = MemberBandManager()

column_band_name = 2
columns_possible_schedules = list(range(9,14))
columns_members = list(range(3,8))
columns_info = [2,1,3,4,5,6,7,14]

bands_parser(data_path, mb_manager, column_band_name, columns_possible_schedules, columns_members, columns_info)

# 似た名前の人がいないかチェック
for member1, member2 in mb_manager.simliar_member_name():
  print(f"{member1}と{member2}は似た名前です。無視して別人として続けますか？(y/n)")
  answer = input()
  if answer == "y":
    continue
  else:
    exit()

prob = pulp.LpProblem('Scheduling1', pulp.LpMinimize)
# choicesはscheduleとbandの組になっており、そのscheduleにそのbandが入る場合は1, そうでない場合は0の値を取る。
choices = pulp.LpVariable.dicts("Choice", [(schedule, band) for schedule in mb_manager.schedules for band in mb_manager.bands], cat="Binary")

# 制約条件を加える
one_band_per_schedule(mb_manager, prob, choices)
one_band_per_possible_schedule(mb_manager, prob, choices)
close_schedule(1, mb_manager, prob, choices)

# 目的関数を設定
maxmize_band_gap(mb_manager, prob, choices)

#解く
max_exec_minutes = 30
print(prob.solve(pulp.PULP_CBC_CMD(60 * max_exec_minutes)))  # 1が出力されれば成功

# 解の並べ替えを取得
sorted_bands = []
for schedule in mb_manager.schedules:
  for band in mb_manager.bands:
    if pulp.value(choices[schedule, band]) == 1:
      sorted_bands.append(band)

# 並べ替え結果をCSVに出力する
with open(os.path.join(result_dir, 'sort.csv'), "w", newline='') as f:
  writer = csv.writer(f)
  writer.writerow([band.id for band in sorted_bands])

# 解いた結果をCSVに出力する
output_schedule(os.path.join(result_dir, 'schedule.csv'), mb_manager, sorted_bands)
output_members_schedule(os.path.join(result_dir, 'members.csv'), mb_manager, sorted_bands)