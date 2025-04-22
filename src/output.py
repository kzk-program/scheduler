from .manager import Band, MemberBandManager
import matplotlib.pyplot as plt
import csv
import pandas as pd
from typing import List


def num_bands_per_member(mb_manager: MemberBandManager) -> None:
    num_bands = [len(member.bands) for member in mb_manager.members]
    plt.hist(num_bands, bins=range(1, max(num_bands) + 1))
    plt.xlabel("#bands")
    plt.ylabel("#members")
    plt.show()
    plt.savefig("num_bands_per_member.png")


def gap_between_bands(
    output_png: str, mb_manager: MemberBandManager, sorted_bands: List[Band]
) -> None:
    gaps = []
    for member in mb_manager.members:
        band_schedules_id = sorted([sorted_bands.index(band) for band in member.bands])
        for i in range(len(band_schedules_id) - 1):
            gaps.append(band_schedules_id[i + 1] - band_schedules_id[i] - 1)
    print(gaps)
    plt.hist(gaps, bins=range(1, max(gaps) + 1))
    plt.xlabel("gap")
    plt.ylabel("#members")
    plt.savefig(output_png)


def output_schedule(
    output_csv: str, mb_manager: MemberBandManager, sorted_bands: List[Band]
) -> None:
    """組んだタイスケをCSVに出力する

    Args:
        output_csv (str): 出力先のCSVファイルへのパス
        mb_manager (MemberBandManager): メンバー、バンド、スケジュールの情報を持つクラス
        sorted_bands (List[Band]): スケジュール順に並べ替えられたバンドのリスト
    """
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["時刻"] + list(mb_manager.bands[0].info.keys()))
        for i, schedule in enumerate(mb_manager.schedules):
            if sorted_bands[i] is None:
                writer.writerow([schedule.name] + ["休み"])
                continue
            writer.writerow(
                [schedule.name]
                + [
                    "" if pd.isna(item) else item
                    for item in sorted_bands[i].info.values
                ]
            )


def output_members_schedule(
    output_csv: str, mb_manager: MemberBandManager, sorted_bands: List[int]
) -> None:
    """組んだタイスケのメンバーごとの出番表をCSVに出力する

    Args:
        output_csv (str): 出力先のCSVファイルへのパス
        mb_manager (MemberBandManager): メンバー、バンド、スケジュールの情報を持つクラス
        sorted_bands (List[int]): スケジュール順に並べ替えられたバンドのリスト
    """
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([""] + [schedule.name for schedule in mb_manager.schedules])
        writer.writerow([""] + [band.name if band else "休み" for band in sorted_bands])
        for member in mb_manager.members:
            bands_id = [band.id for band in member.bands]
            row = [member.name]
            for band_id in [band.id if band else None for band in sorted_bands]:
                if band_id in bands_id:
                    row.append("〇")
                else:
                    row.append("")
            # 一番最後に登場する〇を◎にする
            for i in range(len(row) - 1, 0, -1):
                if row[i] == "〇":
                    row[i] = "◎"
                    break
            writer.writerow(row)
