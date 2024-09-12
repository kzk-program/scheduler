import pandas as pd
from manager import Member, Band, Schedule, MemberBandManager
from typing import Type, List

def bands_parser(csv_file:str, mb_manager:MemberBandManager, column_band_name: int, columns_possible_schedules: List[int], columns_members: List[int], columns_info: List[int])->None:
    # バンドを並べ替えたい時用　(CL、OLなど)
    df = pd.read_csv(csv_file)

    # スケジュール枠をセットする
    mb_manager.set_schedule(df.columns[columns_possible_schedules])

    #バンドとそのメンバーを追加していく
    for row_index in df.index:
        row = df.loc[row_index]
        possible_schedules_id = []
        for column in columns_possible_schedules:
            if row.iloc[column] == 1:
                possible_schedules_id.append(columns_possible_schedules.index(column))
                info = row.iloc[columns_info]
        mb_manager.add_band(row.iloc[column_band_name], [member_name for member_name in row.iloc[columns_members].values if not pd.isnull(member_name)], possible_schedules_id, info)