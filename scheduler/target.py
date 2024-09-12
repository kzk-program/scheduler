import pulp
import typing
import itertools
from manager import MemberBandManager
from enum import Enum

class Target(Enum):
    MAXIMIZE_BAND_GAP = 1
    EARLY_FINISH = 2


def maxmize_band_gap(mb_manager: MemberBandManager, prob: pulp.LpProblem, choices: dict) -> None:
    # TODO
    penalties = []
    for member in mb_manager.members:
        penalties += [3*choices[mb_manager.schedules[i+j], band] for j in range(3) for i in range(len(mb_manager.schedules) - 2) for band in member.bands] + [choices[mb_manager.schedules[i+j], band] for j in range(4) for i in range(len(mb_manager.schedules) - 3) for band in member.bands]
    prob += pulp.lpSum(penalties)

def early_finish(mb_manager: MemberBandManager, prob: pulp.LpProblem, choices: dict) -> None:
    """これはエラーを吐くので使えない"""
    finish_ids = []
    for member in mb_manager.members:
        finish_id = 0
        for i, schedule in enumerate(mb_manager.schedules):
            temp = i*pulp.lpSum([choices[schedule, band] for band in member.bands])
            for j in range(i+1, len(mb_manager.schedules)):
                for band in member.bands:
                    # if else を 乗算に変換
                    # 非線形最適化になるからPulpは使えない
                    temp *= (1 - choices[mb_manager.schedules[j], band])
            finish_id += temp
        finish_ids.append(finish_id)
    prob += pulp.lpSum(finish_ids)