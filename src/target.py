import pulp
from .manager import MemberBandManager
from enum import Enum


class Target(Enum):
    MAXIMIZE_BAND_GAP = 1
    EARLY_FINISH = 2


def maxmize_band_gap(
    mb_manager: MemberBandManager, prob: pulp.LpProblem, choices: dict
) -> None:
    """バンドの出演間隔を最大化する目的関数
    """
    penalties = []
    for member in mb_manager.members:
        for gap in range(len(mb_manager.schedules) - 2): # 全スケジュール合計で2バンド以上あるのはどうしようもないのでペナルティに入れず、gap == len(schedules) - 2は除外する
            for start_idx in range(len(mb_manager.schedules) - gap - 1): #gap=0, start_idx=0なら、schedule_id=0と1にその人が所属するバンドが2バンドあるとペナルティがつく
                v = pulp.LpVariable(
                    f"{member.name}_{gap}_{start_idx}",
                    cat=pulp.LpBinary,
                )
                prob += v >= pulp.lpSum(
                    choices[mb_manager.schedules[start_idx + i], band]
                    for i in range(gap + 2)
                    for band in member.bands
                ) - 1
                penalties.append(v)
    prob += pulp.lpSum(penalties)  # 目的関数を追加



def early_finish(
    mb_manager: MemberBandManager, prob: pulp.LpProblem, choices: dict
) -> None:
    """これはエラーを吐くので使えない"""
    finish_ids = []
    for member in mb_manager.members:
        finish_id = 0
        for i, schedule in enumerate(mb_manager.schedules):
            temp = i * pulp.lpSum([choices[schedule, band] for band in member.bands])
            for j in range(i + 1, len(mb_manager.schedules)):
                for band in member.bands:
                    # if else を 乗算に変換
                    # 非線形最適化になるからPulpは使えない
                    temp *= 1 - choices[mb_manager.schedules[j], band]
            finish_id += temp
        finish_ids.append(finish_id)
    prob += pulp.lpSum(finish_ids)
