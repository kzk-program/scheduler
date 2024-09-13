import pandas as pd
from .manager import MemberBandManager
from typing import List


def bands_parser(
    csv_file: str,
    mb_manager: MemberBandManager,
    column_band_name: int,
    columns_possible_schedules: List[int],
    columns_members: List[int],
    columns_info: List[int],
) -> None:
    """CSVファイルを読み込んでバンド情報をmb_managerにセットする

    Args:
        csv_file (str): バンド情報が記載されたCSVファイルへのパス
        mb_manager (MemberBandManager): メンバー、バンド、スケジュールの情報を持つクラス（初期化直後を想定）
        column_band_name (int): バンド名が記載されている列のインデックス
        columns_possible_schedules (List[int]): バンドが出演可能なスケジュールが記載されている列のインデックスのリスト
        columns_members (List[int]): バンドのメンバーが記載されている列のインデックスのリスト
        columns_info (List[int]): バンドの情報 (出力CSVファイルに記載されていてほしい情報) が記載されている列のインデックスのリスト
    """
    df = pd.read_csv(csv_file)

    # スケジュール枠をセットする
    mb_manager.set_schedule(df.columns[columns_possible_schedules])

    # バンドとそのメンバーを追加していく
    for row_index in df.index:
        row = df.loc[row_index]
        possible_schedules_id = []
        for column in columns_possible_schedules:
            if row.iloc[column] == 1:
                possible_schedules_id.append(columns_possible_schedules.index(column))
                info = row.iloc[columns_info]
        mb_manager.add_band(
            row.iloc[column_band_name],
            [
                member_name
                for member_name in row.iloc[columns_members].values
                if not pd.isnull(member_name)
            ],
            possible_schedules_id,
            info,
        )
