"""成果物の図（docs/analysis-plan.md §5：O-01〜O-04）。

dataviz の決まりに従う：検証済みの配色を固定の順で使う（4 色まで）、線は 2px、
補助線は細い実線、2 系列以上は凡例＋線の端のラベル、文字はデータの色を使わない。
ライト用とダーク用の画像を両方作る（ダークは同じ色相を暗い面向けに調整した値）。
"""

from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .sources import ATTRIBUTION, CODE_TO_LABEL, CODE_TO_SHORT, FIGURES_DIR  # noqa: E402

FONT_CANDIDATES = ["Hiragino Sans", "Noto Sans CJK JP", "BIZ UDGothic", "YuGothic"]


@dataclass(frozen=True)
class Theme:
    name: str
    surface: str
    ink: str
    ink_secondary: str
    muted: str
    grid: str
    baseline: str
    series: tuple[str, ...]


# validate_palette.js で 4 色とも検証済み（ライトは 2 色が 3:1 未満 → 線の端のラベルと表で補う）
LIGHT = Theme(
    "light", "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
)
DARK = Theme(
    "dark", "#1a1a19", "#f0efec", "#c3c2b7", "#898781", "#2c2c2a", "#383835", ("#3987e5", "#d95926", "#199e70", "#c98500")
)


@dataclass(frozen=True)
class Figure:
    id: str
    file: str
    title: str
    ylabel: str
    codes: tuple[str, ...]
    baseline: float


FIGURES = (
    Figure("O-01", "o01-overall-index", "物価の推移（2020年平均＝100）", "指数", ("0001", "0161", "0178", "0167"), 100),
    Figure("O-02", "o02-overall-yoy", "物価が上がるペース（前年同月比）", "前年同月比（%）", ("0001", "0161", "0178"), 0),
    Figure("O-03", "o03-rice-index", "お米の値段（2020年平均＝100）", "指数", ("0004", "0002", "0001"), 100),
    Figure(
        "O-04", "o04-rice-foods-index", "お米を使った食品の値段（2020年平均＝100）", "指数", ("0004", "1793", "1795", "1791"), 100
    ),
)


def _font() -> str:
    from matplotlib import font_manager

    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in FONT_CANDIDATES:
        if name in available:
            return name
    raise RuntimeError(f"日本語フォントが見つかりません：{FONT_CANDIDATES}")


def _end_label_positions(values: list[float], min_gap: float) -> list[float]:
    """線の端のラベルが重ならないよう、縦の位置を最小の間隔だけ離す（順序は保つ）"""
    order = sorted(range(len(values)), key=lambda i: values[i])
    placed = [0.0] * len(values)
    last = None
    for i in order:
        y = values[i] if last is None else max(values[i], last + min_gap)
        placed[i] = y
        last = y
    # 上にずれた分を全体で半分戻し、元の位置からの離れ方を小さくする
    shift = (sum(placed) - sum(values)) / len(values) / 2
    return [p - shift for p in placed]


def draw(fig_spec: Figure, data: pd.DataFrame, theme: Theme):
    plt.rcParams["font.family"] = _font()
    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=150)
    fig.patch.set_facecolor(theme.surface)
    ax.set_facecolor(theme.surface)

    x = data.index.to_timestamp()
    ends = []
    for color, code in zip(theme.series, fig_spec.codes, strict=False):
        s = data[code]
        ax.plot(x, s, color=color, linewidth=2, solid_capstyle="round", solid_joinstyle="round", label=CODE_TO_LABEL[code])
        last = s.dropna()
        ends.append((last.index[-1].to_timestamp(), float(last.iloc[-1]), color, CODE_TO_SHORT[code]))

    ax.axhline(fig_spec.baseline, color=theme.baseline, linewidth=1)
    ax.grid(axis="y", color=theme.grid, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(theme.baseline)
    ax.tick_params(colors=theme.muted, labelsize=10, length=0)
    ax.set_ylabel(fig_spec.ylabel, color=theme.ink_secondary, fontsize=10)

    # 線の端のラベル：小さな色の点＋文字用の色の文字。近い場合は離して細い引き出し線でつなぐ
    lo, hi = ax.get_ylim()
    positions = _end_label_positions([e[1] for e in ends], (hi - lo) * 0.055)
    x_label = x[-1] + pd.Timedelta(days=45)
    for (xe, ye, color, label), yl in zip(ends, positions, strict=True):
        ax.plot([xe], [ye], marker="o", markersize=5, color=color, markeredgecolor=theme.surface, markeredgewidth=1.5)
        if abs(yl - ye) > (hi - lo) * 0.01:
            ax.plot([xe, x_label], [ye, yl], color=theme.muted, linewidth=0.8)
        ax.annotate(
            f"{label}  {ye:.1f}",
            (x_label, yl),
            xytext=(4, 0),
            textcoords="offset points",
            va="center",
            fontsize=10,
            color=theme.ink_secondary,
            annotation_clip=False,
        )
    ax.set_xlim(x[0], x[-1] + pd.Timedelta(days=30))

    ax.set_title(fig_spec.title, loc="left", color=theme.ink, fontsize=15, fontweight="bold", pad=34)
    legend = ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncol=len(fig_spec.codes),
        frameon=False,
        fontsize=10,
        handlelength=1.6,
        borderaxespad=0.3,
    )
    for text in legend.get_texts():
        text.set_color(theme.ink_secondary)
    fig.text(0.01, 0.01, ATTRIBUTION, fontsize=7.5, color=theme.muted, ha="left", va="bottom")
    fig.subplots_adjust(left=0.08, right=0.72, top=0.84, bottom=0.12)
    return fig


def render_all(index: pd.DataFrame, yoy: pd.DataFrame) -> list[str]:
    """O-01〜O-04 をライト用・ダーク用の PNG で書き出す。書き出したファイル名を返す"""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for spec in FIGURES:
        source = yoy if spec.id == "O-02" else index
        data = source.loc[:, list(spec.codes)]
        if spec.id == "O-02":
            data = data.dropna(how="all")
        for theme in (LIGHT, DARK):
            fig = draw(spec, data, theme)
            name = f"{spec.file}-{theme.name}.png"
            fig.savefig(FIGURES_DIR / name, facecolor=theme.surface, metadata={"Software": None})
            plt.close(fig)
            written.append(name)
    return written
