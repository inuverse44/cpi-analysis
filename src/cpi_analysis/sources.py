"""データの出所と、分析で使う系列の定義（docs/analysis-plan.md §3：D-01、S-01〜S-10）。"""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "figures"

# D-01 消費者物価指数 全国 中分類・品目別 月次（2020 年基準）
SOURCE_URL = "https://www.stat.go.jp/data/cpi/2020/csv/zmi2020aa.csv"
SOURCE_PAGE = "https://www.stat.go.jp/data/cpi/1.html"
RAW_FILE = RAW_DIR / "zmi2020aa.csv"
SOURCES_MD = RAW_DIR / "SOURCES.md"
ATTRIBUTION = f"出典：「消費者物価指数」（総務省統計局）（{SOURCE_PAGE}）を加工して作成"


@dataclass(frozen=True)
class Series:
    id: str
    code: str
    label: str
    short: str = ""  # 図の線の端に出す短い名前（省略時は label）


# 系列は名前ではなく類・品目符号で指定する（同じ名前が別の分類表にも現れるため）
SERIES: tuple[Series, ...] = (
    Series("S-01", "0001", "総合"),
    Series("S-02", "0161", "生鮮食品を除く総合", "生鮮食品を除く"),
    Series("S-03", "0178", "生鮮食品及びエネルギーを除く総合", "生鮮食品・エネルギーを除く"),
    Series("S-04", "0167", "エネルギー"),
    Series("S-05", "0002", "食料"),
    Series("S-06", "0004", "米類"),
    Series("S-07", "1001", "うるち米A"),
    Series("S-07", "1002", "うるち米B"),
    Series("S-08", "1793", "おにぎり"),
    Series("S-09", "1791", "弁当A"),
    Series("S-09", "1797", "弁当B"),
    Series("S-10", "1795", "すし（弁当）A"),
    Series("S-10", "1798", "すし（弁当）B"),
)

CODE_TO_LABEL = {s.code: s.label for s in SERIES}
CODE_TO_SHORT = {s.code: s.short or s.label for s in SERIES}
