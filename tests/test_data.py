"""V-01〜V-04：実データの検証（docs/analysis-plan.md §6）"""

import pandas as pd
import pytest

from cpi_analysis.load import DataValidationError, _check_months, load
from cpi_analysis.measures import annual_mean
from cpi_analysis.sources import SERIES


@pytest.fixture(scope="module")
def index() -> pd.DataFrame:
    return load().index


def test_v03_sha256_matches_record():
    load(verify_sha256=True)  # 一致しなければ DataValidationError


def test_v04_all_series_present_and_months_continuous(index):
    assert list(index.columns) == [s.code for s in SERIES]
    assert index.index.min() == pd.Period("2020-01", "M")
    assert not index.index.has_duplicates


def test_v04_detects_gaps_and_duplicates():
    with pytest.raises(DataValidationError):
        _check_months(pd.PeriodIndex(["2020-01", "2020-03"], freq="M"))
    with pytest.raises(DataValidationError):
        _check_months(pd.PeriodIndex(["2020-01", "2020-01"], freq="M"))


def test_v01_base_year_average_is_100(index):
    base = annual_mean(index).loc[2020]
    assert ((base - 100).abs() <= 0.05).all(), base[(base - 100).abs() > 0.05]


def test_v02_2025_all_items_matches_published_value(index):
    # 総務省統計局の公表値：2025 年平均 総合 111.9（2020 年＝100）
    assert round(annual_mean(index).loc[2025, "0001"], 1) == 111.9
