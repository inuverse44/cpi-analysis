"""D-01 の読み込みと、データの形の検証（V-03、V-04）。"""

from dataclasses import dataclass

import pandas as pd

from .fetch import sha256_of
from .sources import RAW_FILE, SERIES, SOURCES_MD

HEADER_ROWS = 6  # 名前、英語名、符号、連番、ウエイト、ウエイト 1 万分比
CODE_ROW = 2


class DataValidationError(Exception):
    pass


@dataclass(frozen=True)
class CpiData:
    """月次の指数（行：月、列：類・品目符号）"""

    index: pd.DataFrame


def recorded_sha256() -> str:
    """SOURCES.md に記録した SHA-256（V-03）"""
    for line in SOURCES_MD.read_text(encoding="utf-8").splitlines():
        if RAW_FILE.name in line:
            return line.rsplit("`", 2)[-2]
    raise DataValidationError(f"{SOURCES_MD} に {RAW_FILE.name} の記録がありません")


def load(path=RAW_FILE, verify_sha256: bool = True) -> CpiData:
    if verify_sha256:
        actual, expected = sha256_of(path), recorded_sha256()
        if actual != expected:  # V-03
            raise DataValidationError(f"SHA-256 が記録と一致しません：{actual} != {expected}")

    raw = pd.read_csv(path, encoding="cp932", header=None, dtype=str, keep_default_na=False)
    codes = raw.iloc[CODE_ROW, 1:].str.strip().tolist()
    body = raw.iloc[HEADER_ROWS:, :].copy()
    months = pd.PeriodIndex(body.iloc[:, 0].str.strip(), freq="M")
    values = body.iloc[:, 1:].apply(lambda col: pd.to_numeric(col.str.strip().replace("", None), errors="raise"))
    values.index = months
    values.index.name = "month"

    # 同じ符号が複数の分類表に現れることがある。最初に現れた列を使う（符号で一意に指定する）
    values.columns = codes
    values = values.loc[:, ~pd.Index(codes).duplicated()]

    wanted = [s.code for s in SERIES]
    missing = [c for c in wanted if c not in values.columns]
    if missing:  # V-04
        raise DataValidationError(f"使う系列の符号がありません：{missing}")
    _check_months(values.index)
    return CpiData(index=values[wanted].astype(float))


def _check_months(months: pd.PeriodIndex) -> None:
    """V-04：月が重複せず、欠けなく連続している"""
    if months.has_duplicates:
        raise DataValidationError("同じ月が重複しています")
    expected = pd.period_range(months.min(), months.max(), freq="M")
    if len(expected) != len(months) or not (months == expected).all():
        raise DataValidationError("月が連続していません")
