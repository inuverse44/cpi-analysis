"""V-05：手法の定義どおりに計算できる（docs/analysis-plan.md §4、§6）"""

import pandas as pd
import pytest

from cpi_analysis.measures import annual_mean, peak, year_over_year


def frame(values: list[float], start: str = "2020-01") -> pd.DataFrame:
    return pd.DataFrame({"x": values}, index=pd.period_range(start, periods=len(values), freq="M"))


def test_v05_yoy_first_12_months_are_empty():
    yoy = year_over_year(frame([100.0] * 13))
    assert yoy["x"].iloc[:12].isna().all()
    assert yoy["x"].iloc[12] == 0


def test_v05_yoy_matches_hand_calculation():
    values = [100.0] * 12 + [110.0, 95.0]
    yoy = year_over_year(frame(values))["x"]
    assert yoy.iloc[12] == pytest.approx(10.0)
    assert yoy.iloc[13] == pytest.approx(-5.0)


def test_m03_annual_mean_drops_incomplete_years():
    means = annual_mean(frame([100.0] * 12 + [120.0] * 3))["x"]
    assert list(means.index) == [2020]
    assert means.loc[2020] == 100


def test_m04_peak_ignores_missing_values():
    month, value = peak(frame([1.0, float("nan"), 3.0, 2.0])["x"])
    assert (str(month), value) == ("2020-03", 3.0)
