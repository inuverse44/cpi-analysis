"""O-05 要約表と O-06 加工済みデータ（docs/analysis-plan.md §5）。"""

import pandas as pd

from .measures import annual_mean, peak, year_over_year
from .sources import PROCESSED_DIR, SERIES


def tidy(index: pd.DataFrame) -> pd.DataFrame:
    """O-06：月 × 系列の縦長データ（指数と前年同月比）"""
    yoy = year_over_year(index)
    rows = []
    for s in SERIES:
        for month, value in index[s.code].items():
            rows.append(
                {
                    "month": str(month),
                    "series_id": s.id,
                    "code": s.code,
                    "label": s.label,
                    "index": value,
                    "yoy_pct": yoy.at[month, s.code],
                }
            )
    out = pd.DataFrame(rows)
    out["index"] = out["index"].round(3)
    out["yoy_pct"] = out["yoy_pct"].round(3)
    return out


def summarize(index: pd.DataFrame) -> pd.DataFrame:
    """O-05：系列ごとの最新値、山、年平均"""
    yoy = year_over_year(index)
    means = annual_mean(index)
    rows = []
    for s in SERIES:
        latest_month = index[s.code].dropna().index[-1]
        index_peak_month, index_peak = peak(index[s.code])
        yoy_peak_month, yoy_peak = peak(yoy[s.code])
        row = {
            "series_id": s.id,
            "code": s.code,
            "label": s.label,
            "latest_month": str(latest_month),
            "latest_index": index.at[latest_month, s.code],
            "latest_yoy_pct": yoy.at[latest_month, s.code],
            "index_peak_month": str(index_peak_month),
            "index_peak": index_peak,
            "yoy_peak_month": str(yoy_peak_month),
            "yoy_peak_pct": yoy_peak,
        }
        for year in means.index:
            row[f"mean_{year}"] = means.at[year, s.code]
        rows.append(row)
    out = pd.DataFrame(rows)
    numeric = out.select_dtypes("number").columns
    out[numeric] = out[numeric].round(3)
    return out


def write(index: pd.DataFrame) -> dict[str, pd.DataFrame]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    frames = {"cpi_selected.csv": tidy(index), "summary.csv": summarize(index)}
    for name, frame in frames.items():
        frame.to_csv(PROCESSED_DIR / name, index=False, encoding="utf-8", lineterminator="\n")
    return frames
