"""V-06：加工済みデータと要約が、コードから毎回同じものとして作り直せる（docs/analysis-plan.md §6）"""

import io

from cpi_analysis.load import load
from cpi_analysis.report import render
from cpi_analysis.sources import PROCESSED_DIR, ROOT
from cpi_analysis.summary import summarize, tidy


def as_csv(frame) -> str:
    buffer = io.StringIO()
    frame.to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue()


def test_v06_committed_outputs_match_regenerated():
    index = load().index
    summary = summarize(index)
    assert as_csv(tidy(index)) == (PROCESSED_DIR / "cpi_selected.csv").read_text(encoding="utf-8")
    assert as_csv(summary) == (PROCESSED_DIR / "summary.csv").read_text(encoding="utf-8")
    assert render(summary) == (ROOT / "REPORT.md").read_text(encoding="utf-8")


def test_v06_regeneration_is_deterministic():
    index = load().index
    assert as_csv(summarize(index)) == as_csv(summarize(index))
