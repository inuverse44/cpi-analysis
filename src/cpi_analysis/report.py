"""O-07 REPORT.md を作る（docs/analysis-plan.md §5）。

数値は毎回データから埋める。文章は NARRATIVE_AS_OF 時点のデータを見て書いたもので、
新しい月のデータを取り込んだときは、注意書きを出して文章の見直しを促す。
"""

import pandas as pd

from .figures import FIGURES
from .sources import ATTRIBUTION, ROOT, SERIES

NARRATIVE_AS_OF = "2026-08"


def _picture(file: str, alt: str) -> str:
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="figures/{file}-dark.png">\n'
        f'  <img src="figures/{file}-light.png" alt="{alt}" width="100%">\n'
        "</picture>"
    )


def _row(summary: pd.DataFrame, code: str) -> pd.Series:
    return summary.set_index("code").loc[code]


def _ym(period: str) -> str:
    year, month = period.split("-")
    return f"{year}年{int(month)}月"


def render(summary: pd.DataFrame) -> str:
    all_items, energy, food, rice = (_row(summary, c) for c in ("0001", "0167", "0002", "0004"))
    onigiri, sushi, bento = (_row(summary, c) for c in ("1793", "1795", "1791"))
    latest = all_items["latest_month"]
    fig = {f.id: f for f in FIGURES}

    stale = ""
    if latest != NARRATIVE_AS_OF:
        stale = (
            f"> [!NOTE]\n> 文章は {_ym(NARRATIVE_AS_OF)}分までのデータを見て書いたものです。"
            f"図と表は {_ym(latest)}分まで更新されています。\n\n"
        )

    rice_from_peak = (rice["latest_index"] / rice["index_peak"] - 1) * 100
    onigiri_from_peak = (onigiri["latest_index"] / onigiri["index_peak"] - 1) * 100

    table_rows = "\n".join(
        f"| {s.label} | {_row(summary, s.code)['latest_index']:.1f} | "
        f"{_row(summary, s.code)['latest_yoy_pct']:+.1f}% | "
        f"{_ym(_row(summary, s.code)['index_peak_month'])}（{_row(summary, s.code)['index_peak']:.1f}） |"
        for s in SERIES
    )

    return f"""# 消費者物価指数で見る、この数年の物価とお米

{stale}2020 年から {_ym(latest)}までの消費者物価指数（全国、2020 年平均＝100）から、物価全体の動きと、お米の値段の動きをまとめました。
分析の進め方は [分析計画書](docs/analysis-plan.md) に、計算はすべて [src/](src/) にあります。

## 要点

- 物価全体（総合）は {_ym(latest)}に **{all_items["latest_index"]:.1f}** で、2020 年より **{all_items["latest_index"] - 100:.1f}%** 高くなっています。
- 上がるペースが最も速かったのは {_ym(all_items["yoy_peak_month"])}で、前年同月比 **{all_items["yoy_peak_pct"]:+.1f}%** でした。直近（{_ym(latest)}）は {all_items["latest_yoy_pct"]:+.1f}% です。
- お米（米類）は {_ym(rice["index_peak_month"])}に **{rice["index_peak"]:.1f}**（2020 年の約 {rice["index_peak"] / 100:.1f} 倍）まで上がりました。{_ym(latest)}は {rice["latest_index"]:.1f} で、山から {abs(rice_from_peak):.0f}% 下がっています。
- おにぎりは {_ym(latest)}に {onigiri["latest_index"]:.1f} で、山（{_ym(onigiri["index_peak_month"])}、{onigiri["index_peak"]:.1f}）からの下がり幅は {abs(onigiri_from_peak):.1f}% にとどまっています。

## Q-01 物価は、2020 年からどれくらい、いつごろ上がったか

{_picture(fig["O-01"].file, fig["O-01"].title)}

- 2021 年までは、ほぼ横ばいでした。2022 年から、総合・生鮮食品を除く総合・生鮮食品及びエネルギーを除く総合の 3 つがそろって上がり続けています。
- エネルギーは動きが大きく、{_ym(energy["index_peak_month"])}に {energy["index_peak"]:.1f} まで上がったあと、上下を繰り返しています（{_ym(latest)}は {energy["latest_index"]:.1f}）。

{_picture(fig["O-02"].file, fig["O-02"].title)}

- 前年同月比で見ると、上がるペースには 2 つの山があります。総合の最大は {_ym(all_items["yoy_peak_month"])}の {all_items["yoy_peak_pct"]:+.1f}% です。
- 生鮮食品及びエネルギーを除く総合は、少し遅れて山を迎えています。エネルギーの値上がりが、ほかの品目に時間をかけて広がったように見えます（ここでは因果関係までは検証していません）。

## Q-02 お米の値段は、どう動いたか

{_picture(fig["O-03"].file, fig["O-03"].title)}

- 米類は 2023 年ごろまで 2020 年より低い水準でしたが、2024 年から急に上がり、{_ym(rice["index_peak_month"])}に {rice["index_peak"]:.1f} になりました。上がるペースの最大は {_ym(rice["yoy_peak_month"])}の前年同月比 {rice["yoy_peak_pct"]:+.1f}%（1 年で約 2 倍）です。
- 同じ期間の食料全体は {food["latest_index"]:.1f}、総合は {all_items["latest_index"]:.1f} なので、お米の動きが際立っています。

{_picture(fig["O-04"].file, fig["O-04"].title)}

- お米を使った食品も上がりましたが、上がり方はお米より小さく、おにぎり {onigiri["latest_index"]:.1f}、すし（弁当）A {sushi["latest_index"]:.1f}、弁当 A {bento["latest_index"]:.1f} です（{_ym(latest)}）。
- お米が山から下がり始めたあとも、おにぎりや弁当はほとんど下がっていません。材料の値段が下がっても、商品の値段はすぐには戻らないようです（理由までは、このデータからはわかりません）。

## 表：系列ごとの最新値と山

| 系列 | 指数（{_ym(latest)}） | 前年同月比 | 指数の山 |
| --- | --- | --- | --- |
{table_rows}

すべての月の値は [data/processed/cpi_selected.csv](data/processed/cpi_selected.csv)、年平均などは [data/processed/summary.csv](data/processed/summary.csv) にあります。

## 検証

計算が正しいことを、テストで確かめています（[分析計画書 §6](docs/analysis-plan.md#6-検証)）。

- 2020 年の各系列の年平均が 100 になること
- 2025 年平均の総合が、総務省統計局の公表値 111.9 と一致すること
- 元データが、取得したときのものから変わっていないこと（SHA-256）

## 再現の手順

```sh
uv sync
uv run cpi-analysis     # 検証 → 集計 → 図と表 → このレポート
uv run pytest
```

---

{ATTRIBUTION}
"""


def write(summary: pd.DataFrame) -> None:
    (ROOT / "REPORT.md").write_text(render(summary), encoding="utf-8")
