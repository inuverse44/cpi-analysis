"""手法（docs/analysis-plan.md §4：M-01〜M-04）。"""

import pandas as pd


def year_over_year(index: pd.DataFrame) -> pd.DataFrame:
    """M-02 前年同月比（%）。最初の 12 か月は前年がないので NaN"""
    return (index / index.shift(12) - 1) * 100


def annual_mean(index: pd.DataFrame) -> pd.DataFrame:
    """M-03 暦年の単純平均。12 か月そろわない年は出さない"""
    grouped = index.groupby(index.index.year)
    means = grouped.mean()
    complete = grouped.count() == 12
    return means.where(complete).dropna(how="all")


def peak(series: pd.Series) -> tuple[pd.Period, float]:
    """M-04 値が最も大きい月とその値"""
    s = series.dropna()
    month = s.idxmax()
    return month, float(s.loc[month])
