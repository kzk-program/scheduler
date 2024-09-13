import os
import csv
import pulp
from manager import MemberBandManager
from csv_parser import bands_parser
from constraint import (
    one_band_per_schedule,
    one_possible_schedule_per_band,
    close_schedule,
    Constraint,
    Constraints,
)
from target import maxmize_band_gap, Target
from output import output_schedule, output_members_schedule
from typing import List


def solver(
    data_path: str,
    result_dir: str,
    column_band_name: int,
    columns_possible_schedules: List[int],
    columns_members: List[int],
    columns_info: List[int],
    target: Target,
    constraints: Constraints,
):
    """タイスケ組みをする

    Args:
        data_path (str): _description_
        result_dir (str): _description_
        column_band_name (int): _description_
        columns_possible_schedules (List[int]): _description_
        columns_members (List[int]): _description_
        columns_info (List[int]): _description_
        target (Target): _description_
        constraints (Constraints): _description_

    Output:
        None (全て出力はファイルに書き込む)
    """
    mb_manager = MemberBandManager()
    bands_parser(
        data_path,
        mb_manager,
        column_band_name,
        columns_possible_schedules,
        columns_members,
        columns_info,
    )

    prob = pulp.LpProblem("Scheduling1", pulp.LpMinimize)
    # choicesはscheduleとbandの組になっており、そのscheduleにそのbandが入る場合は1, そうでない場合は0の値を取る。
    choices = pulp.LpVariable.dicts(
        "Choice",
        [
            (schedule, band)
            for schedule in mb_manager.schedules
            for band in mb_manager.bands
        ],
        cat="Binary",
    )

    # 制約条件を加える
    print(constraints.constraints)
    for constraint, value in constraints.constraints.items():
        if constraint == Constraint.ONE_BAND_PER_SCHEDULE:
            one_band_per_schedule(mb_manager, prob, choices)
        if constraint == Constraint.ONE_POSSIBLE_SCHEDULE_PER_BAND:
            one_possible_schedule_per_band(mb_manager, prob, choices)

        if constraint == Constraint.CLOSE_SCHEDULE:
            close_schedule(value["gap"], mb_manager, prob, choices)

    # 目的関数を設定
    if target == Target.MAXIMIZE_BAND_GAP:
        maxmize_band_gap(mb_manager, prob, choices)

    # 解く
    max_exec_minutes = 30
    print(prob.solve(pulp.PULP_CBC_CMD(60 * max_exec_minutes)))  # 1が出力されれば成功

    # 解の並べ替えを取得
    sorted_bands = []
    for schedule in mb_manager.schedules:
        for band in mb_manager.bands:
            if pulp.value(choices[schedule, band]) == 1:
                sorted_bands.append(band)

    # 並べ替え結果をCSVに出力する
    with open(os.path.join(result_dir, "sort.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([band.id for band in sorted_bands])

    # 解いた結果をCSVに出力する
    output_schedule(os.path.join(result_dir, "schedule.csv"), mb_manager, sorted_bands)
    output_members_schedule(
        os.path.join(result_dir, "members.csv"), mb_manager, sorted_bands
    )


def similar_name(data_path: str):
    mb_manager = MemberBandManager()
    bands_parser(
        data_path,
        mb_manager,
        column_band_name,
        columns_possible_schedules,
        columns_members,
        columns_info,
    )
    return mb_manager.similar_member_name()


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    data_path = os.path.join(parent_dir, "data", "sample.csv")
    result_dir = os.path.join(parent_dir, "result", "sample")
    os.makedirs(result_dir, exist_ok=True)
    constraints = Constraints()
    constraints.add(Constraint.ONE_BAND_PER_SCHEDULE, {})
    constraints.add(Constraint.ONE_POSSIBLE_SCHEDULE_PER_BAND, {})
    constraints.add(Constraint.CLOSE_SCHEDULE, {"gap": 1})
    column_band_name = 2
    columns_possible_schedules = list(range(9, 14))
    columns_members = list(range(3, 8))
    columns_info = [2, 1, 3, 4, 5, 6, 7, 14]

    for member1, member2 in similar_name(data_path):
        print(
            f"{member1}と{member2}は似た名前です。無視して別人として続けますか？(y/n)"
        )
        answer = input()
        if answer == "y":
            continue
        else:
            exit()

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
