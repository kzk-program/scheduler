from typing import List, Tuple
import pandas as pd
import Levenshtein
import itertools


class Member:
    """メンバーのクラス
    id: メンバーのID (MemberBandManagerのmembersのインデックス)
    name: メンバーの名前 (一意であることが前提 (期+本名を想定))
    bands: メンバーが所属しているバンドのリスト
    """

    def __init__(self, id: int, name: str) -> None:
        self.id: int = id
        self.name: str = name
        self.bands: List[Band] = []


class Schedule:
    """スケジュールのクラス
    id: スケジュールのID (MemberBandManagerのschedulesのインデックス)
    name: スケジュールの名前 (例: 20:00-23:00 2)
    """

    def __init__(self, id: int, name: str) -> None:
        self.id: int = id
        self.name: str = name


class Band:
    """バンドのクラス
    id: バンドのID (MemberBandManagerのbandsのインデックス)
    name: バンドの名前
    members: バンドに所属しているメンバーのリスト
    possible_schedule: バンドが出演可能なスケジュールのリスト
    info: バンドの情報 (出力CSVに表示したい情報)
    """

    def __init__(
        self,
        id: int,
        name: str,
        members: List[Member],
        possible_schedule: List[Schedule],
        info: pd.Series,
    ) -> None:
        self.id: int = id
        self.name: str = name
        self.members: List[Member] = members
        self.possible_schedule: List[Schedule] = possible_schedule
        self.info: pd.Series = info


class MemberBandManager:
    def __init__(self):
        # membersとbandsは、idと配列のインデックスが一致する必要がある
        self.members: List[Member] = []
        self.bands: List[Band] = []
        self.schedules: List[Schedule] = []

    def get_band(self, id: int) -> Band:
        return self.bands[id]

    def is_valid_member_name(self, name: str) -> bool:
        for member in self.members:
            if member.name == name:
                return True
        return False

    def get_valid_member(self, name: str) -> Member:
        for member in self.members:
            if member.name == name:
                return member

    def add_member(self, name: str) -> Member:
        id = len(self.members)
        member = Member(id, name)
        self.members.append(member)
        return member

    def get_member(self, name: str) -> Member:
        if self.is_valid_member_name(name):
            return self.get_valid_member(name)
        else:
            return self.add_member(name)

    def set_schedule(self, schedules_name: List[str]) -> None:
        for id, schedule_name in enumerate(schedules_name):
            schedule = Schedule(id, schedule_name)
            self.schedules.append(schedule)

    def get_schedule(self, schedule_id: int) -> Schedule:
        return self.schedules[schedule_id]

    def add_band(
        self,
        name: str,
        members_name: List[str],
        possible_schedules_id: List[int],
        info: pd.Series,
    ) -> Band:
        members = [self.get_member(member_name) for member_name in members_name]
        band_id = len(self.bands)
        possible_schedules = [
            self.get_schedule(possible_schedule_id)
            for possible_schedule_id in possible_schedules_id
        ]
        band = Band(band_id, name, members, possible_schedules, info)
        self.bands.append(band)
        for member in members:
            member.bands.append(band)
        return band

    def display(self) -> None:
        # デバッグ用
        print("band id, band name, (member id, member name)")
        for i, band in enumerate(self.bands):
            print(i, ",", band.name, ",", end="")
            for member in band.members:
                print("(", member.name, ",", member.id, ")", end="")
            print("")

        # 2つのバンド間で同じメンバーがいるかチェックする関数

    def contain_same_member(self, band1: Band, band2: Band) -> bool:
        """2つのバンド間で同じメンバーがいるかチェックする"""
        for member1 in band1.members:
            for member2 in band2.members:
                if member1 is member2:
                    return True
        return False

    def same_member(self, band1: Band, band2: Band) -> List[Member]:
        """2つのバンド間の同じメンバーを取得する"""
        same_members = []
        for member1 in band1.members:
            for member2 in band2.members:
                if member1 is member2:
                    same_members.append(member1)
        return same_members

    def similar_member_name(self) -> List[Tuple[str]]:
        """メンバー名が似ているメンバーの組を取得する

        Returns:
            List[Tuple[str]]: 似ているメンバーの組のリスト
        """
        simliar_members = []
        for member1, member2 in itertools.combinations(self.members, 2):
            if Levenshtein.distance(member1.name, member2.name) <= 2:
                simliar_members.append((member1.name, member2.name))
        return simliar_members
