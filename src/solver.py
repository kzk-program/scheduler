import os
import csv
import pulp
from .manager import MemberBandManager
from .csv_parser import bands_parser
from .constraint import (
    one_band_per_schedule,
    one_possible_schedule_per_band,
    close_schedule,
    Constraint,
    Constraints,
)
from .target import maxmize_band_gap, Target, early_finish
from .output import output_schedule, output_members_schedule
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
    elif target == Target.EARLY_FINISH:
        early_finish(mb_manager, prob, choices)

    # 解く
    max_exec_minutes = 30
    print(prob.solve(pulp.PULP_CBC_CMD(60 * max_exec_minutes)))  # 1が出力されれば成功

    # 解の並べ替えを取得
    sorted_bands = []
    for schedule in mb_manager.schedules:
        result_band = None
        for band in mb_manager.bands:
            if pulp.value(choices[schedule, band]) == 1:
                result_band = band
                break
        sorted_bands.append(result_band)

    # 並べ替え結果をCSVに出力する
    with open(os.path.join(result_dir, "sort.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([band.id if band else -1 for band in sorted_bands])

    # 解いた結果をCSVに出力する
    output_schedule(os.path.join(result_dir, "schedule.csv"), mb_manager, sorted_bands)
    output_members_schedule(
        os.path.join(result_dir, "members.csv"), mb_manager, sorted_bands
    )


def similar_name(data_path: str, columns_members: List[int]) -> List[str]:
    mb_manager = MemberBandManager()
    bands_parser(
        data_path,
        mb_manager,
        0,
        [],
        columns_members,
        [],
    )
    return mb_manager.similar_member_name()