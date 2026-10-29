"""消費者物価指数の集計・可視化（docs/analysis-plan.md）。"""

import sys


def main(argv: list[str] | None = None) -> int:
    """`cpi-analysis`：検証 → 集計 → 図と表 → REPORT.md。`cpi-analysis fetch`：元データを取り込み直す"""
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["fetch"]:
        from .fetch import fetch

        print(f"取得しました（SHA-256：{fetch()}）")
        return 0

    from . import figures, report, summary
    from .load import load
    from .measures import year_over_year

    index = load().index  # V-03、V-04
    frames = summary.write(index)  # O-05、O-06
    written = figures.render_all(index, year_over_year(index))  # O-01〜O-04
    report.write(frames["summary.csv"])  # O-07
    print(f"{index.index.max()} までのデータで、図 {len(written)} 枚・表・REPORT.md を作りました")
    return 0
