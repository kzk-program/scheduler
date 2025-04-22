import pulp
import itertools
from .manager import MemberBandManager, Member
from typing import Dict, Callable
from enum import Enum

"""タイスケの制約条件を定義するモジュール

TODO:どうせEnumにするくらいなら、制約条件の関数たちをクラスにまとめた方がいいかもしれない
"""


class Constraint(Enum):
    """制約条件のEnumクラス"""

    ONE_BAND_PER_SCHEDULE = 1
    ONE_POSSIBLE_SCHEDULE_PER_BAND = 2
    CLOSE_SCHEDULE = 3


class Constraints:
    """制約条件を格納するクラス"""

    def __init__(self):
        self.constraints: Dict[Constraint] = dict()

    def add(self, constraint: Constraint, value: dict):
        self.constraints[constraint] = value


def one_band_per_schedule(
    mb_manager: MemberBandManager, prob: pulp.LpProblem, choices: dict
) -> None:
    """1つのスケジュールに入れるバンドは1つだけにする制約条件を追加する

    Args:
        mb_manager (MemberBandManager): メンバー、バンド、スケジュールの情報を持つクラス
        prob (pulp.LpProblem): pulpの最適化問題
        choices (dict): pulpの変数
    """
    for schedule in mb_manager.schedules:
        prob += pulp.lpSum([choices[schedule, band] for band in mb_manager.bands]) == 1


def one_possible_schedule_per_band(
    mb_manager: MemberBandManager, prob: pulp.LpProblem, choices: dict
) -> None:
    """バンドが出演可能なスケジュールの中で1つだけに出演する制約条件を追加する

    Args:
        mb_manager (MemberBandManager): メンバー、バンド、スケジュールの情報を持つクラス
        prob (pulp.LpProblem): pulpの最適化問題
        choices (dict): pulpの変数
    """
    for band in mb_manager.bands:
        prob += (
            pulp.lpSum(
                [
                    choices[possible_schedule, band]
                    for possible_schedule in band.possible_schedule
                ]
            )
            == 1
        )
        for schedule in mb_manager.schedules:
            if schedule not in band.possible_schedule:
                prob += choices[schedule, band] == 0


def close_schedule(
    gap: int,
    mb_manager: MemberBandManager,
    prob: pulp.LpProblem,
    choices: dict,
    target_member_condition: Callable[[Member], bool] = (lambda member: True),
) -> None:
    """同じメンバーのいるバンド同士は、スケジュールの間隔がgap以下にならないようにする制約条件を追加する

    Args:
        gap (int): スケジュールの間隔
        mb_manager (MemberBandManager): メンバー、バンド、スケジュールの情報を持つクラス
        prob (pulp.LpProblem): pulpの最適化問題
        choices (dict): pulpの変数
        target_member_condition (_type_, optional): 対象になるメンバーの条件 Defaults to (lambda member: True).
    """
    # for band1, band2 in itertools.combinations(mb_manager.bands, 2):
    #     contain_same_target_member = False
    #     for member in mb_manager.same_member(band1, band2):
    #         if target_member_condition(member):
    #             contain_same_target_member = True
    #             break
    #     if contain_same_target_member:
    #         for i in range(len(mb_manager.schedules) - gap):
    #             prob += (
    #                 pulp.lpSum(
    #                     [
    #                         choices[mb_manager.schedules[i + j], band1]
    #                         for j in range(gap + 1)
    #                     ] + [
    #                         choices[mb_manager.schedules[i + j], band2]
    #                         for j in range(gap + 1)
    #                     ]
    #                 )
    #                 <= 1
    #             )

    for member in mb_manager.members:
        if target_member_condition(member):
            for start_idx in range(len(mb_manager.schedules) - gap):
                prob += (
                    pulp.lpSum(
                        [
                            choices[mb_manager.schedules[start_idx + j], band]
                            for j in range(gap + 1)
                            for band in member.bands
                        ]
                    )
                    <= 1
                )