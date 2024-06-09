import pulp
import itertools
from managers import MemberBandManager

def one_band_per_schedule(mb_manager: MemberBandManager, prob: pulp.LpProblem, choices:dict) -> None:
    for schedule in mb_manager.schedules:
        prob += pulp.lpSum([choices[schedule, band] for band in mb_manager.bands]) == 1

def one_band_per_possible_schedule(mb_manager: MemberBandManager, prob:pulp.LpProblem, choices:dict) -> None:
    for band in mb_manager.bands:
        prob += pulp.lpSum([choices[possible_schedule, band] for possible_schedule in band.possible_schedule]) == 1
        for schedule in mb_manager.schedules:
            if not schedule in band.possible_schedule:
                prob += choices[schedule, band] == 0

def close_schedule(gap: int, mb_manager: MemberBandManager, prob:pulp.LpProblem, choices:dict, target_member_condition: bool = True) -> None:
    # TODO
    close_schedules = []
    for schedule1, schedule2 in itertools.combinations(mb_manager.schedules, 2):
        if abs(schedule1.id - schedule2.id) <= gap:
            close_schedules.append((schedule1, schedule2))
    for band1, band2 in itertools.combinations(mb_manager.bands, 2):
        if mb_manager.contain_same_member(band1, band2):
            for schedule1, schedule2 in close_schedules:
                prob += pulp.lpSum([choices[schedule1, band1], choices[schedule2, band2]]) <= 1
                prob += pulp.lpSum([choices[schedule1, band2], choices[schedule2, band1]]) <= 1