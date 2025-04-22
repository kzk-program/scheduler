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
    """なるべく多くの人がなるべく早く終われるようにする
    OLでみんな早く寝れるようにするときに使う
    最後の方が同じ人ばっかりになる可能性があるのに注意
    """
    finish_ids = []
    for member in mb_manager.members:
        finish_id = pulp.LpVariable(
            f"{member.name}_finish_id",
            lowBound=0,
            cat=pulp.LpInteger,
        )
        for i, schedule in enumerate(mb_manager.schedules):
            prob += finish_id >=  i * pulp.lpSum([choices[schedule, band] for band in member.bands])
        finish_ids.append(finish_id)
    prob += pulp.lpSum(finish_ids)
