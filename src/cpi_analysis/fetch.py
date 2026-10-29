"""新しい月のデータを取り込む（docs/analysis-plan.md §7）。V-03 のための SHA-256 を記録する。"""

import hashlib
import urllib.request
from datetime import date

from .sources import RAW_FILE, SOURCE_URL, SOURCES_MD


def sha256_of(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(today: date | None = None) -> str:
    """D-01 をダウンロードして data/raw/ に保存し、SOURCES.md を書き換える。保存したファイルの SHA-256 を返す。"""
    today = today or date.today()
    with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:  # 取得元は固定の https URL
        body = response.read()
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_bytes(body)
    digest = sha256_of(RAW_FILE)
    SOURCES_MD.write_text(
        "# 元データの記録（D-01、V-03）\n\n"
        "| ファイル | 取得元 | 取得日 | SHA-256 |\n"
        "| --- | --- | --- | --- |\n"
        f"| `{RAW_FILE.name}` | {SOURCE_URL} | {today.isoformat()} | `{digest}` |\n\n"
        "文字コードは Shift_JIS（CP932）。統計局が配布したままの形で保存している。\n",
        encoding="utf-8",
    )
    return digest
